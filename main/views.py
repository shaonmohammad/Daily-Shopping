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
from sslcommerz_lib  import SSLCOMMERZ
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
import datetime

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
            user = User.objects.create(username=username,email=email)
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
    product_id = request.GET.get('product_id')
    if product_id:
        product = Product.objects.get(id=product_id)
        cartlist,created = AddToCart.objects.get_or_create(customer=request.user.customer,product=product)
        total_price = product.price
        total_cart = 1
    else:
        cartlist = AddToCart.objects.filter(
        customer=request.user.customer).select_related('product')
        total_price = 0
        total_cart = cartlist.count()

        if request.user.is_authenticated:
            total_price = sum(item.product.price * item.quantity for item in cartlist)
        
    context =  {
        'cart_items': [cartlist] if product_id else cartlist,
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

def initiate_payment(request):
    if request.method == 'POST':
        try:
            # Fetch cart items and calculate total price
            cart_items = AddToCart.objects.filter(customer=request.user.customer)
            if not cart_items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            total_amount = sum(item.product.price * item.quantity for item in cart_items)

            settings_data = {
                'store_id': settings.SSLCOMMERZ['store_id'],
                'store_pass': settings.SSLCOMMERZ['store_password'],
                'issandbox': settings.SSLCOMMERZ['sandbox']
            }

            sslcz = SSLCOMMERZ(settings_data)
            post_body = {}
            post_body['total_amount'] = total_amount
            post_body['currency'] = "BDT"
            post_body['tran_id'] = f"TRANSACTION_{str(request.user.id)}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            post_body['success_url'] = request.build_absolute_uri(reverse('payment_success'))
            post_body['fail_url'] = request.build_absolute_uri(reverse('payment_fail'))
            post_body['cancel_url'] = request.build_absolute_uri(reverse('payment_cancel'))
            post_body['ipn_url'] = request.build_absolute_uri(reverse('payment_ipn'))
            post_body['cus_name'] = request.user.username
            post_body['cus_email'] = request.user.email
            post_body['cus_add1'] = request.user.customer.address
            post_body['cus_city'] = "Dhaka"
            post_body['cus_postcode'] = "1212"
            post_body['cus_country'] = "Bangladesh"
            post_body['cus_phone'] = request.user.customer.phone_number or "123"
            post_body['shipping_method'] = "NO"
            post_body['product_name'] = "Shopping Cart Items"
            post_body['product_category'] = "Shopping"
            post_body['product_profile'] = "general"

            response = sslcz.createSession(post_body)
            print(response)
            if response['status'] == 'SUCCESS':
                return redirect(response['GatewayPageURL'])
            else:
                return JsonResponse({'error': 'Payment initialization failed'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Verify the payment status
        payment_data = request.POST
        if 'status' in payment_data and payment_data['status'] == 'VALID':
            # Update your order status here
            return JsonResponse({'status': 'success', 'message': 'Payment completed successfully!'})
    return redirect('order_complete')  # Redirect to an order complete page

@csrf_exempt
def payment_fail(request):
    return redirect('cart_list')  # Redirect back to cart page

@csrf_exempt
def payment_cancel(request):
    return redirect('cart_list')  # Redirect back to cart page

@csrf_exempt
def payment_ipn(request):
    if request.method == 'POST':
        payment_data = request.POST
        if 'status' in payment_data:
            # Verify payment with SSLCommerz
            # Update order status accordingly
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)