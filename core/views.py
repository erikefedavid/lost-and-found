# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import]
from django.db.models import Q
from datetime import datetime
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm, LostItemForm, FoundItemForm, ClaimForm
from .models import LostItem, FoundItem, Claim

def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    lost_items = LostItem.objects.all().order_by('-created_at')[:5]
    found_items = FoundItem.objects.filter(status='unclaimed').order_by('-created_at')[:5]
    return render(request, 'core/dashboard.html', {'lost_items': lost_items, 'found_items': found_items})

@login_required
def report_lost(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            lost_item = form.save(commit=False)
            lost_item.user = request.user
            lost_item.save()
            messages.success(request, 'Lost item reported successfully.')
            return redirect('dashboard')
    else:
        form = LostItemForm()
    return render(request, 'core/report_lost.html', {'form': form, 'title': 'Report Lost Item'})

@login_required
def report_found(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            found_item = form.save(commit=False)
            found_item.user = request.user
            found_item.save()
            messages.success(request, 'Found item reported successfully.')
            return redirect('dashboard')
    else:
        form = FoundItemForm()
    return render(request, 'core/report_found.html', {'form': form, 'title': 'Report Found Item'})

@login_required
def browse(request):
    item_type = request.GET.get('type', 'lost') # default to 'lost'
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if item_type == 'found':
        items = FoundItem.objects.filter(status='unclaimed')
    else:
        items = LostItem.objects.all()

    if query:
        items = items.filter(Q(item_name__icontains=query) | Q(description__icontains=query))
    if category:
        items = items.filter(category__icontains=category)
    if location:
        items = items.filter(location__icontains=location)
    
    if date_from:
        try:
            parsed_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            if item_type == 'found':
                items = items.filter(date_found__gte=parsed_from)
            else:
                items = items.filter(date_lost__gte=parsed_from)
        except ValueError:
            pass
            
    if date_to:
        try:
            parsed_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            if item_type == 'found':
                items = items.filter(date_found__lte=parsed_to)
            else:
                items = items.filter(date_lost__lte=parsed_to)
        except ValueError:
            pass

    items = items.order_by('-created_at')

    context = {
        'items': items,
        'item_type': item_type,
        'query': query,
        'category': category,
        'location': location,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'core/browse.html', context)

@login_required
def item_detail(request, item_type, item_id):
    if item_type == 'found':
        item = get_object_or_404(FoundItem, id=item_id)
        
        existing_claim = None
        if request.user.is_authenticated:
            existing_claim = Claim.objects.filter(found_item=item, user=request.user).first()
        
        form = None
        if request.user.is_authenticated and not existing_claim:
            if request.method == 'POST':
                form = ClaimForm(request.POST, request.FILES)
                if form.is_valid():
                    claim = form.save(commit=False)
                    claim.found_item = item
                    claim.user = request.user
                    claim.save()
                    messages.success(request, 'Claim submitted successfully. Administrators will review it.')
                    return redirect('item_detail', item_type=item_type, item_id=item_id)
            else:
                form = ClaimForm()
            
        context = {
            'item': item,
            'item_type': item_type,
            'form': form,
            'existing_claim': existing_claim
        }
    else:
        item = get_object_or_404(LostItem, id=item_id)
        context = {
            'item': item,
            'item_type': item_type
        }
        
    return render(request, 'core/item_detail.html', context)

@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    # Mark all as read when viewing the page
    notifications.update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifications})
