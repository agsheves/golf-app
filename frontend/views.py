from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from courses.models import Course, Amenity


def course_list(request):
    courses = Course.objects.filter(status='approved')
    
    search_query = request.GET.get('search', '')
    state_filter = request.GET.get('state', '')
    amenity_filter = request.GET.getlist('amenity')
    
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) | 
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    if state_filter:
        courses = courses.filter(state=state_filter)
    
    if amenity_filter:
        for amenity_id in amenity_filter:
            courses = courses.filter(amenities__id=amenity_id)
    
    states = Course.objects.filter(status='approved').values_list('state', flat=True).distinct().order_by('state')
    amenities = Amenity.objects.all()
    
    context = {
        'courses': courses,
        'states': states,
        'amenities': amenities,
        'search_query': search_query,
        'selected_state': state_filter,
        'selected_amenities': [int(a) for a in amenity_filter] if amenity_filter else [],
    }
    
    return render(request, 'frontend/course_list.html', context)


def course_detail(request, course_id):
    if request.user.is_authenticated and request.user.is_staff:
        course = get_object_or_404(Course, id=course_id)
    else:
        course = get_object_or_404(Course, id=course_id, status='approved')
    
    context = {
        'course': course,
    }
    
    if request.htmx:
        return render(request, 'frontend/course_detail_modal.html', context)
    
    return render(request, 'frontend/course_detail.html', context)
