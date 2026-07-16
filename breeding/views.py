from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.db.models import Count, Q
from datetime import datetime, timedelta
from cattle.models import Cattle, CattleEvent
from .models import PregnancyRecord, CalvingRecord
from django.contrib.auth.decorators import login_required

@login_required
def breeding_dashboard(request):
    """Breeding overview page"""
    
    # Get pregnant cattle
    pregnancies = PregnancyRecord.objects.filter(
        pregnancy_status__in=['SUSPECTED', 'CONFIRMED']
    ).select_related('cattle').order_by('expected_calving_date')
    
    # Get recent calvings
    calvings = CalvingRecord.objects.select_related('mother', 'calf').order_by('-calving_date')[:20]
    
    # Counts
    pregnant_count = pregnancies.count()
    calving_count = calvings.count()
    
    # Upcoming calvings (next 30 days)
    today = datetime.now().date()
    next_month = today + timedelta(days=30)
    upcoming_calvings = pregnancies.filter(
        expected_calving_date__gte=today,
        expected_calving_date__lte=next_month
    )
    
    context = {
        'pregnancies': pregnancies,
        'pregnant_count': pregnant_count,
        'calvings': calvings,
        'calving_count': calving_count,
        'upcoming_calvings': upcoming_calvings,
        'upcoming_calvings_count': upcoming_calvings.count(),
    }
    return render(request, 'breeding/breeding_dashboard.html', context)

@login_required
def pregnancy_record_add(request, cattle_id):
    """Add a pregnancy record for a specific cattle"""
    cattle = get_object_or_404(Cattle, id=cattle_id)
    
    if request.method == 'POST':
        service_date = request.POST.get('service_date')
        pregnancy_status = request.POST.get('pregnancy_status')
        expected_calving_date = request.POST.get('expected_calving_date')
        notes = request.POST.get('notes')
        
        # Validate
        if not service_date or not pregnancy_status:
            messages.error(request, 'Service date and status are required!')
            return render(request, 'breeding/pregnancy_record_form.html', {
                'cattle': cattle, 
                'form_data': request.POST,
            })
        
        # Create the record
        PregnancyRecord.objects.create(
            cattle=cattle,
            service_date=service_date,
            pregnancy_status=pregnancy_status,
            expected_calving_date=expected_calving_date if expected_calving_date else None,
            notes=notes if notes else None,
        )
        
        messages.success(request, f'Pregnancy record added for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'cattle': cattle,
        'pregnancy_status_choices': PregnancyRecord.PREGNANCY_STATUS_CHOICES,
        'form_data': {},
    }
    return render(request, 'breeding/pregnancy_record_form.html', context)

@login_required
def pregnancy_record_edit(request, pregnancy_id):
    """Edit a pregnancy record"""
    
    pregnancy = get_object_or_404(PregnancyRecord, id=pregnancy_id)
    cattle = pregnancy.cattle
    
    if request.method == 'POST':
        service_date = request.POST.get('service_date')
        pregnancy_status = request.POST.get('pregnancy_status')
        expected_calving_date = request.POST.get('expected_calving_date')
        notes = request.POST.get('notes')
        
        if not service_date or not pregnancy_status:
            messages.error(request, 'Service date and pregnancy status are required!')
            return render(request, 'breeding/pregnancy_record_form.html', {
                'pregnancy': pregnancy,
                'cattle': cattle,
                'form_data': request.POST,
            })
        
        pregnancy.service_date = service_date
        pregnancy.pregnancy_status = pregnancy_status
        pregnancy.expected_calving_date = expected_calving_date if expected_calving_date else None
        pregnancy.notes = notes if notes else None
        pregnancy.save()
        
        messages.success(request, f'✅ Pregnancy record updated for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'pregnancy': pregnancy,
        'cattle': cattle,
        'pregnancy_status_choices': PregnancyRecord.PREGNANCY_STATUS_CHOICES,
        'form_data': {
        'service_date': pregnancy.service_date,
        'pregnancy_status': pregnancy.pregnancy_status,
        'expected_calving_date': pregnancy.expected_calving_date,
        'notes': pregnancy.notes,
        },
    }
    return render(request, 'breeding/pregnancy_record_form.html', context)

