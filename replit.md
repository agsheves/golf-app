# Golf Course Registry

## Overview
The Golf Course Registry is a Django-based web application designed to help users discover and manage public golf courses. It features a responsive frontend for browsing and searching courses, an administrative dashboard for managing course data and an approval workflow, and a web scraping tool to automatically gather new course information. The project aims to provide a comprehensive and user-friendly platform for golf enthusiasts and course administrators alike.

## User Preferences
No specific user preferences were provided in the original `replit.md` file.

## System Architecture

### UI/UX Decisions
- **Frontend Framework**: Bootstrap 5 provides a responsive and mobile-first design.
- **Dynamic Interactions**: HTMX is used for partial page updates and enhanced interactivity without full page reloads, particularly for course detail modals and admin real-time updates.
- **Design Consistency**: A clean, user-friendly interface for both public and admin sections. Golf flag icons serve as default visuals for courses without specific thumbnails.

### Technical Implementations
- **Framework**: Django 5.2.7 is the core web framework.
- **Database**: PostgreSQL is used for data storage, leveraging Replit's built-in services.
- **Static Files**: WhiteNoise handles static file serving in production environments.
- **Package Management**: `uv` is used for Python package management.

### Feature Specifications
- **Public Frontend**:
    - Displays approved golf courses with search and filter capabilities (name, location, state, amenities).
    - Course cards are clickable, opening HTMX-powered detail modals.
    - Discrete admin access button in the navbar for staff.
- **Admin Dashboard**:
    - Custom, user-friendly interface for managing courses at `/admin/dashboard/`.
    - Features editable course cards with real-time auto-save and visual feedback.
    - Image management with live thumbnail previews.
    - Quick approval/unapproval toggle for courses.
    - Filtering by approval status (pending, approved, rejected) and search by name, location, state.
    - Direct preview of public course pages from the dashboard.
    - Staff-only authentication for access.
- **Django Admin (Super Admin)**:
    - Located at `/django-admin/` for advanced configuration and superuser operations.
    - Supports bulk actions (approve/reject courses), custom filters, and amenity management.
    - Facilitates conversion of `ImportedCourse` staging data to live `Course` records.
- **Web Scraper (FireCrawl)**:
    - Utilizes a multi-step search process to identify and scrape actual golf course websites, avoiding aggregator sites.
    - Management commands (`scrape_courses`, `test_scraper`) for execution.
    - Intelligently extracts course names, phone numbers, pricing, addresses, and saves them to the `Course` table with a 'pending' status.
    - Includes rate limiting to comply with API usage policies.

### System Design Choices
- **Database Models**:
    - `Course`: Stores approved course data, including status, contact info, details, ratings, pricing, amenities (many-to-many), and moderation logs.
    - `ImportedCourse`: A staging model for scraped/imported data, containing raw JSON and source information, used before conversion to a `Course`.
    - `Amenity`: Reusable amenity definitions (e.g., Driving Range, Pro Shop).
    - `CourseImage`: Stores multiple images per course, with a primary image flag for thumbnails.
- **Admin Workflow**: Data is scraped into a pending state, reviewed via the custom admin dashboard, and then approved or rejected. Approved courses are displayed on the public site.
- **Deployment**: Configured for Replit Autoscale, using `gunicorn` for running the application. Deployments are idempotent, handling migrations and demo data seeding gracefully without data loss. Database connectivity is managed via `DATABASE_URL` with SSL enforcement and connection health checks.

## External Dependencies
- **PostgreSQL**: Used as the primary database, integrated through Replit's built-in service.
- **FireCrawl API**: Utilized for web scraping functionality, requiring a `FIRECRAWL_API_KEY` environment secret.
- **Bootstrap 5**: Frontend framework sourced via CDN or static files.
- **HTMX**: For dynamic frontend interactions, sourced via CDN or static files.
- **WhiteNoise**: For serving static files efficiently in production.
- **gunicorn**: WSGI HTTP server used for running the Django application in production.