from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Cart, CartItem, Product, Category, Review


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'image']


class CategoryListSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug', 'products']


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'products']


ProductSerializer = ProductListSerializer
CategorySerializer = CategoryListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'sub_total']

    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(read_only=True, many=True)
    cart_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ["id", "cart_code", "cart_items", "cart_total"]
    
    def get_cart_total(self, cart):
        items = cart.cart_items.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total


class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ["id", "cart_code", "total_quantity"]
    
    def get_total_quantity(self, cart):
        items = cart.cart_items.all()
        total = sum([item.quantity for item in items])
        return total


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'profile_picture']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        