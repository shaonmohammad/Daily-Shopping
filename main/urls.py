from django.urls import path
from .views import home_view, login_view, register_view, logout_view, cart_list_view, add_to_cart, product_details_view,remove_cart_item
urlpatterns = [
    path('', home_view, name='home'),
    path('product/<int:product_id>', product_details_view, name="product-details"),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('cart-list/', cart_list_view, name='cart_list'),
    path('add-to-cart/', add_to_cart, name="add_to_cart"),
    path("remove-cart-item/", remove_cart_item, name="remove_cart_item"),
    
    # url for ssl payment method
    # path('checkout/', initiate_payment, name='initiate_payment'),
    # path('payment/success/', payment_success, name='payment_success'),
    # path('payment/fail/', payment_fail, name='payment_fail'),
    # path('payment/cancel/', payment_cancel, name='payment_cancel'),
    # path('payment/ipn/', payment_ipn, name='payment_ipn'), 
]
