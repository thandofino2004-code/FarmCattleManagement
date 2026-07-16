from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Cattle, CattleEvent
from health.models import HealthRecord, Vaccination
from breeding.models import PregnancyRecord 
from weight.models import WeightRecord
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    total_cattle = Cattle.objects.count()
    active_cattle = Cattle.objects.filter(current_status='Active').count()
    missing_cattle = Cattle.objects.filter(current_status='Missing').count()

    healthy_count = Cattle.objects.filter(health_status='Healthy').count()
    sick_count = Cattle.objects.filter(health_status='Sick').count()

    healthy_percentage = round((healthy_count / total_cattle * 100), 1) if total_cattle > 0 else 0
    

    pregnant_count = PregnancyRecord.objects.filter(
        pregnancy_status__in=['SUSPECTED', 'CONFIRMED']
    ).count()

    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    vaccines_due = Vaccination.objects.filter(
        next_due_date__gte=today,
       next_due_date__lte=next_week
 ).select_related('cattle', 'vaccine')
    vaccines_due_count = vaccines_due.count()

    breed_counts = Cattle.objects.values('breed').annotate(
       count=Count('id')
        ).order_by('-count')
    max_breed_count = breed_counts[0]['count'] if breed_counts else 1
    
    recent_events = CattleEvent.objects.select_related('cattle').order_by('-event_date')[:10]
      #will create a task model later 
    tasks_due = [
        {'id': 1, 'title': 'Fix Fence Line West-3', 'priority': 'high', 'due_in_days': None},
        {'id': 2, 'title': 'Deworming Batch A2', 'priority': 'medium', 'due_in_days': 2},
        {'id': 3, 'title': 'Inventory Audit', 'priority': 'low', 'due_in_days': None, 'recurrence': 'Monthly'},
    ]
    
    pending_task_count = len(tasks_due)

    context = {

        'total_cattle': total_cattle,
        'active_cattle': active_cattle,
        'missing_cattle': missing_cattle,
        'healthy_count': healthy_count,
        'healthy_percentage': healthy_percentage,
        'sick_count': sick_count,
        'pregnant_count': pregnant_count,
        'vaccines_due_count': vaccines_due_count,
        'vaccines_due': vaccines_due,
        'breed_counts': breed_counts,
        'max_breed_count': max_breed_count,
        'recent_events': recent_events,
        'tasks_due': tasks_due,
        'pending_task_count': pending_task_count,
        'farm_name': 'DEBAITS Farm',
       
    }
    
    #
    return render(request, 'cattle/dashboard.html', context)

