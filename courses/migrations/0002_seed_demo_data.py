from django.db import migrations
from django.utils import timezone


def seed_demo_data(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    Amenity = apps.get_model('courses', 'Amenity')
    
    if Course.objects.exists():
        return
    
    driving_range = Amenity.objects.create(name='Driving Range')
    pro_shop = Amenity.objects.create(name='Pro Shop')
    restaurant = Amenity.objects.create(name='Restaurant')
    
    pebble_beach = Course.objects.create(
        name='Pebble Beach Golf Links',
        address='1700 17 Mile Dr',
        city='Pebble Beach',
        state='CA',
        zip_code='93953',
        phone_number='(831) 622-8723',
        website='https://www.pebblebeach.com',
        rating_google='4.8',
        cost='$575',
        course_length_forward='6828',
        course_slope='145',
        status='approved',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    pebble_beach.amenities.set([driving_range, pro_shop, restaurant])
    
    torrey_pines = Course.objects.create(
        name='Torrey Pines Golf Course',
        address='11480 N Torrey Pines Rd',
        city='La Jolla',
        state='CA',
        zip_code='92037',
        phone_number='(858) 452-3226',
        website='https://www.sandiego.gov/park-and-recreation/golf/torreypines',
        rating_google='4.7',
        cost='$252',
        course_length_forward='7698',
        course_slope='139',
        status='approved',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    torrey_pines.amenities.set([driving_range, pro_shop])


def remove_demo_data(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    Amenity = apps.get_model('courses', 'Amenity')
    
    Course.objects.filter(
        name__in=['Pebble Beach Golf Links', 'Torrey Pines Golf Course']
    ).delete()
    
    Amenity.objects.filter(
        name__in=['Driving Range', 'Pro Shop', 'Restaurant']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_demo_data, remove_demo_data),
    ]
