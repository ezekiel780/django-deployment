from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategoryDetailSerializer, CategorySerializer, ProductDetailSerializer, ProductSerializer


@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializers = CategorySerializer(categories, many=True)
    return Response(serializers.data)

@api_view(['GET'])
def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)

