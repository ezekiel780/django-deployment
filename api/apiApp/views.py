import uuid
from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Category, Product, Review
from .serializers import CartItemSerializer, CartSerializer, CategoryDetailSerializer, CategorySerializer, ProductDetailSerializer, ProductSerializer, ReviewSerializer


@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(featured=True)
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


@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')
    product_id = request.data.get('product_id')
    
    # Validate product_id
    if not product_id:
        return Response(
            {'error': 'product_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # If no cart_code provided, generate a new one
    if not cart_code:
        cart_code = str(uuid.uuid4())[:11].upper()
        cart = Cart.objects.create(cart_code=cart_code)
    else:
        # Try to get existing cart or create new one
        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    
    # Get or create cart item
    cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        # If cart item already exists, increment quantity
        cartitem.quantity += 1
    else:
        cartitem.quantity = 1
    
    cartitem.save()
    
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")
    
    # Validate inputs
    if not cartitem_id:
        return Response(
            {'error': 'item_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if quantity is None:
        return Response(
            {'error': 'quantity is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quantity = int(quantity)
        if quantity < 0:
            return Response(
                {'error': 'quantity must be a positive number'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError):
        return Response(
            {'error': 'quantity must be a valid number'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the cart item with error handling
    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
    except CartItem.DoesNotExist:
        return Response(
            {'error': f'CartItem with id {cartitem_id} does not exist'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Delete item if quantity is 0
    if quantity == 0:
        cart = cartitem.cart
        cartitem.delete()
        serializer = CartSerializer(cart)
        return Response(
            {
                'message': 'Item removed from cart',
                'cart': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
    
    # Update quantity
    cartitem.quantity = quantity
    cartitem.save()
    
    serializer = CartItemSerializer(cartitem)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_review(request):
    User = get_user_model
    product_id = request.data.get("product_id")
    email = request.data.get("email")
    rating = request.data.get("rating")
    comment = request.data.get("comment")


    product = Product.objects.get(id=product_id)
    user = User.objects.get(email=email)

    comment = Review.objects.create(product=product, user=user, rating=rating, comment=comment)
    serializer = ReviewSerializer(comment)
    return Response(serializer.data)
    
