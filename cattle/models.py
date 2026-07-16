from django.db import models
from django.utils import timezone 



class Cattle(models.Model):
    """Represents a single animal in the herd"""
#each field becomes a column in the database
    gov_tag = models.CharField(
        max_length=20,
        unique=True,
        help_text="Official Government Tag number"
    )
    ear_tag = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique identification tag number bought for animal"
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional name for the animal"
    )
    BREED_CHOICES=[
            ('Simmental', 'Simmental'),
            ('Brahman', 'Brahman'),
            ('Angus', 'Angus'),
            ('Hereford', 'Hereford'),
            ('Tswana', 'Tswana'),
            ('Nguni', 'Nguni'),
            ('Crossbreed', 'Crossbreed'),
            ('Other','Other'),
        ]
    breed = models.CharField(max_length=50, choices=BREED_CHOICES)
    SEX_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)

    COLOUR_CHOICES = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Brown', 'Brown'),
        ('Red', 'Red'),
        ('Roan', 'Roan'),
        ('Grey', 'Grey'),
        ('Spotted', 'Spotted'),
        ('Tshwaana','Tshwaana'),
        ('Other', 'Other'),
    ]
    colour = models.CharField(max_length=20, choices=COLOUR_CHOICES, blank=True, null=True)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Sold', 'Sold'),
        ('Missing', 'Missing'),
        ('Deceased', 'Deceased'),

    ]
    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active'
    )

    HEALTH_STATUS_CHOICES = [
        ('Healthy', 'Healthy'),
        ('Sick', 'Sick'),
        ('Injury', 'Injury'),
        ('Under Treatment', 'Under Treatment'),
        ('Quarantined', 'Qurantined'),
    ]
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default='Healthy'
    )

    location = models.CharField(
        max_length=100,
        default='Kraal 1',
        help_text="Current kraal"
    )

    mother_gov_tag = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Government tag of mother"
     )
    
    father_gov_tag = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Government tag of father"
    )

    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Purchase price in BWP"
    )

    source_supplier = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Where the animal was purchased from"
    )

    photo = models.ImageField(
        upload_to='cattle_photos/',
        blank=True,
        null=True,
        help_text="Upload a photo of the animal"
    )

    notes = models.TextField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        """How model appears in the admin and shell"""
        if self.gov_tag and self.ear_tag:
         return f"{self.gov_tag} ({self.ear_tag}) -{self.name or 'unnamed'}"
        elif self.gov_tag:
            return f"{self.gov_tag} - {self.name or 'unnamed'}"
        
        elif self.ear_tag:
            return f"{self.ear_tag} -{self.name or 'Unnamed'}"
        
        else:
            return f"Cattle #{self.id} -{self.name or 'Unnamed'}"
    

    @property
    def age(self):
        """Calculate age from date_of_birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    class Meta:
        ordering = ['gov_tag']
        verbose_name_plural = "Cattle"


class CattleEvent(models.Model):
    EVENT_TYPES = [
        ('BIRTH', 'Birth'),
        ('CALVING', 'Calving'),
        ('VACCINATION', 'Vaccination'),
        ('HEALTH_CHECK', 'Health Check'),
        ('SOLD', 'Sold'),
        ('PURCHASED', 'Purchased'),
        ('MISSING_REPORTED', 'Missing Reported'),
        ('FOUND', 'Found'),
    ]
    
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.cattle.gov_tag} - {self.event_type} ({self.event_date})"
    
    class Meta:
        ordering = ['-event_date']
        verbose_name_plural = "Cattle Events"




# Create your models here.
