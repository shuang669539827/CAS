#coding:utf8
from django import forms
from django.contrib.auth.models import User
from .models import  Apply


class ApplyForm(forms.Form):
	desc = forms.CharField(label=u'申请理由', widget=forms.Textarea)


class VisitForm(forms.Form):
	visitor = forms.CharField(max_length=50, label='客户名称')
	address = forms.CharField(max_length=50, label='地点')
	note = forms.CharField(label=u'备注', widget=forms.Textarea)


class FileForm(forms.Form):
	desc = forms.CharField(label=u'备注', widget=forms.Textarea)
	upfile = forms.FileField(max_length=300, label=u'附件', required=False, widget=forms.FileInput())


class MaterForm(forms.Form):
	matertype = forms.ChoiceField(choices=[(1,'产检假1天'),(15,'陪产假15天'),(128,'产假128天')], label=u'产假类型')
	desc = forms.CharField(label=u'备注', widget=forms.Textarea)
	upfile = forms.FileField(max_length=300, label=u'附件', required=False, widget=forms.FileInput())


		
		
