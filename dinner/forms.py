from django.forms import ModelForm
from .models import Food


# class TypeForm(ModelForm):
#     class  Meta:
# 	    model = Type
# 	    fields = ('id', 'ch_name', 'en_name')


class FoodForm(ModelForm):
    class  Meta:
	    model = Food
	    fields = ('id', 'name', 'info')	