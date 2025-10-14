from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import Course, Amenity


class Command(BaseCommand):
    help = 'Seed demo golf courses for initial deployment'

    def handle(self, *args, **options):
        if Course.objects.exists():
            self.stdout.write(self.style.WARNING('Demo data already exists. Skipping.'))
            return

        driving_range, _ = Amenity.objects.get_or_create(name='Driving Range')
        pro_shop, _ = Amenity.objects.get_or_create(name='Pro Shop')
        restaurant, _ = Amenity.objects.get_or_create(name='Restaurant')
        clubhouse, _ = Amenity.objects.get_or_create(name='Clubhouse')

        pebble_beach = Course.objects.create(
            name='Pebble Beach Golf Links',
            address='1700 17 Mile Dr',
            city='Pebble Beach',
            state='CA',
            zip_code='93953',
            phone_number='(831) 622-8723',
            website='https://www.pebblebeach.com',
            rating_google='4.8',
            cost='$675',
            course_length_forward='6,828',
            course_slope='143',
            status='approved',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        pebble_beach.amenities.set([driving_range, pro_shop, restaurant, clubhouse])

        torrey_pines = Course.objects.create(
            name='Torrey Pines Golf Course',
            address='11480 N Torrey Pines Rd',
            city='La Jolla',
            state='CA',
            zip_code='92037',
            phone_number='(858) 452-3226',
            website='https://www.sandiego.gov/torrey-pines',
            rating_google='4.7',
            cost='$306',
            course_length_forward='7,804',
            course_slope='145',
            status='approved',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        torrey_pines.amenities.set([driving_range, pro_shop, restaurant])

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data: Pebble Beach and Torrey Pines'))
