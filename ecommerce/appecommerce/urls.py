from django.urls import path
from .views import (create_customer, customer_profile, product_category_list,
                    widget_list, brand_list, variant_list, product_detail, inventory_detail, cart_list,
                    add_to_cart, remove_from_cart, update_cart_item_quantity, delete_customer_cart_items,
                    address_list, add_address, get_address_by_id, edit_address, delete_address, verify_otp,
                    add_to_wishlist, get_default_address, view_wishlist, remove_from_wishlist, clear_wishlist)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('customer/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('customer/login/token-refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('customer/sign-up', create_customer, name='create_customer'),
    path('customer/sign-up/verify-otp', verify_otp, name='verify_otp'),
    path('customer/details', customer_profile, name='customer_profile'),

    path('product/categories', product_category_list, name='product-categories'),
    path('product/widgets', widget_list, name='widgets'),
    path('product/brands', brand_list, name='brands'),
    path('product/variant-values', variant_list, name='variants'),
    path('product/product-detail/<int:product_id>', product_detail, name='product-detail'),
    path('product/inventory-detail/<int:inventory_id>', inventory_detail, name='inventory-detail'),

    path('cart/cart-items', cart_list, name='cart-list'),
    path('cart/cart-items/add', add_to_cart, name='cart-item'),
    path('cart/cart-items/update-quantity', update_cart_item_quantity, name='update-cart-item-quantity'),
    path('cart/cart-items/delete/<int:cart_item_id>', remove_from_cart, name='cart-item-delete'),
    path('cart/cart-items/delete-all', delete_customer_cart_items, name='delete-customer-cart-items'),

    path('address/address-list', address_list, name='address-list-get'),
    path('address/add', add_address, name='address-list-post'),
    path('address/address-list/<int:address_id>', get_address_by_id, name='get-address'),
    path('address/edit/<int:address_id>', edit_address, name='patch_address'),
    path('address/delete/<int:address_id>', delete_address, name='delete-address'),
    path('address/default-address', get_default_address, name='get_default_address'),

    path('wishlist/items', view_wishlist, name='view_wishlist'),
    path('wishlist/add-to-wishlist/<int:inventory_id>', add_to_wishlist, name='toggle_wishlist'),
    path('wishlist/remove-from-wishlist/<int:wishlist_item_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/remove-all', clear_wishlist, name='clear_wishlist'),
]
