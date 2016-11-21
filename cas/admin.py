#coding:utf8
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import UserRole, ProjectRole, Department, Zone, Project, UserProject, Pro, News, Menu, ApplyPerm
# Register your models here.


@admin.register(UserRole, ProjectRole, Department, Zone, Project, News, Menu, ApplyPerm)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')
    list_filter = ('project__name',)
    def first_name(self, instance):
        return str(instance.user.first_name)
    search_fields = ['user__first_name', 'project__name']

    def name(self, obj):
        return obj.user.first_name


class ProInline(admin.StackedInline):
    model = Pro
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = u'附加信息列表'


class CustomUserAdmin(UserAdmin):
    inlines = (ProInline,)
    list_display = ('username', 'first_name', 'email')
    ordering = ('username',)
    list_filter = ('pro__department__name', 'pro__role__name','pro__zone__name')

    def zone(self, obj):
        return obj.pro.zone.name
    zone.short_description = u'区域'

	
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
