from django.db import models
from cattle.models import Cattle 


class WeightRecord(models.Model):
    """Tracks weight measurements for each animal over time"""
    
    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='weights'
    )
    
    weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        help_text="Weight in kilograms"
    )
    
    record_date = models.DateField(
        auto_now_add=True,
        help_text="Date of weight measurement"
    )
    
    notes = models.TextField(blank=True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.cattle.gov_tag} - {self.weight_kg}kg ({self.record_date})"
    
    class Meta:
        ordering = ['-record_date']
        verbose_name_plural = "Weight Records"
        unique_together = ['cattle', 'record_date']  # One weight per day per animal



# Create your models here.
