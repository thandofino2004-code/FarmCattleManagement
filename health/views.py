from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.db.models import Count, Q
from datetime import datetime, timedelta
from cattle.models import Cattle, CattleEvent
from .models import Vaccination
from .models import Vaccine
from .models import HealthRecord
from breeding.models import PregnancyRecord
from weight.models import WeightRecord
from django.contrib.auth.decorators import login_required


@login_required
def health_dashboard(request):
    """Health overview page"""
    
    # Get all health records
    health_records = HealthRecord.objects.select_related('cattle').order_by('-record_date')[:50]
    
    # Get sick cattle
    sick_cattle = Cattle.objects.filter(health_status='Sick')
    under_treatment = Cattle.objects.filter(health_status='Under Treatment')
    
    context = {
        'health_records': health_records,
        'sick_cattle': sick_cattle,
        'sick_count': sick_cattle.count(),
        'under_treatment': under_treatment,
        'under_treatment_count': under_treatment.count(),
    }
    return render(request, 'health/health_dashboard.html', context)

@login_required
def health_record_add(request, cattle_id):
    """Add a health record for a specific cattle"""

    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':
        # Get form data
        health_status = request.POST.get('health_status')
        symptoms = request.POST.get('symptoms')
        treatment = request.POST.get('treatment')
        notes = request.POST.get('notes')

        # Validate form data
        if not health_status:
            messages.error(request, 'Health status is required!')
            return render(request, 'health/health_record_form.html', {
                'cattle': cattle,
                'form_data': request.POST,
            })
        
        # Create health record
        HealthRecord.objects.create(
            cattle=cattle,
            health_status=health_status,
            symptoms=symptoms if symptoms else None,
            treatment=treatment if treatment else None,
            notes=notes if notes else None,
        )
        
        # Update cattle current health status
        cattle.health_status = health_status
        cattle.save()

        # Create an event
        CattleEvent.objects.create(
            cattle=cattle,
            event_type='HEALTH_CHECK',
            description=f'Health check: {health_status}',
            location=cattle.location,
            notes=f'Symptoms: {symptoms}' if symptoms else '',
        )

        messages.success(request, f'Health record added for {cattle.gov_tag}!')
        return redirect('health:cattle_detail', cattle_id=cattle.id)

    # GET request - show empty form (INDENTED INSIDE THE FUNCTION)
    context = {
        'cattle': cattle,
        'health_status_choices': HealthRecord.HEALTH_STATUS_CHOICES,
        'form_data': {},
    }
    return render(request, 'health/health_record_form.html', context)

@login_required
def health_dashboard(request):
    """Health overview page with all health data"""
    
    # Health records
    health_records = HealthRecord.objects.select_related('cattle').order_by('-record_date')[:50]
    
    # Sick cattle
    sick_cattle = Cattle.objects.filter(health_status='Sick')
    under_treatment = Cattle.objects.filter(health_status='Under Treatment')
    
    # Pregnant
    pregnant_count = PregnancyRecord.objects.filter(
        pregnancy_status__in=['SUSPECTED', 'CONFIRMED']
    ).count()
    
    # Vaccinations due
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    vaccines_due = Vaccination.objects.filter(
        next_due_date__gte=today,
        next_due_date__lte=next_week
    ).select_related('cattle', 'vaccine')
    vaccines_due_count = vaccines_due.count()
    
    # Weight records
    weight_records = WeightRecord.objects.select_related('cattle').order_by('-record_date')[:50]
    
    # Pregnancies
    pregnancies = PregnancyRecord.objects.filter(
        pregnancy_status__in=['SUSPECTED', 'CONFIRMED']
    ).select_related('cattle').order_by('expected_calving_date')
    
    # Vaccinations
    vaccinations = Vaccination.objects.select_related('cattle', 'vaccine').order_by('-date_administered')[:50]
    
    # All cattle for dropdown
    all_cattle = Cattle.objects.all().order_by('gov_tag')
    
    context = {
        'health_records': health_records,
        'sick_cattle': sick_cattle,
        'sick_count': sick_cattle.count(),
        'under_treatment': under_treatment,
        'under_treatment_count': under_treatment.count(),
        'pregnant_count': pregnant_count,
        'vaccines_due_count': vaccines_due_count,
        'weight_records': weight_records,
        'pregnancies': pregnancies,
        'vaccinations': vaccinations,
        'all_cattle': all_cattle,
    }
    return render(request, 'health/health_dashboard.html', context)

