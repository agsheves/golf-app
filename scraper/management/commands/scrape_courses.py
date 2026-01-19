"""
Management command to scrape golf course data using FireCrawl API.

Usage:
    python manage.py scrape_courses --state "California" --limit 5
    python manage.py scrape_courses --state "Texas" --limit 10
"""
import os
from django.core.management.base import BaseCommand
from courses.models import Course
from scraper.search_and_scrape import search_and_scrape_courses


class Command(BaseCommand):
    help = 'Scrape golf course data from public sources using FireCrawl'

    def add_arguments(self, parser):
        parser.add_argument(
            '--state',
            type=str,
            required=True,
            help='US state name to search for golf courses (e.g., "California", "Texas")'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Maximum number of courses to scrape (default: 5)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Search and display results without saving to database'
        )

    def handle(self, *args, **options):
        state = options['state']
        limit = options['limit']
        dry_run = options['dry_run']
        
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'FIRECRAWL_API_KEY environment variable not set. '
                'Please add it to your secrets.'
            ))
            return
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting golf course scraper for {state}...'
        ))
        
        try:
            courses = search_and_scrape_courses(state, limit=limit)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error during scraping: {e}'))
            return
        
        if not courses:
            self.stdout.write(self.style.WARNING(
                f'No golf courses found for {state}'
            ))
            return
        
        self.stdout.write(f'Found {len(courses)} courses')
        
        for course in courses:
            self.stdout.write(f"\n  Name: {course.get('name', 'Unknown')}")
            self.stdout.write(f"  URL: {course.get('source_url', 'N/A')}")
            if course.get('phone_number'):
                self.stdout.write(f"  Phone: {course['phone_number']}")
            if course.get('cost'):
                self.stdout.write(f"  Cost: {course['cost']}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nDry run - no data saved to database'
            ))
            return
        
        saved_count = 0
        for course_data in courses:
            name = course_data.get('name', '')
            if not name:
                continue
            
            existing = Course.objects.filter(
                name=name,
                website=course_data.get('source_url', '')
            ).exists()
            
            if existing:
                self.stdout.write(f'  Skipping duplicate: {name[:50]}')
                continue
            
            try:
                course = Course.objects.create(
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
                self.stdout.write(self.style.SUCCESS(
                    f'  Created course (pending): {course.name[:50]}'
                ))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f'  Error saving {name[:50]}: {e}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nScraper completed! Saved {saved_count} new courses from {state} with status=pending'
        ))
