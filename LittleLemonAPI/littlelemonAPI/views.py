from rest_framework import generics
import math
from datetime import date
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest, request
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from .paginations import MenuItemListPagination
from .models import MenuItem, Cart, Order, OrderItem, Category
from .serializers import (
    MenuItemSerializer,
    ManagerListSerializer,
    CartSerializer,
    CartAddSerializer,
    OrderSerializer,
    OrderPutSerializer,
    CartRemoveSerialzer,
    CategorySerializer,
    SingleOrderSerializer,
)

from .permissions import IsManager, IsDeliveryCrew


# Create your views here.
class MenuItemListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ["title", "category__title"]
    ordering_fields = ["price", "category"]
    pagination_class = MenuItemListPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class CategoryView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]


class MenuItemDetailsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == "PATCH":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs["pk"])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return JsonResponse(
            status=200,
            data={
                "message": f"Featured status of {menuitem.title} changed to {menuitem.featured}"
            },
        )


class ManagerListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name="Managers")
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Managers")
            managers.user_set.add(user)
            return JsonResponse(
                status=201, data={"message": "User added to Managers group"}
            )


class ManagersRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name="Managers")
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    serializer_class = ManagerListSerializer

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name="Managers")
        managers.user_set.remove(user)
        return JsonResponse(status=200, data={"message": "User removed Managers Group"})


class DeliveryCrewListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name="Delivery Crew")
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            crew = Group.objects.get(name="Delivery Crew")
            crew.user_set.add(user)
            return JsonResponse(
                satus=201, data={"message": "USer added to the delivery Crew group"}
            )


class DeliveryCrewRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name="Delivery Crew")
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name="Delivery Crew")
        managers.user_set.remove(user)
        return JsonResponse(
            status=201, data={"Message": "User removed from the Delivery Crew group"}
        )


class CartOperationsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *agrs, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart

    def post(self, *args, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data["quantity"]
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(
                user=request.user,
                quantity=quantity,
                unit_price=item.price,
                price=price,
                menuitem_id=id,
            )
        except:
            return JsonResponse(status=409, data={"message": "Item already in cart"})
        return JsonResponse(status=201, data={"Message": "Item added to the cart!"})

    def delete(self, request, *args, **kwargs):
        if request.data["menuitem"]:
            serialized_item = CartRemoveSerialzer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data["menuitem"]
            cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem)
            cart.delete()
            return JsonResponse(status=200, data={"message": "Items removed from cart"})
        else:
            Cart.objects.filter(user=request.user).delete()
            return JsonResponse(
                status=201, data={"message": "ALl Items removed ftom the cart"}
            )


class OrderOperationsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    def get_queryset(self, *args, **kwargs):
        if (
            self.request.user.groups.filter(name="Managers").exists()
            or self.request.user.is_superuser == True
        ):
            query = Order.objects.all()
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query

    def get_permissisions(self):
        if self.request.method == "GET" or "POST":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        x = cart.values_list()
        if len(x) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([float(x[-1]) for x in x])
        order = Order.objects.create(
            user=request.user, status=False, total=total, date=date.today()
        )
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i["menuitem_id"])
            orderitem = OrderItem.objects.create(
                order=order, menuitem=menuitem, quantity=i["quantity"]
            )
            orderitem.save()
        cart.delete()
        return JsonResponse(
            status=201,
            data={
                "message": f"Your order has been placed and your order number is #{order.id}"
            },
        )


class SingleOrderView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer

    @api_view(['GET', 'POST', "DELETE", "PUT"])
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs["pk"])
        if self.request.user == order.user and self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif self.request.method == "PUT" or self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [
                IsAuthenticated,
                IsDeliveryCrew | IsManager | IsAdminUser,
            ]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        query = OrderItem.objects.filter(order_id=self.kwargs["pk"])
        return query

    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs["pk"])
        order.status = not order.status
        order.save()
        return JsonResponse(
            status=200,
            data={
                "message": "Status of order #"
                + str(order.id)
                + " Change to "
                + str(order.status)
            },
        )

    def put(self, request, *args, **kwargs):
        serilized_item = OrderPutSerializer(data=request.data)
        serilized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs["pk"]
        crew_pk = request.data["delivery_crew"]
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(
            status=201,
            data={
                "message": str(crew.username)
                + " was assigned to order #"
                + str(order.id)
            },
        )

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs["pk"])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(
            status=200, data={"message": f"Order #{order_number} was deleted"}
        )
