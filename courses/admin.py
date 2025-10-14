from django.contrib import admin
from django.utils import timezone
from .models import Amenity, Course, ImportedCourse, CourseImage


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class CourseImageInline(admin.TabularInline):
    model = CourseImage
    extra = 1
    fields = ['image', 'caption', 'is_primary']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'status', 'reviewed_by', 'reviewed_at', 'created_at']
    list_filter = ['status', 'state', 'reviewed_at']
    search_fields = ['name', 'city', 'state', 'address']
    filter_horizontal = ['amenities']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CourseImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city', 'state', 'zip_code')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'website', 'booking_link')
        }),
        ('Course Information', {
            'fields': ('course_length_forward', 'course_length_tips', 'course_slope', 'scorecard', 'thumbnail')
        }),
        ('Pricing', {
            'fields': ('cost', 'rent_cart_cost')
        }),
        ('Ratings', {
            'fields': ('rating_google', 'rating_golf_now', 'rating_grint')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('Moderation', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'moderation_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_courses', 'reject_courses', 'mark_as_pending']
    
    def approve_courses(self, request, queryset):
        count = queryset.update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{count} course(s) approved successfully.')
    approve_courses.short_description = "Approve selected courses"
    
    def reject_courses(self, request, queryset):
        count = queryset.update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{count} course(s) rejected.')
    reject_courses.short_description = "Reject selected courses"
    
    def mark_as_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f'{count} course(s) marked as pending review.')
    mark_as_pending.short_description = "Mark as pending review"


@admin.register(ImportedCourse)
class ImportedCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'source', 'processed', 'created_at']
    list_filter = ['source', 'processed', 'created_at']
    search_fields = ['name', 'city', 'state']
    readonly_fields = ['raw_data', 'created_at']
    
    fieldsets = (
        ('Source Information', {
            'fields': ('source', 'source_url', 'raw_data')
        }),
        ('Extracted Data', {
            'fields': ('name', 'address', 'city', 'state', 'phone_number', 'website')
        }),
        ('Processing', {
            'fields': ('processed', 'approved_course', 'created_at')
        }),
    )
    
    actions = ['create_courses_from_imports']
    
    def create_courses_from_imports(self, request, queryset):
        count = 0
        for imported in queryset.filter(processed=False):
            course = Course.objects.create(
                name=imported.name,
                address=imported.address,
                city=imported.city,
                state=imported.state,
                phone_number=imported.phone_number,
                website=imported.website,
                status='pending'
            )
            imported.processed = True
            imported.approved_course = course
            imported.save()
            count += 1
        
        self.message_user(request, f'{count} imported course(s) created as pending review.')
    create_courses_from_imports.short_description = "Create courses from selected imports"


@admin.register(CourseImage)
class CourseImageAdmin(admin.ModelAdmin):
    list_display = ['course', 'caption', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['course__name', 'caption']