@login_required
def pregnancy_record_delete(request, pregnancy_id):
    """Delete a pregnancy record"""
    
    pregnancy = get_object_or_404(PregnancyRecord, id=pregnancy_id)
    cattle = pregnancy.cattle
    
    if request.method == 'POST':
        pregnancy.delete()
        messages.success(request, f'Pregnancy record deleted for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'record': pregnancy,
        'cattle': cattle,
        'record_type': 'Pregnancy Record',
        'detail': f'Status: {pregnancy.get_pregnancy_status_display()}',
    }
    return render(request, 'breeding/pregnancy_record_confirm_delete.html', context)

@login_required
def calving_record_add(request, cattle_id):
    """Add a calving record for a specific cattle"""
    
    mother = get_object_or_404(Cattle, id=cattle_id)
    
    if request.method == 'POST':
        calf_gov_tag = request.POST.get('calf_gov_tag')
        calf_name = request.POST.get('calf_name')
        calf_breed = request.POST.get('calf_breed')
        calf_sex = request.POST.get('calf_sex')
        calving_date = request.POST.get('calving_date')
        calving_outcome = request.POST.get('calving_outcome')
        number_of_calves = request.POST.get('number_of_calves')
        notes = request.POST.get('notes')
        
        if not calf_gov_tag or not calving_date:
            messages.error(request, 'Calf Gov Tag and calving date are required!')
            return render(request, 'breeding/calving_record_form.html', {
                'mother': mother,
                'breed_choices': Cattle.BREED_CHOICES,
                'sex_choices': Cattle.SEX_CHOICES,
                'form_data': request.POST,
            })
        
        # Check if calf already exists
        if Cattle.objects.filter(gov_tag=calf_gov_tag).exists():
            messages.error(request, f'Calf with Gov Tag "{calf_gov_tag}" already exists!')
            return render(request, 'breeding/calving_record_form.html', {
                'mother': mother,
                'breed_choices': Cattle.BREED_CHOICES,
                'sex_choices': Cattle.SEX_CHOICES,
                'form_data': request.POST,
            })
        
        # Create the calf
        calf = Cattle.objects.create(
            gov_tag=calf_gov_tag,
            name=calf_name if calf_name else None,
            breed=calf_breed,
            sex=calf_sex,
            date_of_birth=calving_date,
            current_status='Active',
            health_status='Healthy',
            location=mother.location,
            mother_gov_tag=mother.gov_tag,
        )
        
        # Create calving record
        CalvingRecord.objects.create(
            mother=mother,
            calf=calf,
            calving_date=calving_date,
            calving_outcome=calving_outcome if calving_outcome else 'LIVE',
            number_of_calves=number_of_calves if number_of_calves else 1,
            notes=notes if notes else None,
        )
        
        # Update mother's pregnancy status if pregnant
        pregnancy = PregnancyRecord.objects.filter(
            cattle=mother,
            pregnancy_status__in=['SUSPECTED', 'CONFIRMED']
        ).first()
        if pregnancy:
            pregnancy.pregnancy_status = 'CALVED'
            pregnancy.actual_calving_date = calving_date
            pregnancy.save()
        
        # Create events
        CattleEvent.objects.create(
            cattle=mother,
            event_type='CALVING',
            description=f'Gave birth to {calf_gov_tag}',
            location=mother.location,
        )
        CattleEvent.objects.create(
            cattle=calf,
            event_type='BIRTH',
            description=f'Born to {mother.gov_tag}',
            location=mother.location,
        )
        
        messages.success(request, f' Calving recorded for {mother.gov_tag}! Calf {calf_gov_tag} created.')
        return redirect('cattle:cattle_detail', cattle_id=mother.id)
    
    context = {
        'mother': mother,
        'breed_choices': Cattle.BREED_CHOICES,
        'sex_choices': Cattle.SEX_CHOICES,
        'calving_outcome_choices': CalvingRecord.CALVING_OUTCOME_CHOICES,
        'form_data': {},
    }
    return render(request, 'breeding/calving_record_form.html', context)