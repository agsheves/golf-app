from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Amenity, Course, CourseImage


class Command(BaseCommand):
    help = 'Load demo golf course data and create admin user'

    def handle(self, *args, **options):
        self.stdout.write('Loading demo data...')
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@golf.com', 'admin123')
            self.stdout.write('  Created admin user (username: admin, password: admin123)')
        else:
            self.stdout.write('  Admin user already exists')
        
        amenities_data = [
            'Driving Range',
            'Putting Green',
            'Pro Shop',
            'Club Rental',
            'Golf Carts',
            'Restaurant',
            'Bar',
            'Locker Rooms',
            'Practice Facility',
            'Teaching Professional',
            'Tournament Hosting',
            'Banquet Facilities',
        ]
        
        amenities = {}
        for amenity_name in amenities_data:
            amenity, created = Amenity.objects.get_or_create(name=amenity_name)
            amenities[amenity_name] = amenity
            if created:
                self.stdout.write(f'  Created amenity: {amenity_name}')
        
        courses_data = [
            {
                'name': 'Pebble Beach Golf Links',
                'address': '1700 17 Mile Drive',
                'city': 'Pebble Beach',
                'state': 'CA',
                'zip_code': '93953',
                'phone_number': '(831) 624-3811',
                'website': 'https://www.pebblebeach.com',
                'rating_google': '4.8',
                'rating_golf_now': '4.9',
                'rating_grint': '4.8',
                'cost': '$575 - $650',
                'rent_cart_cost': 'Included',
                'course_length_forward': '6,828 yards',
                'course_length_tips': '7,040 yards',
                'course_slope': '145',
                'thumbnail': 'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Pro Shop', 'Restaurant', 'Club Rental', 'Golf Carts', 'Locker Rooms'],
            },
            {
                'name': 'Augusta National Golf Club',
                'address': '2604 Washington Road',
                'city': 'Augusta',
                'state': 'GA',
                'zip_code': '30904',
                'phone_number': '(706) 667-6000',
                'website': 'https://www.masters.com',
                'rating_google': '5.0',
                'rating_golf_now': '5.0',
                'rating_grint': '5.0',
                'cost': 'Private (Members Only)',
                'course_length_forward': '6,365 yards',
                'course_length_tips': '7,510 yards',
                'course_slope': '155',
                'thumbnail': 'https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Putting Green', 'Pro Shop', 'Restaurant', 'Bar', 'Tournament Hosting', 'Banquet Facilities'],
            },
            {
                'name': 'Torrey Pines Golf Course',
                'address': '11480 N Torrey Pines Road',
                'city': 'La Jolla',
                'state': 'CA',
                'zip_code': '92037',
                'phone_number': '(858) 452-3226',
                'website': 'https://www.sandiego.gov/park-and-recreation/golf/torreypines',
                'rating_google': '4.7',
                'rating_golf_now': '4.6',
                'rating_grint': '4.7',
                'cost': '$252 - $290',
                'rent_cart_cost': '$45',
                'course_length_forward': '6,561 yards',
                'course_length_tips': '7,765 yards',
                'course_slope': '144',
                'thumbnail': 'https://images.unsplash.com/photo-1592919505780-303950717480?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Putting Green', 'Pro Shop', 'Club Rental', 'Golf Carts', 'Restaurant'],
            },
            {
                'name': 'Bethpage Black Course',
                'address': '99 Quaker Meeting House Road',
                'city': 'Farmingdale',
                'state': 'NY',
                'zip_code': '11735',
                'phone_number': '(516) 249-0700',
                'website': 'https://www.nysparks.com/golf-courses/11/details.aspx',
                'rating_google': '4.6',
                'rating_golf_now': '4.7',
                'rating_grint': '4.6',
                'cost': '$65 - $150',
                'rent_cart_cost': '$35',
                'course_length_forward': '6,684 yards',
                'course_length_tips': '7,468 yards',
                'course_slope': '155',
                'thumbnail': 'https://images.unsplash.com/photo-1593111774240-d529f12a7e5?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Pro Shop', 'Club Rental', 'Golf Carts', 'Restaurant', 'Practice Facility'],
            },
            {
                'name': 'Pinehurst No. 2',
                'address': '1 Carolina Vista Drive',
                'city': 'Pinehurst',
                'state': 'NC',
                'zip_code': '28374',
                'phone_number': '(855) 235-8507',
                'website': 'https://www.pinehurst.com',
                'rating_google': '4.9',
                'rating_golf_now': '4.8',
                'rating_grint': '4.9',
                'cost': '$395 - $495',
                'rent_cart_cost': 'Included',
                'course_length_forward': '6,335 yards',
                'course_length_tips': '7,588 yards',
                'course_slope': '148',
                'thumbnail': 'https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Putting Green', 'Pro Shop', 'Club Rental', 'Golf Carts', 'Restaurant', 'Bar', 'Locker Rooms', 'Teaching Professional'],
            },
            {
                'name': 'Chambers Bay Golf Course',
                'address': '6320 Grandview Drive West',
                'city': 'University Place',
                'state': 'WA',
                'zip_code': '98467',
                'phone_number': '(253) 460-4653',
                'website': 'https://www.chambersbayGolf.com',
                'rating_google': '4.5',
                'rating_golf_now': '4.4',
                'rating_grint': '4.5',
                'cost': '$79 - $229',
                'rent_cart_cost': '$25',
                'course_length_forward': '6,349 yards',
                'course_length_tips': '7,585 yards',
                'course_slope': '142',
                'thumbnail': 'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Pro Shop', 'Club Rental', 'Restaurant', 'Bar'],
            },
            {
                'name': 'TPC Sawgrass (Stadium Course)',
                'address': '110 Championship Way',
                'city': 'Ponte Vedra Beach',
                'state': 'FL',
                'zip_code': '32082',
                'phone_number': '(904) 273-3235',
                'website': 'https://www.tpc.com/sawgrass',
                'rating_google': '4.8',
                'rating_golf_now': '4.9',
                'rating_grint': '4.8',
                'cost': '$450 - $550',
                'rent_cart_cost': 'Included',
                'course_length_forward': '6,394 yards',
                'course_length_tips': '7,256 yards',
                'course_slope': '155',
                'thumbnail': 'https://images.unsplash.com/photo-1592919505780-303950717480?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Putting Green', 'Pro Shop', 'Club Rental', 'Golf Carts', 'Restaurant', 'Bar', 'Locker Rooms', 'Tournament Hosting'],
            },
            {
                'name': 'Whistling Straits (Straits Course)',
                'address': 'N8501 County Highway LS',
                'city': 'Haven',
                'state': 'WI',
                'zip_code': '53083',
                'phone_number': '(920) 457-4446',
                'website': 'https://www.destinationkohler.com/golf/whistling-straits',
                'rating_google': '4.9',
                'rating_golf_now': '4.8',
                'rating_grint': '4.9',
                'cost': '$410 - $490',
                'rent_cart_cost': 'Included',
                'course_length_forward': '6,086 yards',
                'course_length_tips': '7,790 yards',
                'course_slope': '151',
                'thumbnail': 'https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Pro Shop', 'Golf Carts', 'Restaurant', 'Bar', 'Locker Rooms', 'Banquet Facilities'],
            },
            {
                'name': 'Kiawah Island Golf Resort (Ocean Course)',
                'address': '1000 Ocean Course Drive',
                'city': 'Kiawah Island',
                'state': 'SC',
                'zip_code': '29455',
                'phone_number': '(843) 768-2121',
                'website': 'https://www.kiawahresort.com',
                'rating_google': '4.7',
                'rating_golf_now': '4.8',
                'rating_grint': '4.7',
                'cost': '$320 - $425',
                'rent_cart_cost': 'Included',
                'course_length_forward': '5,327 yards',
                'course_length_tips': '7,876 yards',
                'course_slope': '152',
                'thumbnail': 'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Putting Green', 'Pro Shop', 'Club Rental', 'Golf Carts', 'Restaurant', 'Bar', 'Locker Rooms'],
            },
            {
                'name': 'Bandon Dunes Golf Resort',
                'address': '57744 Round Lake Drive',
                'city': 'Bandon',
                'state': 'OR',
                'zip_code': '97411',
                'phone_number': '(541) 347-4380',
                'website': 'https://www.bandondunesgolf.com',
                'rating_google': '4.9',
                'rating_golf_now': '4.9',
                'rating_grint': '4.9',
                'cost': '$315 - $390',
                'rent_cart_cost': 'Walking Only',
                'course_length_forward': '5,706 yards',
                'course_length_tips': '7,109 yards',
                'course_slope': '145',
                'thumbnail': 'https://images.unsplash.com/photo-1592919505780-303950717480?w=800',
                'status': 'approved',
                'amenities': ['Driving Range', 'Pro Shop', 'Club Rental', 'Restaurant', 'Bar', 'Locker Rooms', 'Practice Facility'],
            },
            {
                'name': 'Oakmont Country Club',
                'address': '1233 Hulton Road',
                'city': 'Oakmont',
                'state': 'PA',
                'zip_code': '15139',
                'phone_number': '(412) 828-8000',
                'website': 'https://www.oakmont-countryclub.org',
                'rating_google': '4.6',
                'cost': 'Private (Members Only)',
                'course_length_forward': '6,259 yards',
                'course_length_tips': '7,255 yards',
                'course_slope': '150',
                'status': 'pending',
                'amenities': ['Driving Range', 'Putting Green', 'Pro Shop', 'Restaurant', 'Bar', 'Tournament Hosting'],
            },
            {
                'name': 'Spyglass Hill Golf Course',
                'address': '3206 Stevenson Drive',
                'city': 'Pebble Beach',
                'state': 'CA',
                'zip_code': '93953',
                'phone_number': '(831) 625-8563',
                'website': 'https://www.pebblebeach.com',
                'rating_google': '4.7',
                'cost': '$425 - $495',
                'rent_cart_cost': 'Included',
                'course_length_forward': '6,043 yards',
                'course_length_tips': '7,041 yards',
                'course_slope': '148',
                'status': 'pending',
                'amenities': ['Driving Range', 'Pro Shop', 'Golf Carts', 'Restaurant'],
            },
        ]
        
        for course_data in courses_data:
            amenity_names = course_data.pop('amenities')
            
            course, created = Course.objects.get_or_create(
                name=course_data['name'],
                defaults=course_data
            )
            
            if created:
                for amenity_name in amenity_names:
                    if amenity_name in amenities:
                        course.amenities.add(amenities[amenity_name])
                
                self.stdout.write(self.style.SUCCESS(f'  Created course: {course.name}'))
            else:
                self.stdout.write(f'  Course already exists: {course.name}')
        
        self.stdout.write(self.style.SUCCESS('\nDemo data loaded successfully!'))
        self.stdout.write(f'Total courses: {Course.objects.count()}')
        self.stdout.write(f'Approved courses: {Course.objects.filter(status="approved").count()}')
        self.stdout.write(f'Pending courses: {Course.objects.filter(status="pending").count()}')
