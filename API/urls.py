from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path('received-messages/', views.getReceivedMessages, name='received'),
    path('received-messages/<int:id>', views.getReceivedMessage, name='receivedOne'),
    
    #Register
    path('signup/', views.signUp, name="signup"),
    
    #Login
    path('signin/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signin/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
