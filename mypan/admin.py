from django.contrib import admin

from .models import MaxSize
# Register your models here.


class MaxSizeAdmin(admin.ModelAdmin):
    pass


admin.site.register(MaxSize, MaxSizeAdmin)
