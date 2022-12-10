from django.contrib import admin
from .models import InventoryGroup, Inventory

admin.site.register((InventoryGroup, Inventory, ))
