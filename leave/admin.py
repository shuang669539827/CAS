from django.contrib import admin
from .models import LeaveType, Apply, UserHoliday, MonthApply

# Register your models here.

@admin.register(LeaveType)
class CommentAdmin(admin.ModelAdmin):
	pass


class UserHolidayAdmin(admin.ModelAdmin):
	def first_name(self, instance):
		return str(instance.user.first_name)
	search_fields = ['user__first_name']


class ApplyAdmin(admin.ModelAdmin):
	def first_name(self, instance):
		return str(instance.user.first_name)
	list_filter = ['user', 'apply_date']
	search_fields = ['user__first_name']


class MonthApplyAdmin(admin.ModelAdmin):
	def first_name(self, instance):
		return str(instance.user.first_name)
	list_filter = ['user', 'year_month']
	search_fields = ['user__first_name']


admin.site.register(Apply, ApplyAdmin)
admin.site.register(UserHoliday, UserHolidayAdmin)
admin.site.register(MonthApply, MonthApplyAdmin)