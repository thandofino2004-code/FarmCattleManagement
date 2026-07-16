from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.db.models import Count, Q
from datetime import datetime, timedelta
from cattle.models import Cattle, CattleEvent
from .models import WeightRecord
from django.contrib.auth.decorators import login_required

@login_required
def weight_dashboard(request):
    """Weight tracking dashboard with chart data"""
    
    #weight records
    weight_records = WeightRecord.objects.select_related('cattle').order_by('-record_date')[:50]
    
    # Getting all cattle
    all_cattle = Cattle.objects.all().order_by('gov_tag')
    
    # all the  weight records for chart (grouped by cattle)
    chart_data = WeightRecord.objects.select_related('cattle').order_by('cattle', 'record_date')[:100]
    
    context = {
        'weight_records': weight_records,
        'all_cattle': all_cattle,
        'chart_data': chart_data,
    }
    return render(request, 'weight/weight_dashboard.html', context)

@login_required
def weight_record_add(request):
    """Add a weight record"""
    
    if request.method == 'POST':
        cattle_id = request.POST.get('cattle_id')
        weight_kg = request.POST.get('weight_kg')
        notes = request.POST.get('notes')
        
        if not cattle_id or not weight_kg:
            messages.error(request, 'Please select a cattle and enter weight!')
            return redirect('weight:weight_dashboard')
        
        cattle = get_object_or_404(Cattle, id=cattle_id)
        
        WeightRecord.objects.create(
            cattle=cattle,
            weight_kg=weight_kg,
            notes=notes if notes else None,
        )
        
        messages.success(request, f'Weight record added for {cattle.gov_tag}!')
        return redirect('weight:weight_dashboard')
    
    return redirect('weight:weight_dashboard')







@login_required
def weight_record_edit(request, weight_id):
    """Edit a weight record"""
    
    weight = get_object_or_404(WeightRecord, id=weight_id)
    cattle = weight.cattle
    
    if request.method == 'POST':
        weight_kg = request.POST.get('weight_kg')
        record_date = request.POST.get('record_date')
        notes = request.POST.get('notes')
        
        if not weight_kg or not record_date:
            messages.error(request, 'Weight and date are required!')
            return render(request, 'weight/weight_record_edit.html', {
                'weight': weight,
                'cattle': cattle,
                'form_data': request.POST,
            })
        
        weight.weight_kg = weight_kg
        weight.record_date = record_date
        weight.notes = notes if notes else None
        weight.save()
        
        messages.success(request, f' Weight record updated for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'weight': weight,
        'cattle': cattle,
        'form_data': {
            'weight_kg': weight.weight_kg,
            'record_date': weight.record_date,
            'notes': weight.notes,
        },
    }
    return render(request, 'weight/weight_record_edit.html', context)


@login_required
def weight_record_delete(request, weight_id):
    """Delete a weight record"""
    
    weight = get_object_or_404(WeightRecord, id=weight_id)
    cattle = weight.cattle
    
    if request.method == 'POST':
        weight.delete()
        messages.success(request, f'Weight record deleted for {cattle.gov_tag}!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    context = {
        'record': weight,
        'cattle': cattle,
        'record_type': 'Weight Record',
        'detail': f'{weight.weight_kg} kg on {weight.record_date}',
    }
    return render(request, 'weight/weight_record_confirm_delete.html', context)




# Create your views here.
