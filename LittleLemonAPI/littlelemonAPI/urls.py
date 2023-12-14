from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
   
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("menu-item", views.MenuItemListView.as_view()),
    path("menu-items/category", views.CategoryView.as_view()),
    path("menu-items/<int:pk>", views.MenuItemDetailsView.as_view()),
    path('groups/managers/users', views.ManagerListView.as_view()),
    path('groups/managers/users/<int:pk>', views.ManagersRemoveView.as_view()),
    path('groups/delivery-crew/users/users', views.DeliveryCrewListView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewRemoveView.as_view()),
    path('cart/menu-items', views.CartOperationsView.as_view()),
    path("orders", views.OrderOperationsView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
]
