from django.contrib import admin
from models import Task, Partyfirst, Partysecond


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'univalent', 'note', 'create_time', 'end_time']
    search_fields = ['name', 'create_time']
    save_on_top = True


@admin.register(Partyfirst)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Partysecond)
class TaskAdmin(admin.ModelAdmin):
    pass
