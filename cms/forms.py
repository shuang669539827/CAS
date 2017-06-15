# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import ModelForm

from .models import Task


class TaskForm(ModelForm):
    class Meta:
        model = Task
        exclude = ['workflowactivity', 'create_time', 'end_time']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }