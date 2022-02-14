import django_filters
from base.models import *


class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = ['name', 'dish_type']