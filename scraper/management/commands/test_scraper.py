"""
Test script to fetch golf courses from 3 different states.

Usage:
    python manage.py test_scraper
    python manage.py test_scraper --dry-run
"""
import os
from django.core.management.base import BaseCommand
from courses.models import Course
from scraper.search_and_scrape import search_and_scrape_courses


class Command(BaseCommand):
    help = 'Test scraper by fetching 3 courses from 3 different states (AZ, TX, FL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Search and display results without saving to database'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=3,
            help='Number of courses to fetch per state (default: 3)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'FIRECRAWL_API_KEY environment variable not set.'
            ))
            return
        
        test_states = ['Arizona', 'Texas', 'Florida']
        
        self.stdout.write(self.style.SUCCESS(
            f'Testing scraper with {len(test_states)} states, {limit} courses each...\n'
        ))
        
        all_courses = []
        
        for state in test_states:
            self.stdout.write(self.style.HTTP_INFO(f'--- {state} ---'))
            
            try:
                courses = search_and_scrape_courses(state, limit=limit)
                all_courses.extend([(state, c) for c in courses])
                
                for course in courses:
                    name = course.get('name', 'Unknown')[:60]
                    url = course.get('source_url', 'N/A')[:50]
                    phone = course.get('phone_number', '')
                    cost = course.get('cost', '')
                    
                    self.stdout.write(f"  {name}")
                    self.stdout.write(f"    URL: {url}...")
                    if phone:
                        self.stdout.write(f"    Phone: {phone}")
                    if cost:
                        self.stdout.write(f"    Cost: {cost}")
                    self.stdout.write('')
                    
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error scraping {state}: {e}'))
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nTotal courses found: {len(all_courses)}'
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                'Dry run - no data saved to database'
            ))
            return
        
        saved_count = 0
        for state, course_data in all_courses:
            name = course_data.get('name', '')
            if not name:
                continue
            
            existing = Course.objects.filter(
                name=name,
                website=course_data.get('source_url', '')
            ).exists()
            
            if existing:
                continue
            
            try:
                Course.objects.create(
                    name=name,
                    address=course_data.get('description', '')[:500] if course_data.get('description') else '',
                    city='',
                    state=state,
                    phone_number=course_data.get('phone_number', ''),
                    website=course_data.get('source_url', ''),
                    cost=course_data.get('cost', ''),
                    status='pending',
                )
                saved_count += 1
            except Exception as e:
                self.stderr.write(f'Error saving {name[:30]}: {e}')
        
        self.stdout.write(self.style.SUCCESS(
            f'Saved {saved_count} new courses with status=pending'
        ))
