from rest_framework import serializers
from .models import Product, Category, cart, cartItem


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
        fields = ['id', 'name', 'image','slug', 'products']

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'products']

ProductSerializer = ProductListSerializer
CategorySerializer = CategoryListSerializer

class cartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()
    class Meta:
        model = cartItem
        fields = ['id', 'product', 'quantity', 'sub_total']

    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total
    

class cartSerializer(serializers.ModelSerializer):
    cartitems = cartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()
    class Meta:
        model = cart
        fields = ['id', 'cart_code', 'cartitems', 'total_price']

    def get_cart_total(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total
    

class CartStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = cart
        fields = ['id', 'cart_code','total_quantity']

        def get_total_quantity(self, cart):
            items = cart.cartitems.all()
            total = sum([item.quantity * item.product.price for item in items])
            return total
    