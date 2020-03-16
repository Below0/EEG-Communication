from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from .forms import *
from .models import *
from .fcm import *

# Create your views here.
from pip._vendor.requests import Response


def eeg(request):
    if request.method == 'GET':
        return HttpResponse("return this string(GET)")
    elif request.method == 'POST':
        form = EEGForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            is_exist = EEG.objects.filter(address=cd['address']).count()
            if is_exist < 1:
                print('create new Mindwave Mobile2!')
                EEG.objects.create(address=cd['address'], name=cd['name'])

            data = {
                "status": True
            }
            return JsonResponse(data, json_dumps_params={'ensure_ascii': True})
        else:
            data = {
                "status": False
            }
            return JsonResponse(data, json_dumps_params={'ensure_ascii': True})


def call(request):
    if request.method == 'GET':
        return HttpResponse('None')
    elif request.method == 'POST':
        form = EEGForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            caller = EEG.objects.get(cd['title'])
            call_entry = Call.objects.filter(caller=caller.id)
            return HttpResponse(call_entry[0])
        else:
            return HttpResponse('None')


def do_call(request, mac):
    if request.method == 'GET':
        try:
            eeg_instance = EEG.objects.get(address=mac)
            call_entry = Call.objects.filter(caller=eeg_instance.id)
            token_list = []
            for row in call_entry:
                token_list.append(row.callee.token)
            send_fcm_notification(token_list, str(row.caller), '사용자가 호출하였습니다!')
            return HttpResponse(mac)
        except ObjectDoesNotExist:
            return HttpResponse('None')


def make_call(request, mac, callee_id):
    if request.method == 'GET':
        try:
            caller_obj = EEG.objects.get(address=mac)
            callee_obj = Callee.objects.get(pk=callee_id)
            r, is_exist = Call.objects.get_or_create(caller=caller_obj, callee=callee_obj)
            return HttpResponse(is_exist)
        except ObjectDoesNotExist:
            return HttpResponse('None')


def callee(request):
    if request.method == 'POST':
        form = CalleeForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            is_exist = Callee.objects.filter(token=cd['token'], name=cd['name']).count()
            if is_exist < 1:
                print('create new Android!')
                new_callee = Callee.objects.create(token=cd['token'], name=cd['name'])
            else:
                new_callee = Callee.objects.get(token=cd['token'], name=cd['name'])

            data = {
                'status': True,
                'id': new_callee.id
            }
            return JsonResponse(data, json_dumps_params={'ensure_ascii': True})
        else:
            token = request.POST.get("token", "")
            name = request.POST.get("name", "")
            if token is None or name is None:
                return HttpResponseNotFound("None")
            new_callee = Callee.objects.get(token=token, name=name)
            data = {
                'status': False,
                'id': new_callee.id
            }
            return JsonResponse(data, json_dumps_params={'ensure_ascii': True})
