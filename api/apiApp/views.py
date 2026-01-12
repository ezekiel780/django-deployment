import uuid
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem, Category, Product, Review
from .serializers import (CartItemSerializer, CartSerializer, 
                         CategoryDetailSerializer, CategorySerializer,
                         ProductDetailSerializer, ProductSerializer, 
                         ReviewSerializer)
from .tasks import update_product_rating

# Import from helper (at project level)
from helper import (success_response, error_response, validate_rating, 
                   validate_email, generate_unique_code)


@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return success_response(
        data=serializer.data,
        message='Products retrieved successfully'
    )
    


@api_view(['GET'])
def product_detail(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializers = CategorySerializer(categories, many=True)
    return Response(serializers.data)


@api_view(['GET'])
def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug)
        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response(
            {'error': 'Category not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


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


# ==================== REVIEW ENDPOINTS ====================

@api_view(['POST'])
def create_review(request):
    """Create a new review"""
    User = get_user_model()
    product_id = request.data.get("product_id")
    email = request.data.get("email")
    rating = request.data.get("rating")
    comment = request.data.get("comment")
    
    # Validate required fields
    if not all([product_id, email, rating, comment]):
        return Response(
            {'error': 'product_id, email, rating, and comment are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=user).exists():
        return Response(
            {'error': 'You have already reviewed this product'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create review
    review = Review.objects.create(
        product=product, 
        user=user, 
        rating=rating, 
        comment=comment
    )
    
    # Trigger Celery task to update product rating in background
    update_product_rating.delay(product.id)
    
    serializer = ReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def product_reviews(request, product_slug):
    """Get all reviews for a specific product"""
    try:
        product = Product.objects.get(slug=product_slug)
        reviews = product.reviews.all().order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH'])
def update_review(request, review_id):
    """Update an existing review"""
    User = get_user_model()
    email = request.data.get("email")
    
    if not email:
        return Response(
            {'error': 'email is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        review = Review.objects.get(id=review_id, user=user)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Review.DoesNotExist:
        return Response(
            {'error': 'Review not found or you do not have permission to edit it'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update fields if provided
    if 'rating' in request.data:
        review.rating = request.data['rating']
    if 'comment' in request.data:
        review.comment = request.data['comment']
    
    review.save()
    
    # Trigger Celery task to update product rating
    update_product_rating.delay(review.product.id)
    
    serializer = ReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_review(request, review_id):
    """Delete a review"""
    User = get_user_model()
    email = request.data.get("email")
    
    if not email:
        return Response(
            {'error': 'email is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        review = Review.objects.get(id=review_id, user=user)
        product_id = review.product.id
        review.delete()
        
        # Trigger Celery task to update product rating
        update_product_rating.delay(product_id)
        
        return Response(
            {'message': 'Review deleted successfully'},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Review.DoesNotExist:
        return Response(
            {'error': 'Review not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def user_reviews(request, email):
    """Get all reviews by a specific user"""
    User = get_user_model()
    
    try:
        user = User.objects.get(email=email)
        reviews = Review.objects.filter(user=user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

