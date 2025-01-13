from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Product, Customer, Category, AddToCart,Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'gender',)
    search_fields = ('user__email', 'phone_number')
    # Order the customer list by email (associated with the user)
    ordering = ('user__email',)


admin.site.register(Customer, CustomerAdmin)


class CategoryAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('name', 'description')
    search_fields = ('name',)  # Add a search box for category names
    ordering = ('name',)  # Order the list by category name
    list_per_page = 20  # Paginate the list view (20 categories per page)


admin.site.register(Category, CategoryAdmin)


@admin.register(AddToCart)
class AddToCartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('customer__user__email', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'order_date']
    list_filter = ['order_date', 'user']
    search_fields = ['user__username', 'product__name']
    date_hierarchy = 'order_date'
    readonly_fields = ['order_date']
    list_per_page = 20
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')