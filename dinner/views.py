#coding:utf8
from django.shortcuts import render, render_to_response, get_object_or_404, render_to_response, RequestContext, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.views.generic import View
from datetime import datetime
from django.core.paginator import Paginator
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse  
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator

from .models import  Food, Orders
from .forms import FoodForm
from cas.models import Pro

import time
import traceback
import logging


# Create your views here.

errlog = logging.getLogger('daserr')

# @login_required
# class IndexView(View):

@login_required
def Index(request):
    pro = request.user.pro
    department = pro.department.name_id
    now = int(time.strftime('%H%M'))
    foods = Food.objects.all()
    return render(request, 'dinner-dinner.html', {"foods": foods, 'pro': pro, 'now': now})


class OrderView(View):

    def get(self, request):
        food_id = request.GET.get('id')
        pro = request.user.pro
        department = pro.department.name_id
        today = time.strftime("%Y-%m-%d")
        order = Orders.objects.filter(pro=pro, create_time=today)
        if food_id:
            if int(time.strftime('%H%M')) > 1530:
                return HttpResponseRedirect('/dinner/') 
            if len(order) > 0:
                foods = Food.objects.all()
                return render(request, 'dinner.html', {'error': '预定失败,你已经定过餐了!','foods': foods, 'pro': pro})
            try:
                food_obj = Food.objects.get(id=food_id) 
            except Food.DoesNotExist:
                return render(request, 'dinner.html', {'error':'预定失败,该商品已下线!', 'pro': per})
            Orders.objects.create(pro=pro,food=food_obj)       
            return HttpResponseRedirect('/dinner/orders/')
        else:
            orders = Orders.objects.filter(create_time=today)
            return render(request, 'dinner-orders.html', {'orders': orders, 'pro': pro})


class CancelView(View):

    def get(self, request):
        order_id = request.GET.get('order_id')
        try:
            Orders.objects.get(id=order_id).delete()
            return JsonResponse({'msg': 1})
        except Orders.DoesNotExist:
            return JsonResponse({'msg': 0})
    

class TotalView(View):

    def get(self, request):
        pro = request.user.pro
        today = time.strftime("%Y-%m-%d")
        department = pro.department.name_id
        pro_1 = Pro.objects.filter(floor=1)
        orders_1 = Orders.objects.filter(pro=pro_1, create_time = today)
        pro_2 = Pro.objects.filter(floor=2)
        orders_2 = Orders.objects.filter(pro=pro_2, create_time = today)
        pro_3 = Pro.objects.filter(floor=3)
        orders_3 = Orders.objects.filter(pro=pro_3, create_time = today)
        foods = Food.objects.all()
        results = {'2':{}, '20':{}, '石景山':{}}
        for food in foods:
            orders_1_food = orders_1.filter(food=food)
            orders_2_food = orders_2.filter(food=food)
            orders_3_food = orders_3.filter(food=food)
            results['2'].update({food.name: len(orders_1_food)})
            results['20'].update({food.name: len(orders_2_food)})
            results['石景山'].update({food.name: len(orders_3_food)})
        results['2'] = results['2'].items()
        results['20'] = results['20'].items()
        results['石景山'] = results['石景山'].items()
        items = results.items()
        return render(request, 'dinner-total.html', { "pro": pro, "items": items})


# class TypeView(View):
    
#     def get(self, request):
#         if request.user.person.person_department.name_id == 1:
#             types = Type.objects.all()
#             return render(request, 'type.html', {"types": types})
#         else:
#             raise Http404
        

# class DelTypeView(View):

#     def get(self, request):
#         type_id = request.GET.get('type_id')
#         get_object_or_404(Type, pk=type_id).delete()
#         return JsonResponse({'msg': 1})


# class ShowTypeView(View):

#     def get(self, request):
#         if request.user.pro.user_manger:
#             type_id = request.GET.get('type_id')
#             the_type = Type.objects.get(id=type_id)
#             form = TypeForm(instance=the_type)
#             return render(request, 'showtype.html', {'form': form, 'type_id': type_id})
#         else:
#             raise Http404

#     def post(self, request):
#         if request.user.pro.user_manger:
#             type_id = request.POST.get('type_id')
#             the_type = Type.objects.get(pk=type_id)
#             form = TypeForm(request.POST, instance=the_type)
#             if form.is_valid():
#                 form.save()
#                 return HttpResponseRedirect('/dinner/type/')
#             else:
#                 return render(request, 'showtype.html', {'form': form})
#         else:
#             raise Http404


# class AddTypeView(View):

#     def get(self, request):
#         if request.user.pro.user_manger:
#             form = TypeForm()
#             return render(request, 'addtype.html', {'form': form})
#         else:
#             raise Http404

#     def post(self, request):
#         if request.user.pro.user_manger:
#             form = TypeForm(request.POST)
#             if form.is_valid():
#                 ch_name = form.cleaned_data['ch_name']
#                 en_name = form.cleaned_data['en_name']
#                 Type.objects.create(ch_name=ch_name, en_name=en_name)
#                 return HttpResponseRedirect('/type/')
#             else:
#                 return render(request, 'showtype.html', {'form': form})
#         else:
#             raise Http404

class FoodView(View):
    
    def get(self, request):
        if request.user.pro.user_manger:
            foods = Food.objects.all()
            return render(request, 'dinner-food.html', {'foods': foods})
        else:
            raise Http404


class DelFoodView(View):

    def get(self, request):
        food_id = request.GET.get('food_id')
        get_object_or_404(Food ,pk=food_id).delete()
        return JsonResponse({'msg': 1})


class ShowFoodView(View):
    def get(self, request):
        if request.user.pro.user_manger:
            pro = request.user.pro
            food_id = request.GET.get('food_id')
            food = Food.objects.get(id=food_id)
            form = FoodForm(instance=food)
            return render(request, 'dinner-showfood.html', {'form': form, 'food_id': food_id, 'pro': pro})
        else:
            raise Http404

    def post(self, request):
        if request.user.pro.user_manger:
            food_id = request.POST.get('food_id')
            the_food = Food.objects.get(pk=food_id)
            form = FoodForm(request.POST, instance=the_food)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/dinner/food/')
            else:
                return render(request, 'dinner-showfood.html', {'form': form})
        else:
            raise Http404


class AddFoodView(View):

    def get(self, request):
        if request.user.pro.user_manger:
            form = FoodForm()
            pro = request.user.pro
            return render(request, 'dinner-addfood.html', {'form': form, 'pro': pro})
        else:
            raise Http404

    def post(self, request):
        form = FoodForm(request.POST)
        if request.user.pro.user_manger:
            if form.is_valid():
                name = form.cleaned_data['name']
                info = form.cleaned_data['info']
                Food.objects.create(name=name, info=info)
                return HttpResponseRedirect('/dinner/food/')
            else:
                return render(request, 'dinner-addfood.html', {'form': form})
        else:
            raise Http404


class OrderList(ListView):

    queryset = Orders.objects.all()
    # context_object_name = 'orders'
    template_name = 'dinner-notes.html'

    def get_context_data(self, **kwargs):
        context = super(OrderList, self).get_context_data(**kwargs)
        user = self.request.user
        page_num = self.request.GET.get('page')
        if page_num:
            page_num = int(page_num)
        foods = Food.objects.all()
        objs = Orders.objects.all()
        p = Paginator(objs, 15)
        try:
            page = p.page(int(page_num))
        except:
            page = p.page(1)
        context['pro'] = user.pro
        context['page'] = page
        context['foods'] = foods
        return context



        
            


