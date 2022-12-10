from rest_framework.viewsets import ModelViewSet
from .serializers import (
    Inventory, InventorySerializer, InventoryGroupSerializer, InventoryGroup,
    Shop, ShopSerializer
)
from rest_framework.response import Response
from inventory_api.custom_methods import IsAuthenticatedCustom
from inventory_api.utils import get_query, CustomPagination
from django.db.models import Count


class InventoryView(ModelViewSet):
    queryset = Inventory.objects.select_related("group", "created_by")
    serializer_class = InventorySerializer
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination
    
    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        
        results = self.queryset(**data)
        
        if keyword:
            search_fields = (
                "code", "name", "created_by__fullname", "updated_by__email",
                "group_name",
            )
            query = get_query(keyword, search_fields)
            return results.filter(query)
        
        return results       
    
    
class InventoryGroupView(ModelViewSet):
    queryset = InventoryGroup.objects.select_related(
        "group", "created_by").prefetch_related("inventories")
    serializer_class = InventoryGroupSerializer
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        
        results = self.queryset(**data)
        
        if keyword:
            search_fields = (
                "name", "created_by__fullname", "updated_by__email",
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results.annotate(
            total_items = Count('inventories')
        )    
    
    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)
    

class ShopView(ModelViewSet):
    queryset = Shop.objects.select_related("created_by")
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        
        results = self.queryset(**data)
        
        if keyword:
            search_fields = (
                "name", "created_by__fullname", "updated_by__email",
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results   
    
    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)