@login_required
def health_record_edit(request, record_id):
    """Edit a health record"""
    
    record = get_object_or_404(HealthRecord, id=record_id)
    cattle = record.cattle
    
    if request.method == 'POST':
        # Get form data
        health_status = request.POST.get('health_status')
        symptoms = request.POST.get('symptoms')
        treatment = request.POST.get('treatment')
        notes = request.POST.get('notes')
        
        if not health_status:
            messages.error(request, 'Health status is required!')
            return render(request, 'health/health_record_edit.html', {
                'record': record,
                'cattle': cattle,
                'form_data': request.POST,
            })
        
        # Update record
        record.health_status = health_status
        record.symptoms = symptoms if symptoms else None
        record.treatment = treatment if treatment else None
        record.notes = notes if notes else None
        record.save()
        
        # Update cattle's current health status if this is the latest record
        latest = HealthRecord.objects.filter(cattle=cattle).order_by('-record_date').first()
        if latest and latest.id == record.id:
            cattle.health_status = health_status
            cattle.save()
        
        messages.success(request, f'Health record updated for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    # GET request - show form with existing data
    context = {
        'record': record,
        'cattle': cattle,
        'health_status_choices': HealthRecord.HEALTH_STATUS_CHOICES,
        'form_data': {
            'health_status': record.health_status,
            'symptoms': record.symptoms,
            'treatment': record.treatment,
            'notes': record.notes,
        },
    }
    return render(request, 'health/health_record_edit.html', context)

@login_required
def health_record_delete(request, record_id):
    """Delete a health record"""
    
    record = get_object_or_404(HealthRecord, id=record_id)
    cattle = record.cattle
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, f'Health record deleted for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'record': record,
        'cattle': cattle,
        'record_type': 'Health Record',
    }
    return render(request, 'health/record_confirm_delete.html', context)

@login_required
def vaccination_add(request, cattle_id):
    """Add a vaccination for a specific cattle"""
    
    cattle = get_object_or_404(Cattle, id=cattle_id)
    
    if request.method == 'POST':
        vaccine_id = request.POST.get('vaccine_id')
        date_administered = request.POST.get('date_administered')
        next_due_date = request.POST.get('next_due_date')
        batch_number = request.POST.get('batch_number')
        dosage = request.POST.get('dosage')
        veterinarian = request.POST.get('veterinarian')
        notes = request.POST.get('notes')
        
        if not vaccine_id or not date_administered:
            messages.error(request, 'Vaccine and date are required!')
            return render(request, 'health/vaccination_add.html', {
                'cattle': cattle,
                'vaccines': Vaccine.objects.all(),
                'form_data': request.POST,
            })
        
        Vaccination.objects.create(
            cattle=cattle,
            vaccine_id=vaccine_id,
            date_administered=date_administered,
            next_due_date=next_due_date if next_due_date else None,
            batch_number=batch_number if batch_number else None,
            dosage=dosage if dosage else None,
            veterinarian=veterinarian if veterinarian else None,
            notes=notes if notes else None,
        )
        
        messages.success(request, f'Vaccination added for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'cattle': cattle,
        'vaccines': Vaccine.objects.all(),
        'form_data': {},
    }
    return render(request, 'health/vaccination_add.html', context)

@login_required
def vaccination_edit(request, vax_id):
    """Edit a vaccination record"""
    
    vax = get_object_or_404(Vaccination, id=vax_id)
    cattle = vax.cattle
    
    if request.method == 'POST':
        vaccine_id = request.POST.get('vaccine_id')
        date_administered = request.POST.get('date_administered')
        next_due_date = request.POST.get('next_due_date')
        batch_number = request.POST.get('batch_number')
        dosage = request.POST.get('dosage')
        veterinarian = request.POST.get('veterinarian')
        notes = request.POST.get('notes')
        
        if not vaccine_id or not date_administered:
            messages.error(request, 'Vaccine and date are required!')
            return render(request, 'health/vaccination_edit.html', {
                'vax': vax,
                'cattle': cattle,
                'vaccines': Vaccine.objects.all(),
                'form_data': request.POST,
            })
        
        vax.vaccine_id = vaccine_id
        vax.date_administered = date_administered
        vax.next_due_date = next_due_date if next_due_date else None
        vax.batch_number = batch_number if batch_number else None
        vax.dosage = dosage if dosage else None
        vax.veterinarian = veterinarian if veterinarian else None
        vax.notes = notes if notes else None
        vax.save()
        
        messages.success(request, f'Vaccination updated for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'vax': vax,
        'cattle': cattle,
        'vaccines': Vaccine.objects.all(),
        'form_data': {
            'vaccine_id': vax.vaccine.id,
            'date_administered': vax.date_administered,
            'next_due_date': vax.next_due_date,
            'batch_number': vax.batch_number,
            'dosage': vax.dosage,
            'veterinarian': vax.veterinarian,
            'notes': vax.notes,
        },
    }
    return render(request, 'health/vaccination_edit.html', context)

@login_required
def vaccination_delete(request, vax_id):
    """Delete a vaccination record"""
    
    vax = get_object_or_404(Vaccination, id=vax_id)
    cattle = vax.cattle
    
    if request.method == 'POST':
        vax.delete()
        messages.success(request, f'Vaccination deleted for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'record': vax,
        'cattle': cattle,
        'record_type': 'Vaccination',
        'detail': f'{vax.vaccine.name} on {vax.date_administered}',
    }
    return render(request, 'health/record_confirm_delete.html', context)





# Create your views here.
