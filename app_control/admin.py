from django.contrib import admin
from .models import InventoryGroup, Inventory, Shop

admin.site.register((InventoryGroup, Inventory, Shop))
