from django.db import models
from cattle.models import Cattle 


class Sale(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.PROTECT)
    buyer_name = models.CharField(max_length=200)
    buyer_contact = models.CharField(max_length=100, blank=True, null=True)
    sale_date = models.DateField()
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(choices=[('Paid', 'Paid'), ('Pending', 'Pending'), ('Partial', 'Partial')])
    notes = models.TextField(blank=True, null=True)

class Purchase(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.PROTECT)
    seller_name = models.CharField(max_length=200)
    seller_contact = models.CharField(max_length=100, blank=True, null=True)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

class Expense(models.Model):
    #farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    CATEGORY_CHOICES = [
        ('Food/Feed', 'Food/Feed'),
        ('Salaries', 'Salaries'),
        ('Veterinary', 'Veterinary'),
        ('Medicine', 'Medicine'),
        ('Equipment', 'Equipment'),
        ('Transport', 'Transport'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category} - P{self.amount} ({self.expense_date})"
    
    class Meta:
        ordering = ['-expense_date']
        verbose_name_plural = "Expenses"



# Create your models here.
