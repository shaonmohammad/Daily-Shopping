import json
from django.shortcuts import render, redirect
from .models import Product, Category, Customer, AddToCart
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.http import JsonResponse
# from sslcommerz  import SSLCSession
# from decimal import Decimal
# from django.urls import reverse
# from django.conf import settings

def home_view(request):
    categories = Category.objects.prefetch_related('products')
    all_categories = categories
    query = request.GET.get('q', '')
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        categories = categories.filter(id=selected_category_id)

    total_cart = 0
    if request.user.is_authenticated:
        try:
            total_cart = AddToCart.objects.filter(
                customer=request.user.customer
            ).count()
        except Exception as e:
            print(e)

    # Filter products dynamically for each category based on the search query
    categories_with_filtered_products = []
    for category in categories:
        filtered_products = category.products.all()
        if query:
            filtered_products = filtered_products.filter(
                Q(name__icontains=query)
            )

        categories_with_filtered_products.append({
            'category': category,
            'products': filtered_products,
        })

    context = {
        'categories_with_filtered_products': categories_with_filtered_products,
        'total_cart': total_cart,
        'query': query,
        'all_categories': all_categories
    }

    return render(request, 'home.html', context)


def product_details_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    samiller_products = Product.objects.filter(
        category=product.category).exclude(id=product.id)

    total_cart = 0
    if request.user.is_authenticated:
        try:
            total_cart = AddToCart.objects.filter(
                customer=request.user.customer
            ).count()
        except Exception as e:
            print(e)
    context =  {
        "product": product,
        "samiller": samiller_products,
        "total_cart":total_cart
        }
    return render(request, "product_details.html",context)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=email.split(
            '@')[0], password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            # messages.success(request, 'You have successfully logged in.')
            return redirect('home')  # Redirect to a home page or dashboard
        else:
            # Invalid credentials
            error_message = 'Invalid email or password.'
            return render(request, 'login.html', {'error_message': error_message})

    else:
        return render(request, 'login.html')


def logout_view(request):
    print("click log")
    logout(request)
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        gender = request.POST.get('gender')

        try:
            # Create user
            username = email.split('@')[0]
            user = User.objects.create(username=username)
            user.set_password(password)
            user.username = username
            user.save()

            # Create customer profile
            Customer.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
                gender=gender
            )

            messages.success(
                request, "Registration successful! Please log in.")
            return redirect('login')
        except Exception as e:
            return render(request, 'register.html', {'error': str(e)})

    return render(request, 'register.html')


def cart_list_view(request):
    cartlist = AddToCart.objects.filter(
        customer=request.user.customer).select_related('product')

    total_cart = 0
    total_price = 0

    if request.user.is_authenticated:
        total_cart = cartlist.count()
        total_price = sum(item.product.price * item.quantity for item in cartlist)
    
    context =  {
        'cart_items': cartlist,
        'total_cart': total_cart,
        'total_price':total_price
        }
    return render(request, 'cartlist.html',context)


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            product = Product.objects.get(id=product_id)
            print(product, 'product')
            # Check if the cart item already exists
            cart_item, created = AddToCart.objects.get_or_create(
                customer=request.user.customer,
                product=product,
            )
            print(cart_item)
            if not created:
                # If already exists, increment quantity
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({"message": "Product added to cart successfully."})
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def remove_cart_item(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = data.get("item_id")
            # Assume `CartItem` is your model for cart items
            cart_item = AddToCart.objects.get(id=item_id)
            cart_item.delete()

            return JsonResponse({
                "success": True
            })
        except AddToCart.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request."})


# Implementation of Payment method SSL Commerz
# def initiate_payment(request):
#     if request.method == 'POST':
#         # Fetch cart items and calculate total price
#         cart_items = AddToCart.objects.filter(customer=request.user.customer)
#         total_amount = sum(item.product.price * item.quantity for item in cart_items)

#         # SSLCommerz payment initialization
#         sslcz = SSLCSession(
#             sslc_is_sandbox=settings.SSLCOMMERZ['sandbox'], 
#             sslc_store_id=settings.SSLCOMMERZ['store_id'], 
#             sslc_store_pass=settings.SSLCOMMERZ['store_password']
#         )
#         sslcz.set_urls(
#             success_url=request.build_absolute_uri(reverse('payment_success')),
#             fail_url=request.build_absolute_uri(reverse('payment_fail')),
#             cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
#             ipn_url=request.build_absolute_uri(reverse('payment_ipn')),
#         )
#         sslcz.set_product_integration(
#             total_amount=Decimal(total_amount),
#             currency="BDT",
#             product_category="Shopping",
#             product_name="Shopping Cart Items",
#             num_of_item=len(cart_items),
#             shipping_method="Courier",
#             product_profile="general",
#         )
#         sslcz.set_customer_info(
#             name=request.user.username,
#             email=request.user.email,
#             address=request.user.customer.address,
#             city="Dhaka",
#             postcode="1212",
#             country="Bangladesh",
#             phone=request.user.customer.phone_number,
#         )
#         sslcz.set_shipping_info(
#             shipping_to=request.user.username,
#             address=request.user.customer.address,
#             city="Dhaka",
#             postcode="1212",
#             country="Bangladesh",
#         )

#         # Create the session
#         response_data = sslcz.init_payment()
#         return redirect(response_data['GatewayPageURL'])
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# def payment_success(request):
#     return JsonResponse({'status': 'success', 'message': 'Payment completed successfully!'})

# def payment_fail(request):
#     return JsonResponse({'status': 'fail', 'message': 'Payment failed. Please try again.'})

# def payment_cancel(request):
#     return JsonResponse({'status': 'cancel', 'message': 'Payment cancelled by the user.'})

# def payment_ipn(request):
#     # Handle SSLCommerz IPN (Instant Payment Notification)
#     if request.method == 'POST':
#         data = request.POST
#         # Verify payment status and update order/payment status
#         return JsonResponse({'status': 'received', 'message': 'IPN received.'})
#     return JsonResponse({'error': 'Invalid request'}, status=400)
