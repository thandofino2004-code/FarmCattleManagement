from django.contrib import admin
from .models import Cattle
#from health.models import HealthRecord
#from health.models import Vaccine
#from health.models import Vaccination
#from breeding.models import PregnancyRecord
#from breeding.models import CalvingRecord
#from weight.models import WeightRecord
#from finance.models import Sale
#from finance.models import Purchase
#from finance.models import Expense



@admin.register(Cattle)
class CattleAdmin(admin.ModelAdmin):
    list_display = ['gov_tag','ear_tag','name', 'breed', 'sex', 'health_status','current_status', 'location']
    list_filter = ['breed', 'sex', 'health_status','current_status', 'colour']
    search_fields = ['gov_tag','ear_tag', 'name',
                     ]

    list_editable = ['health_status', 'current_status', 'location']

fieldsets = (
    ('Identification', {
        'fields': ('gov_tag', 'ear_tag', 'name')
    }),
    ('Animal Details', {
        'fields' : ('breed', 'sex', 'colour', 'date_of_birth', 'photo')
    }),
    ('Health & Status', {
        'fields': ('health_status', 'current_status', 'location')
    }),
    ('Family & Purchase', {
        'fields': ('mother_gov_tag', 'father_gov_tag', 'purchase_date', 'purchase_price', 'source_supplier')
    }),
    ('Additional', {
        'fields': ('notes',),
        'classes':('collapse',)
    }),
)

ordering = ['gov_tag']

# Register your models here.
