from django.db import models
from django.utils import timezone


class EEG(models.Model):
    address = models.CharField(max_length=50)
    name = models.CharField(max_length=15, default='test')
    created_date = models.DateTimeField(
        default=timezone.now)

    def __str__(self):
        return self.name


class Callee(models.Model):
    token = models.CharField(max_length=250)
    name = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name


class Call(models.Model):
    caller = models.ForeignKey(EEG, on_delete=models.CASCADE)
    callee = models.ForeignKey(Callee, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.caller)

    def register(self, cd):
        if cd['callee'] is None or cd['caller'] is None:
            return

        self.callee = cd['callee']
        self.caller = cd['caller']
        self.save()
