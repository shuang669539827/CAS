from django.contrib import admin
from .models import CheckInOut, Record, CheckTotal


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'inTime', 'outTime', 'allTime']
    search_fields = ['user__first_name']
    list_filter = ['createDate']
    save_on_top = True

    @staticmethod
    def name(self):
        return self.user.first_name


@admin.register(CheckInOut)
class CheckInOutAdmin(admin.ModelAdmin):
    list_display = ['emId', 'checkTime']
    search_fields = ['emId']
    save_on_top = True


@admin.register(CheckTotal)
class CheckInOutAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name']
    save_on_top = True

