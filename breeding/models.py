from django.db import models
from cattle.models import Cattle 


class PregnancyRecord(models.Model):
    """Tracks pregnancy and breeding information for female cattle"""
    
    # Link to the female cattle (mother)
    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='pregnancies',
        limit_choices_to={'sex': 'Female'},  # Only female cattle can be pregnant
        help_text="The female animal that is/was pregnant"
    )
    
    # Optional link to the father (if known)
    sire = models.ForeignKey(
        Cattle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sired_pregnancies',
        limit_choices_to={'sex': 'Male'},  # Only male cattle can be sires
        help_text="The male animal that sired the pregnancy (if known)"
    )
    
    # For when the sire is not in the system
    sire_external = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Description of sire if not in system (e.g., 'AI Bull #123')"
    )
    
    # Breeding information
    BREEDING_METHOD_CHOICES = [
        ('NATURAL', 'Natural Mating'),
        ('AI', 'Artificial Insemination'),
    ]
    breeding_method = models.CharField(
        max_length=20,
        choices=BREEDING_METHOD_CHOICES,
        default='NATURAL'
    )
    
    service_date = models.DateField(
        help_text="Date of breeding/insemination"
    )
    
    # Pregnancy status
    PREGNANCY_STATUS_CHOICES = [
        ('SUSPECTED', 'Suspected'),
        ('CONFIRMED', 'Confirmed'),
        ('ABORTED', 'Aborted'),
        ('CALVED', 'Calved'),
        ('NOT_PREGNANT', 'Not Pregnant'),
    ]
    pregnancy_status = models.CharField(
        max_length=20,
        choices=PREGNANCY_STATUS_CHOICES,
        default='SUSPECTED'
    )
    
    # Dates
    confirmation_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date pregnancy was confirmed"
    )
    
    expected_calving_date = models.DateField(
        blank=True,
        null=True,
        help_text="Expected date of calving (280 days after service)"
    )
    
    actual_calving_date = models.DateField(
        blank=True,
        null=True,
        help_text="Actual date of calving (filled when calving occurs)"
    )
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    
    # Who confirmed (for future user system)
    # confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """How this appears in admin"""
        return f"{self.cattle.gov_tag} - {self.pregnancy_status} ({self.service_date})"
    
    @property
    def is_pregnant(self):
        """Check if currently pregnant"""
        return self.pregnancy_status in ['SUSPECTED', 'CONFIRMED']
    
    @property
    def days_pregnant(self):
        """Calculate days since service date"""
        if self.service_date and self.is_pregnant:
            from datetime import date
            return (date.today() - self.service_date).days
        return None
    
    class Meta:
        ordering = ['-service_date']
        verbose_name_plural = "Pregnancy Records"

class CalvingRecord(models.Model):
    """Records when a calf is born"""
    
    # Link to the mother
    mother = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name='calvings',
        limit_choices_to={'sex': 'Female'},
        help_text="The mother that gave birth"
    )
    
    # Optional link to pregnancy record
    pregnancy = models.ForeignKey(
        PregnancyRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calving',
        help_text="Link to the pregnancy record (if tracked)"
    )
    
    # Link to the calf (new cattle record)
    calf = models.OneToOneField(
        Cattle,
        on_delete=models.CASCADE,
        related_name='birth_record',
        help_text="The calf that was born"
    )
    
    # Calving details
    calving_date = models.DateField(
        help_text="Date of birth"
    )
    
    CALVING_OUTCOME_CHOICES = [
        ('LIVE', 'Live Birth'),
        ('STILLBIRTH', 'Stillbirth'),
        ('MISCARRIAGE', 'Miscarriage'),
    ]
    calving_outcome = models.CharField(
        max_length=20,
        choices=CALVING_OUTCOME_CHOICES,
        default='LIVE'
    )
    
    # Twin support
    number_of_calves = models.PositiveSmallIntegerField(
        default=1,
        help_text="Number of calves born"
    )
    
    # Additional information
    complications = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Who assisted (for future user system)
    # assisted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """How this appears in admin"""
        return f"{self.mother.gov_tag} → {self.calf.gov_tag} ({self.calving_date})"
    
    class Meta:
        ordering = ['-calving_date']
        verbose_name_plural = "Calving Records"

# Create your models here.
