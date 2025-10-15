from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Amenity, Course, CourseImage


class AmenityModelTest(TestCase):
    def setUp(self):
        self.amenity = Amenity.objects.create(name='Driving Range')
    
    def test_amenity_creation(self):
        self.assertEqual(self.amenity.name, 'Driving Range')
        self.assertIsNotNone(self.amenity.created_at)
    
    def test_amenity_str(self):
        self.assertEqual(str(self.amenity), 'Driving Range')


class CourseModelTest(TestCase):
    def setUp(self):
        self.amenity1 = Amenity.objects.create(name='Pro Shop')
        self.amenity2 = Amenity.objects.create(name='Restaurant')
        
        self.course = Course.objects.create(
            name='Test Golf Course',
            address='123 Golf Lane',
            city='Testville',
            state='CA',
            zip_code='90210',
            phone_number='555-1234',
            website='https://testgolf.com',
            cost='$50',
            status='approved'
        )
        self.course.amenities.add(self.amenity1, self.amenity2)
    
    def test_course_creation(self):
        self.assertEqual(self.course.name, 'Test Golf Course')
        self.assertEqual(self.course.city, 'Testville')
        self.assertEqual(self.course.state, 'CA')
        self.assertEqual(self.course.status, 'approved')
    
    def test_course_str(self):
        expected = 'Test Golf Course - Testville, CA'
        self.assertEqual(str(self.course), expected)
    
    def test_course_amenities(self):
        self.assertEqual(self.course.amenities.count(), 2)
        self.assertIn(self.amenity1, self.course.amenities.all())
        self.assertIn(self.amenity2, self.course.amenities.all())
    
    def test_course_default_status(self):
        new_course = Course.objects.create(
            name='New Course',
            address='456 New St',
            city='Newtown',
            state='NY'
        )
        self.assertEqual(new_course.status, 'pending')


class CourseListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.approved_course = Course.objects.create(
            name='Approved Course',
            address='123 Main St',
            city='Los Angeles',
            state='CA',
            status='approved'
        )
        
        self.pending_course = Course.objects.create(
            name='Pending Course',
            address='456 Elm St',
            city='San Francisco',
            state='CA',
            status='pending'
        )
    
    def test_course_list_view_status(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_course_list_shows_approved_only(self):
        response = self.client.get(reverse('course_list'))
        self.assertContains(response, 'Approved Course')
        self.assertNotContains(response, 'Pending Course')
    
    def test_course_list_search(self):
        response = self.client.get(reverse('course_list'), {'search': 'Approved'})
        self.assertContains(response, 'Approved Course')
    
    def test_course_list_state_filter(self):
        ny_course = Course.objects.create(
            name='NY Course',
            address='789 Broadway',
            city='New York',
            state='NY',
            status='approved'
        )
        
        response = self.client.get(reverse('course_list'), {'state': 'NY'})
        self.assertContains(response, 'NY Course')
        self.assertNotContains(response, 'Approved Course')


class CourseDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.course = Course.objects.create(
            name='Detail Course',
            address='123 Detail St',
            city='Detailville',
            state='CA',
            phone_number='555-9999',
            website='https://detail.com',
            status='approved'
        )
    
    def test_course_detail_view_status(self):
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_course_detail_shows_course_info(self):
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertContains(response, 'Detail Course')
        self.assertContains(response, 'Detailville')
    
    def test_course_detail_pending_course_404(self):
        pending_course = Course.objects.create(
            name='Pending',
            address='456 Pending St',
            city='Pendingtown',
            state='CA',
            status='pending'
        )
        
        response = self.client.get(reverse('course_detail', args=[pending_course.id]))
        self.assertEqual(response.status_code, 404)


class AdminActionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        
        self.course1 = Course.objects.create(
            name='Course 1',
            address='123 St',
            city='City',
            state='CA',
            status='pending'
        )
        
        self.course2 = Course.objects.create(
            name='Course 2',
            address='456 St',
            city='City',
            state='CA',
            status='pending'
        )
    
    def test_admin_can_login(self):
        response = self.client.post(reverse('admin_login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)
        
    def test_admin_dashboard_accessible(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_django_admin_accessible(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/django-admin/')
        self.assertEqual(response.status_code, 200)


class IntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.amenity1 = Amenity.objects.create(name='Golf Cart')
        self.amenity2 = Amenity.objects.create(name='Clubhouse')
        
        self.course = Course.objects.create(
            name='Integration Test Course',
            address='999 Integration Blvd',
            city='Integration City',
            state='TX',
            zip_code='75001',
            cost='$100',
            rating_google='4.5',
            status='approved'
        )
        self.course.amenities.add(self.amenity1, self.amenity2)
    
    def test_full_workflow(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Course')
        
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration City')
        self.assertContains(response, 'TX')
        self.assertContains(response, '$100')
    
    def test_amenity_filtering(self):
        response = self.client.get(reverse('course_list'), {'amenity': [self.amenity1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Course')
