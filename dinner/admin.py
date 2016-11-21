from django.contrib import admin
from .models import  Food, Orders



# class TypeAdmin(admin.ModelAdmin):
# 	list_display = ('ch_name',)
# 	list_display_link = ('ch_name')


class FoodAdmin(admin.ModelAdmin):
	list_display = ('name','info')
 	list_display_link = ('name')


class OrdersAdmin(admin.ModelAdmin):
	def first_name(self, instance):
		return str(instance.pro.user.first_name)
	search_fields = ['pro__user__first_name']



#admin.site.register(Type, TypeAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Orders, OrdersAdmin)


