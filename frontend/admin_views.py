import subprocess
import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from courses.models import Course, Amenity
from django.db.models import Q

US_STATES = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
    'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
    'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
    'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
    'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
    'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
    'West Virginia', 'Wisconsin', 'Wyoming',
]


def is_staff_user(user):
    return user.is_staff


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'frontend/admin_login.html')


@login_required
def admin_logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('course_list')


@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    courses = Course.objects.all().order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    state_filter = request.GET.get('state', '')
    
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) | 
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    if status_filter:
        courses = courses.filter(status=status_filter)
    
    if state_filter:
        courses = courses.filter(state=state_filter)
    
    states = Course.objects.values_list('state', flat=True).distinct().order_by('state')
    amenities = Amenity.objects.all()
    
    context = {
        'courses': courses,
        'states': states,
        'amenities': amenities,
        'search_query': search_query,
        'selected_status': status_filter,
        'selected_state': state_filter,
        'status_choices': Course.STATUS_CHOICES,
        'scraper_states': US_STATES,
    }
    
    return render(request, 'frontend/admin_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_POST
def toggle_course_approval(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if course.status == 'approved':
        course.status = 'pending'
    else:
        course.status = 'approved'
        course.reviewed_by = request.user
        from django.utils import timezone
        course.reviewed_at = timezone.now()
    
    course.save()
    
    return JsonResponse({
        'success': True,
        'status': course.status,
        'status_display': course.get_status_display()
    })


@login_required
@user_passes_test(is_staff_user)
@require_POST
def reject_course(request, course_id):
    """Reject a course - keeps it in database to prevent re-scraping."""
    course = get_object_or_404(Course, id=course_id)
    
    course.status = 'rejected'
    course.reviewed_by = request.user
    from django.utils import timezone
    course.reviewed_at = timezone.now()
    
    course.save()
    
    return JsonResponse({
        'success': True,
        'status': course.status,
        'status_display': course.get_status_display()
    })


@login_required
@user_passes_test(is_staff_user)
@require_POST
def update_course_field(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    field_name = request.POST.get('field')
    field_value = request.POST.get('value', '')
    
    allowed_fields = [
        'name', 'address', 'city', 'state', 'zip_code',
        'phone_number', 'website', 'rating_google', 
        'rating_golf_now', 'rating_grint', 'cost', 
        'rent_cart_cost', 'course_length_forward', 
        'course_length_tips', 'course_slope', 'scorecard', 
        'booking_link', 'thumbnail', 'moderation_notes'
    ]
    
    if field_name in allowed_fields:
        setattr(course, field_name, field_value)
        course.save()
        return JsonResponse({'success': True, 'value': field_value})
    
    return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)


@login_required
@user_passes_test(is_staff_user)
@require_POST
def run_scraper(request):
    state = request.POST.get('state', '')
    limit = request.POST.get('limit', '5')

    if not state or state not in US_STATES:
        messages.error(request, 'Please select a valid US state.')
        return redirect('admin_dashboard')

    try:
        limit_int = int(limit)
        if limit_int < 1 or limit_int > 20:
            limit_int = 5
    except (ValueError, TypeError):
        limit_int = 5

    subprocess.Popen(
        [sys.executable, 'manage.py', 'scrape_courses', '--state', state, '--limit', str(limit_int)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    messages.success(
        request,
        f'Scraper started for {state} (limit: {limit_int}). '
        f'New courses will appear as "Pending" shortly.'
    )
    return redirect('admin_dashboard')
