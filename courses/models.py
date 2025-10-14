from django.db import models
from django.contrib.auth.models import User


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suppressed', 'Suppressed'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True, blank=True)
    state = models.CharField(max_length=50, db_index=True, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(max_length=500, blank=True)
    
    rating_google = models.CharField(max_length=20, blank=True)
    rating_golf_now = models.CharField(max_length=20, blank=True)
    rating_grint = models.CharField(max_length=20, blank=True)
    
    cost = models.CharField(max_length=100, blank=True)
    rent_cart_cost = models.CharField(max_length=100, blank=True)
    
    course_length_forward = models.CharField(max_length=50, blank=True)
    course_length_tips = models.CharField(max_length=50, blank=True)
    course_slope = models.CharField(max_length=50, blank=True)
    
    scorecard = models.URLField(max_length=500, blank=True)
    booking_link = models.URLField(max_length=500, blank=True)
    thumbnail = models.URLField(max_length=500, blank=True)
    
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='courses')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_courses')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'state']),
            models.Index(fields=['city', 'state']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"


class ImportedCourse(models.Model):
    SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('scraper', 'Web Scraper'),
        ('api', 'API Import'),
    ]

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='scraper')
    source_url = models.URLField(max_length=1000, blank=True)
    raw_data = models.JSONField()
    
    name = models.CharField(max_length=255, db_index=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(max_length=500, blank=True)
    
    processed = models.BooleanField(default=False)
    approved_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='imports')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Import: {self.name} ({self.source})"


class CourseImage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='course_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"Image for {self.course.name}"
