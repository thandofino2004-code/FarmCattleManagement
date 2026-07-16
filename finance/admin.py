from django.contrib import admin
from .models import Cattle
from .models import Sale
from .models import Purchase
from .models import Expense


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['cattle', 'buyer_name', 'sale_date', 'sale_price', 'payment_status']
    list_filter = ['payment_status', 'sale_date']
    search_fields = ['cattle__gov_tag', 'cattle__ear_tag', 'buyer_name']
    list_editable = ['sale_price', 'payment_status']
    
    fieldsets = (
        ('Animal', {
            'fields': ('cattle',)
        }),
        ('Buyer Details', {
            'fields': ('buyer_name', 'buyer_contact')
        }),
        ('Sale Information', {
            'fields': ('sale_date', 'sale_price', 'payment_status')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['cattle', 'seller_name', 'purchase_date', 'purchase_price']
    list_filter = ['purchase_date']
    search_fields = ['cattle__gov_tag', 'cattle__ear_tag', 'seller_name']
    list_editable = ['purchase_price']
    
    fieldsets = (
        ('Animal', {
            'fields': ('cattle',)
        }),
        ('Seller Details', {
            'fields': ('seller_name', 'seller_contact')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'purchase_price')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'expense_date', 'description']
    list_filter = ['category', 'expense_date']
    search_fields = ['description', 'category']
    list_editable = ['amount']
    
    fieldsets = (
        ('Expense Details', {
            'fields': ('category', 'amount', 'expense_date', 'description')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

# Register your models here.