@login_required  
def cattle_list(request):
    """Display all cattle with search and filter options"""
    
    # Start with all cattle
    cattle = Cattle.objects.all()
    
    # Get filter parameters from URL
    status_filter = request.GET.get('status', '')
    breed_filter = request.GET.get('breed', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if status_filter:
        cattle = cattle.filter(current_status=status_filter)
    if breed_filter:
        cattle = cattle.filter(breed=breed_filter)
    if search_query:
        cattle = cattle.filter(
            Q(gov_tag__icontains=search_query) |
            Q(ear_tag__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    # Get all breeds for filter dropdown
    all_breeds = Cattle.objects.values_list('breed', flat=True).distinct().order_by('breed')
    
    context = {
        'cattle': cattle,
        'all_breeds': all_breeds,
        'current_status': status_filter,
        'current_breed': breed_filter,
        'search_query': search_query,
        'status_choices': Cattle.STATUS_CHOICES,
    }
    
    return render(request, 'cattle/cattle_list.html', context)

@login_required
def cattle_add(request):
    """Add a new cattle record"""
    
    if request.method == 'POST':
        # Get form data
        
        gov_tag = request.POST.get('gov_tag')
        ear_tag = request.POST.get('ear_tag')
        name = request.POST.get('name')
        breed = request.POST.get('breed')
        sex = request.POST.get('sex')
        date_of_birth = request.POST.get('date_of_birth')
        colour = request.POST.get('colour')
        health_status = request.POST.get('health_status')
        current_status = request.POST.get('current_status')
        location = request.POST.get('location')
        mother_gov_tag = request.POST.get('mother_gov_tag')
        father_gov_tag = request.POST.get('father_gov_tag')
        purchase_date = request.POST.get('purchase_date')
        purchase_price = request.POST.get('purchase_price')
        source_supplier = request.POST.get('source_supplier')
        notes = request.POST.get('notes')
        photo = request.FILES.get('photo')
        
        # Validate required fields
        if not gov_tag:
            messages.error(request, 'Government Tag is required!')
            return render(request, 'cattle/cattle_form.html', {
                'form_data': request.POST,
                'action': 'Add'
            })
        
        # Check if gov_tag already exists
        if Cattle.objects.filter(gov_tag=gov_tag).exists():
            messages.error(request, f'Government Tag "{gov_tag}" already exists!')
            return render(request, 'cattle/cattle_form.html', {
                'form_data': request.POST,
                'action': 'Add'
            })
        
        # Create the cattle record
        cattle = Cattle.objects.create(
            gov_tag=gov_tag,
            ear_tag=ear_tag if ear_tag else None,
            name=name if name else None,
            breed=breed,
            sex=sex,
            date_of_birth=date_of_birth if date_of_birth else None,
            colour=colour if colour else None,
            health_status=health_status if health_status else 'Healthy',
            current_status=current_status if current_status else 'Active',
            location=location if location else 'Kraal 1',
            mother_gov_tag=mother_gov_tag if mother_gov_tag else None,
            father_gov_tag=father_gov_tag if father_gov_tag else None,
            purchase_date=purchase_date if purchase_date else None,
            purchase_price=purchase_price if purchase_price else None,
            source_supplier=source_supplier if source_supplier else None,
            notes=notes if notes else None,
            photo=photo,
        )
        
        # Create an event for this cattle
        CattleEvent.objects.create(
            cattle=cattle,
            event_type='PURCHASED',
            description=f'{cattle.gov_tag} registered in system',
            location=cattle.location,
        )
        
        messages.success(request, f'Cattle {cattle.gov_tag} registered successfully!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    # GET request - show empty form
    context = {
        'action': 'Add',
        'breed_choices': Cattle.BREED_CHOICES,
        'sex_choices': Cattle.SEX_CHOICES,
        'colour_choices': Cattle.COLOUR_CHOICES,
        'health_status_choices': Cattle.HEALTH_STATUS_CHOICES,
        'status_choices': Cattle.STATUS_CHOICES,
        'form_data': {},
    }
    return render(request, 'cattle/cattle_form.html', context)


@login_required
def cattle_detail(request, cattle_id):
    """View detailed information about a specific cattle"""
    
    cattle = get_object_or_404(Cattle, id=cattle_id)
    
    # Get related records
    health_records = cattle.health_records.all()[:10]
    vaccinations = cattle.vaccinations.all()[:10]
    pregnancies = cattle.pregnancies.all()[:10]
    events = cattle.events.all()[:20]
    
    # Get parents
    parents = []
    if cattle.mother_gov_tag:
        mother = Cattle.objects.filter(gov_tag=cattle.mother_gov_tag).first()
        if mother:
            parents.append({'relation': 'Mother', 'cattle': mother})
    if cattle.father_gov_tag:
        father = Cattle.objects.filter(gov_tag=cattle.father_gov_tag).first()
        if father:
            parents.append({'relation': 'Father', 'cattle': father})
    
    # Get children
    children = Cattle.objects.filter(mother_gov_tag=cattle.gov_tag) | Cattle.objects.filter(father_gov_tag=cattle.gov_tag)
    
    context = {
        'cattle': cattle,
        'health_records': health_records,
        'vaccinations': vaccinations,
        'pregnancies': pregnancies,
        'events': events,
        'parents': parents,
        'children': children,
        'age': cattle.age,
    }
    
    return render(request, 'cattle/cattle_detail.html', context)

@login_required
def cattle_edit(request, cattle_id):
    """Edit an existing cattle record"""
    
    cattle = get_object_or_404(Cattle, id=cattle_id)
    
    if request.method == 'POST':
        # Get form data
        gov_tag = request.POST.get('gov_tag')
        ear_tag = request.POST.get('ear_tag')
        name = request.POST.get('name')
        breed = request.POST.get('breed')
        sex = request.POST.get('sex')
        date_of_birth = request.POST.get('date_of_birth')
        colour = request.POST.get('colour')
        health_status = request.POST.get('health_status')
        current_status = request.POST.get('current_status')
        location = request.POST.get('location')
        mother_gov_tag = request.POST.get('mother_gov_tag')
        father_gov_tag = request.POST.get('father_gov_tag')
        purchase_date = request.POST.get('purchase_date')
        purchase_price = request.POST.get('purchase_price')
        source_supplier = request.POST.get('source_supplier')
        notes = request.POST.get('notes')
        photo = request.FILES.get('photo')
        
        # Check if gov_tag already exists (excluding this cattle)
        if Cattle.objects.filter(gov_tag=gov_tag).exclude(id=cattle_id).exists():
            messages.error(request, f'Government Tag "{gov_tag}" already exists!')
            return render(request, 'cattle/cattle_form.html', {
                'form_data': request.POST,
                'action': 'Edit',
                'cattle': cattle,
            })
        
        # Update the cattle record
        cattle.gov_tag = gov_tag
        cattle.ear_tag = ear_tag if ear_tag else None
        cattle.name = name if name else None
        cattle.breed = breed
        cattle.sex = sex
        cattle.date_of_birth = date_of_birth if date_of_birth else None
        cattle.colour = colour if colour else None
        cattle.health_status = health_status if health_status else 'Healthy'
        cattle.current_status = current_status if current_status else 'Active'
        cattle.location = location if location else 'Kraal 1'
        cattle.mother_gov_tag = mother_gov_tag if mother_gov_tag else None
        cattle.father_gov_tag = father_gov_tag if father_gov_tag else None
        cattle.purchase_date = purchase_date if purchase_date else None
        cattle.purchase_price = purchase_price if purchase_price else None
        cattle.source_supplier = source_supplier if source_supplier else None
        cattle.notes = notes if notes else None
        
        # Only update photo if a new one was uploaded
        if photo:
            cattle.photo = photo
        
        cattle.save()
        
        messages.success(request, f' Cattle {cattle.gov_tag} updated successfully!')
        return redirect('cattle:cattle_detail', cattle_id=cattle.id)
    
    # GET request - show form with existing data
    context = {
        'action': 'Edit',
        'cattle': cattle,
        'breed_choices': Cattle.BREED_CHOICES,
        'sex_choices': Cattle.SEX_CHOICES,
        'colour_choices': Cattle.COLOUR_CHOICES,
        'health_status_choices': Cattle.HEALTH_STATUS_CHOICES,
        'status_choices': Cattle.STATUS_CHOICES,
        'form_data': {
            'gov_tag': cattle.gov_tag,
            'ear_tag': cattle.ear_tag,
            'name': cattle.name,
            'breed': cattle.breed,
            'sex': cattle.sex,
            'date_of_birth': cattle.date_of_birth,
            'colour': cattle.colour,
            'health_status': cattle.health_status,
            'current_status': cattle.current_status,
            'location': cattle.location,
            'mother_gov_tag': cattle.mother_gov_tag,
            'father_gov_tag': cattle.father_gov_tag,
            'purchase_date': cattle.purchase_date,
            'purchase_price': cattle.purchase_price,
            'source_supplier': cattle.source_supplier,
            'notes': cattle.notes,
        },
    }
    return render(request, 'cattle/cattle_form.html', context)

@login_required
def cattle_delete(request, cattle_id):

    """Delete a cattle record (with confirmation)"""
    
    cattle = get_object_or_404(Cattle, id=cattle_id)
    
    if request.method == 'POST':
        # Save the gov_tag for the success message
        gov_tag = cattle.gov_tag
        
        # Delete the cattle
        cattle.delete()
        
        messages.success(request, f'Cattle {gov_tag} has been deleted successfully!')
        return redirect('cattle:cattle_list')
    
    # GET request - show confirmation page
    context = {
        'cattle': cattle,
    }
    return render(request, 'cattle/cattle_confirm_delete.html', context)

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
        
        