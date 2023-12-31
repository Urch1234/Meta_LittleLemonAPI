from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category, Cart, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]
        depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "title", "price"]


class CartHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price"]


class CartSerializer(serializers.ModelSerializer):
    menuItem = CartHelpSerializer()

    class Meta:
        model = Cart
        fields = ["menuitem", "quantity", "price"]


class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["menuitem", "quantity"]
        extra_kwargs = {
            "quantity": {"min_value": 1},
        }


class CartRemoveSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["menuitem"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        models = User
        fields = ["id", "username"]


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ["id", "user", "total", "status", "delivery_crew", "date"]


class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["title", "price"]


class SingleOrderSerializer(serializers.ModelSerializer):
    MenuItem = SingleHelperSerializer()

    class Meta:
        model = OrderItem
        fields = ["menuitem", "quantity"]


class OrderPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["delivery_crew"]
