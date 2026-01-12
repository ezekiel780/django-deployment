from django.urls import path
from . import views

urlpatterns = [
    # Product endpoints
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/<slug:slug>/reviews/", views.product_reviews, name="product_reviews"),
    
    # Category endpoints
    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),
    
    # Cart endpoints
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/items/update/", views.update_cartitem_quantity, name="update_cartitem_quantity"),
    
    # Review endpoints
    path("reviews/", views.create_review, name="create_review"),
    path("reviews/<int:review_id>/", views.update_review, name="update_review"),
    path("reviews/<int:review_id>/delete/", views.delete_review, name="delete_review"),
    path("users/<str:email>/reviews/", views.user_reviews, name="user_reviews"),
    
    # Legacy endpoints (backward compatibility)
    path("product_list/", views.product_list, name="product_list_alt"),
    path("category_list/", views.category_list, name="category_list_alt"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart_legacy"),
    path("add_review/", views.create_review, name="add_review_legacy"),
]
