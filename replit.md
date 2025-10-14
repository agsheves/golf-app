# Golf Course Registry

## Project Overview
A Django-based web application for discovering and managing public golf courses. Features a responsive frontend with search/filter capabilities, an admin approval workflow, and web scraping tools to gather course data.

## Live Application
- **Public Site**: Browse approved golf courses at the root URL (`/`)
- **Admin Panel**: Manage courses and review imports at `/admin`
  - **First-time setup**: Create admin user with `python manage.py createsuperuser`
  - Use a strong, unique password for production!

## Key Features

### Public Frontend
- **Responsive Card Layout**: Mobile and desktop optimized using Bootstrap 5
- **Search & Filter**: Find courses by name, location, state, or amenities
- **Course Cards**: Display key info (name, location, rating, pricing)
- **Detail Views**: HTMX-powered modal for quick course details
- **Golf Flag Icons**: Default visual for courses without thumbnails

### Admin Workflow
- **Approval System**: Review and approve/reject imported courses
- **Bulk Actions**: Approve or reject multiple courses at once
- **Import Management**: Convert ImportedCourse staging data to live Course records
- **Custom Filters**: Filter by status, state, review date
- **Amenity Management**: Create and assign amenities to courses

### Web Scraper
- **Management Command**: `python manage.py scrape_courses`
- **Staging Table**: ImportedCourse stores scraped data for review
- **Data Structure**: JSON raw_data field preserves original scraped content
- **Source Tracking**: Records source URL and type (scraper/manual/API)

## Tech Stack
- **Framework**: Django 5.2.7
- **Database**: PostgreSQL (Replit built-in)
- **Frontend**: Bootstrap 5 + HTMX for dynamic interactions
- **Static Files**: WhiteNoise for serving in production
- **Package Manager**: uv (Python)

## Project Structure

```
golf_registry/          # Django project settings
├── settings.py        # Database, apps, middleware config
├── urls.py           # URL routing
└── wsgi.py           # WSGI application

courses/               # Core app - course data & models
├── models.py         # Course, ImportedCourse, Amenity, CourseImage
├── admin.py          # Custom admin with approval actions
└── migrations/       # Database migrations

frontend/              # Public-facing views and templates
├── views.py          # course_list, course_detail
├── templates/
│   └── frontend/
│       ├── base.html
│       ├── course_list.html
│       ├── course_detail.html
│       └── course_detail_modal.html
└── static/           # CSS, JS (currently using CDN)

scraper/               # Data collection app
└── management/
    └── commands/
        └── scrape_courses.py
```

## Database Models

### Course (Approved Courses)
- **Status**: pending, approved, rejected, suppressed
- **Basic Info**: name, address, city, state, zip_code
- **Contact**: phone_number, website, booking_link
- **Course Details**: length, slope, scorecard
- **Ratings**: Google, Golf Now, The Grint
- **Pricing**: green fee cost, cart rental cost
- **Amenities**: Many-to-many relationship
- **Moderation**: reviewed_by, reviewed_at, moderation_notes

### ImportedCourse (Staging)
- Stores scraped/imported data before approval
- **raw_data**: JSON field with original scraped content
- **source**: scraper, manual, or API
- **processed**: Boolean flag when converted to Course

### Amenity
- Reusable amenities (Driving Range, Pro Shop, Restaurant, etc.)
- Many-to-many with courses

### CourseImage
- Multiple images per course
- Primary image flag for thumbnails

## Admin Workflow

1. **Scrape Data**: Run `python manage.py scrape_courses`
2. **Review Imports**: Go to Admin → Imported Courses
3. **Create Courses**: Select imports → Actions → "Create courses from selected imports"
4. **Approve**: Go to Admin → Courses → Select pending → Actions → "Approve selected courses"
5. **Publish**: Approved courses appear on public site

## Running Locally

The Django server runs automatically via the configured workflow:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Deployment Configuration

- **Type**: Autoscale (stateless web app)
- **Build**: `python manage.py migrate && python manage.py seed_demo_data && python manage.py collectstatic --noinput`
- **Run**: `gunicorn --bind=0.0.0.0:5000 --reuse-port golf_registry.wsgi:application`

### Database Configuration
- **Uses DATABASE_URL**: Automatically configured for both development and production environments
- **SSL Enabled**: Secure connections with `sslmode=require`
- **Seamless Deployment**: No manual database configuration needed
- **Fallback Support**: Falls back to individual PG* variables if DATABASE_URL unavailable

### Production Database & Demo Data
- **Automatic Setup**: Production database migrations run automatically during deployment
- **Demo Data Seeding**: `seed_demo_data` management command populates sample courses
- **No Duplicates**: Command checks if courses exist before seeding
- **Demo Courses Included**:
  - **Pebble Beach Golf Links** (Pebble Beach, CA) - 4.8 rating, **$675** green fee, 6,828 yards, slope 143
  - **Torrey Pines Golf Course** (La Jolla, CA) - 4.7 rating, **$306** green fee, 7,804 yards, slope 145
  - Amenities: Driving Range, Pro Shop, Restaurant, Clubhouse

### Deploying to Production:
1. **Click Deploy** - Migrations and demo data seed automatically
2. **Create admin user**: Run `python manage.py createsuperuser` after deployment
3. **Optional**: Set `DEBUG=False` environment variable to disable debug mode

The app uses DATABASE_URL for seamless database connectivity across all environments.

## Common Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run scraper
python manage.py scrape_courses

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

## Environment Variables

### Database (Replit PostgreSQL)
- `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT` - Auto-configured by Replit

### Optional Settings
- `SECRET_KEY` - Already configured in Replit secrets
- `DEBUG` - Set to `False` to disable debug mode (defaults to `True`)

## Sample Data

The database includes:
- **Pebble Beach Golf Links** (Pebble Beach, CA) - $675, 4.8 rating
- **Torrey Pines Golf Course** (La Jolla, CA) - $306, 4.7 rating
- Various amenities (Driving Range, Pro Shop, Restaurant, Clubhouse)

## Recent Changes

### 2025-10-14: Database Configuration Fixed
- ✅ **Fixed deployment authentication**: Now uses DATABASE_URL for seamless dev/production connectivity
- ✅ Updated settings.py to use dj-database-url for consistent database parsing
- ✅ Fresh database created with real demo course data
- ✅ Demo courses added: Pebble Beach ($675) and Torrey Pines ($306) with accurate information
- ✅ SSL connections enabled for all environments
- ✅ Deployment build process verified: migrations → seed data → collect static files

### 2025-10-14: Simplified Configuration
- ✅ Streamlined settings to work the same in dev and production
- ✅ Removed complex environment differentiation
- ✅ Unified configuration with sensible defaults

### 2025-10-14: Initial Build
- ✅ Django 5.2.7 project setup with PostgreSQL
- ✅ Course management models with approval workflow
- ✅ Responsive Bootstrap 5 frontend with HTMX
- ✅ Custom Django admin with bulk approval actions
- ✅ Web scraper framework with staging table
- ✅ Deployment configuration for Replit autoscale
- ✅ Sample data for Pebble Beach and Torrey Pines

## Next Steps / Enhancements

1. **Enhanced Scraper**: Add real scraping logic for golf course websites
2. **Image Uploads**: Enable course image uploads via admin
3. **Geolocation**: Add map view and distance-based search
4. **User Reviews**: Allow public users to rate and review courses
5. **Booking Integration**: Connect to tee time booking APIs
6. **Email Notifications**: Alert admins when new imports arrive
7. **Advanced Filters**: Course type, difficulty, price ranges
8. **Mobile App**: Consider React Native or PWA for mobile experience
