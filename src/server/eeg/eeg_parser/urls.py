from django.urls import path
from . import views

urlpatterns = [
    path('eeg/', views.eeg, name='eeg'),
    path('callee/', views.callee, name='callee'),
    path('call/', views.call, name='call'),
    path('call/<str:mac>', views.do_call, name='doCall'),
    path('call/<str:mac>/<int:callee_id>', views.make_call, name='makeCall')
]
