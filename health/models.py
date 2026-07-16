from django.db import models
from cattle.models import Cattle 

class HealthRecord(models.Model):
    #link to which cattle it belongs to 

    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='health_records'
    )

    record_date = models.DateField(auto_now_add=True)

    HEALTH_STATUS_CHOICES = [
        ('Healthy', 'Healthy'),
        ('Sick', 'Sick'),
        ('Injury', 'Injury'),
        ('Under Treatment', 'Under Treatment'),
        ('Quarantined', 'Quarantied'),
    ]
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default='Healthy'
    )

    symptoms = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

   # recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cattle.gov_tag} -{self.cattle.ear_tag} -{self.health_status} on {self.record_date}"
    
    class Meta:
        ordering = ['-record_date'] #newest first
        verbose_name_plural = "Health Records"

class Vaccine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    #batchNumber = models.CharField(max_length=100, blank=True, null=True)
    default_interval_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of days until next dose is due"
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Meta:
        ordering = ['name']
        verbose_name_plural = "Vaccines"


class Vaccination(models.Model):
    """Records when a specific animal received a vaccine"""

    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='vaccinations'
    )

    vaccine = models.ForeignKey(
        Vaccine,
        on_delete=models.PROTECT, #dont delete vaccine if it has records
        related_name='vaccinations'
    )
    date_administered = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    dosage = models.CharField(max_length=50, blank=True, null=True)
    veterinarian = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    #Administered by(future improvements)
    #administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Check if vaccination is due"""
        return f"{self.cattle.gov_tag} -{self.cattle.ear_tag} -{self.vaccine.name} ({self.date_administered})"
    def is_due(self):
        from datetime import date
        if self.next_due_date:
         return self.next_due_date <= date.today()
        return False
     
class Meta:
        ordering = ['-date_administered']#newest first
        verbose_name_plural = "Vaccinations"


# Create your models here.
