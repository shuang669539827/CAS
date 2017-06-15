from django.contrib import admin
from models import Messages, Counter

# Register your models here.


@admin.register(Messages)
class Msg(admin.ModelAdmin):
    list_display = ['subject', 'description', 'app', 'url', 'sender', 'sent_at', 'deal_at', 'pushtype']
    search_fields = ['sender', 'app']


@admin.register(Counter)
class Msg(admin.ModelAdmin):
    list_display = ['user', 'count']
    search_fields = ['user', 'count']
