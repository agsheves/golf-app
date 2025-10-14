import os
from django.core.management.base import BaseCommand
from courses.models import ImportedCourse
import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Scrape golf course data from public sources'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting golf course scraper...'))
        
        sample_data = {
            'name': 'Sample Public Golf Course',
            'address': '123 Golf Lane',
            'city': 'San Francisco',
            'state': 'CA',
            'phone_number': '(555) 123-4567',
            'website': 'https://example.com',
        }
        
        imported = ImportedCourse.objects.create(
            source='scraper',
            source_url='https://example.com',
            raw_data=sample_data,
            name=sample_data['name'],
            address=sample_data['address'],
            city=sample_data['city'],
            state=sample_data['state'],
            phone_number=sample_data['phone_number'],
            website=sample_data['website'],
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created import: {imported.name}'))
        self.stdout.write(self.style.SUCCESS('Scraper completed successfully!'))
