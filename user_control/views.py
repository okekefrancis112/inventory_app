from rest_framework.viewsets import ModelViewSet
from .serializers import( 
                         CreateUserSerializer, CustomUser, LoginSerializer, UpdatePasswordSerializer,
                         CustomUserSerializer, UserActivitiesSerializer, UserActivities,                        
                         )
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import datetime
from inventory_api.utils import get_access_token, CustomPagination, get_query
from inventory_api.custom_methods import IsAuthenticatedCustom


def add_user_activity(user, action):
    UserActivities.objects.create(
        user_id = user.id,
        email = user.email,
        fullname = user.fullname,
        action = action,
    )

class CreateUserView(ModelViewSet):
    http_method_names = ['post']
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (IsAuthenticatedCustom, )
    
    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)
        
        CustomUser.objects.create(**valid_request.validated_data)
        
        add_user_activity(request.user, "added new user")
        
        return Response(
            {"success": "User created successfully"}, 
            status=status.HTTP_201_CREATED
        )
  
class LoginView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        new_user = valid_request.validated_data["is_new_user"]

        if new_user:
            user = CustomUser.objects.filter(
                email=valid_request.validated_data["email"]
            )

            if user:
                user = user[0]
                if not user.password:
                    return Response({"user_id": user.id})
                else:
                    raise Exception("User has password already")
            else:
                raise Exception("User with email not found")

        user = authenticate(
            username=valid_request.validated_data["email"],
            password=valid_request.validated_data.get("password", None)
        )

        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        access = get_access_token({"user_id": user.id}, 1)

        user.last_login = datetime.now()
        user.save()

        add_user_activity(user, "logged in")

        return Response({"access": access})
    
class UpdatePasswordView(ModelViewSet):
    http_method_names = ['post']
    queryset = CustomUser.objects.all()
    serializer_class = UpdatePasswordSerializer
    
    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)  
        
        user = CustomUser.objects.filter(
            id=valid_request.validated_data["user_id"],
        )
        
        if not user:
            raise Exception("User with id not found")
        
        user = user[0]
        
        user.set_password(valid_request.validated_data["password"])
        user.save()
        
        add_user_activity(request.user, "updated password")
        
        return Response({"success": "User password updated"})
        

class MeView(ModelViewSet):
    http_method_names = ['get']
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedCustom, )
    
    def list(self, request):
        data =  self.serializer_class(request.user).data
        return Response(data)
    
class UserActivitiesView(ModelViewSet):
    serializer_class = UserActivitiesSerializer
    http_method_names = ["get"]
    permission_classes = (IsAuthenticatedCustom, )
    queryset = UserActivities.objects.all()
    # queryset = UserActivities.objects.select_related("user")
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.request.query_params.dict()
        data.pop("page", None)
        keyword = data.pop("keyword", None)

        results = self.queryset.filter(**data)

        if keyword:
            search_fields = (
                "fullname", "email", "action"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results
    
class UsersView(ModelViewSet):
    http_method_names = ['get']  
    # queryset = CustomUser.objects.prefetch_related("user_activities")
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedCustom, )
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.request.query_params.dict()
        data.pop("page", None)
        keyword = data.pop("keyword", None)

        results = self.queryset.filter(**data, is_superuser=False)

        if keyword:
            search_fields = (
                "fullname", "email", "role"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results
    
    #     "user_id": 7
    
    # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzA4OTQ3NTYsInVzZXJfaWQiOjd9.u2swEBasbm0h4XVpSc83zmgS1Y970tHVq9P3-wkhzk0
    
    # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzA4OTE2OTksInVzZXJfaWQiOjZ9.pNasPhn7RVik-rfSnrDDNQSQ7AquWfQSjOaTKIt3r2c