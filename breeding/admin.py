from django.contrib import admin
from .models import PregnancyRecord
from .models import CalvingRecord


@admin.register(PregnancyRecord)
class PregnancyRecordAdmin(admin.ModelAdmin):
    list_display = [
        'cattle',
        'service_date',
        'pregnancy_status',
        'expected_calving_date',
        'is_pregnant',
    ]
    list_filter = ['pregnancy_status', 'breeding_method', 'service_date']
    search_fields = ['cattle__gov_tag', 'cattle__ear_tag']
    list_editable = ['pregnancy_status']
    
    fieldsets = (
        ('Animal', {
            'fields': ('cattle',)
        }),
        ('Breeding Details', {
            'fields': ('sire', 'sire_external', 'breeding_method', 'service_date')
        }),
        ('Pregnancy Status', {
            'fields': ('pregnancy_status', 'confirmation_date', 'expected_calving_date', 'actual_calving_date')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def is_pregnant(self, obj):
        """Show if currently pregnant"""
        return obj.pregnancy_status in ['SUSPECTED', 'CONFIRMED']
    is_pregnant.boolean = True
    is_pregnant.short_description = "Pregnant?"

@admin.register(CalvingRecord)
class CalvingRecordAdmin(admin.ModelAdmin):
    list_display = [
        'mother',
        'calf',
        'calving_date',
        'calving_outcome',
        'number_of_calves',
    ]
    list_filter = ['calving_outcome', 'calving_date']
    search_fields = ['mother__gov_tag', 'calf__gov_tag', 'mother__ear_tag']
    list_editable = ['calving_outcome']
    
    fieldsets = (
        ('Mother', {
            'fields': ('mother', 'pregnancy')
        }),
        ('Calf', {
            'fields': ('calf',)
        }),
        ('Calving Details', {
            'fields': ('calving_date', 'calving_outcome', 'number_of_calves', 'complications')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


# Register your models here.
