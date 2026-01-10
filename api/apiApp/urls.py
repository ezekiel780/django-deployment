from django.urls import path
from . import views

urlpatterns = [
    path("product_lists/", views.product_list, name="product_list"),
    path("product_list/", views.product_list, name="product_list_alt"),  # Support both singular and plural
    path("Product_list/", views.product_list, name="product_list_capital"),  # Support capital case
    path("product_detail/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category_lists/", views.category_list, name="category_list"),
    path("category_list/", views.category_list, name="category_list_alt"),  # Support both singular and plural
    path("Category_list/", views.category_list, name="category_list_capital"),  # Support capital case
    path("category_detail/<slug:slug>/", views.category_detail, name="category_detail"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("update_cartitem_quantity/", views.update_cartitem_quantity, name="update_cartitem_quantity"),
    path("add_review/", views.add_review, name="add_review")
]
