# Golf Course Registry - Anvil Application

## Project Overview
This is an **Anvil web application** - a golf course directory/registry that allows users to browse, search, and view golf course information including ratings, amenities, contact details, and more.

## Important Notice: Anvil Platform Dependency
**This application is built with Anvil and cannot run in a standard Replit environment.**

Anvil is a proprietary Python web framework that requires:
- Anvil's cloud runtime environment
- Anvil's proprietary UI framework
- Anvil's data tables service (cloud database)
- Anvil's Google Drive integration service
- Anvil's authentication service

## Application Features
- Golf course listing and search
- Filter courses by amenities
- View detailed course information (ratings, contact info, amenities, etc.)
- Integration with Google Sheets for course data
- User authentication system
- Admin capabilities for managing course entries

## Database Schema
The app uses Anvil Data Tables with the following tables:
- **course_info**: Main table for golf course data
- **categories**: Course categories
- **entries**: General entries/posts
- **images**: Image gallery for homepage carousel
- **users**: User authentication and profiles

## How to Run This Application

### Option 1: Run on Anvil (Recommended)
1. Go to [Anvil Editor](https://anvil.works/build)
2. Sign up for a free Anvil account
3. Click "Clone from GitHub"
4. Enter this repository's URL
5. The app will open in the Anvil Editor
6. Click the "Run" button to test the app
7. Use "Publish" to deploy it online

### Option 2: Convert to Standard Python Web App (Significant Effort)
To run this on Replit, you would need to:
1. Rebuild the UI using a standard Python web framework (Flask, Django, Streamlit, etc.)
2. Replace Anvil Data Tables with PostgreSQL or another database
3. Reimplement all server functions as standard Python code
4. Recreate the Google Sheets integration using standard Google APIs
5. Rebuild the authentication system

This would essentially be creating a new application from scratch.

## Project Structure
- `client_code/`: Frontend forms and UI components (Anvil-specific)
- `server_code/`: Backend server functions
- `theme/`: Custom styling and assets
- `anvil.yaml`: Anvil app configuration and database schema

## Recent Changes
- 2025-10-13: Imported from GitHub to Replit

## Notes
- The app integrates with a Google Sheet named "Golf Corse Registry" for data
- Uses Anvil Extras dependency (v3.2.0)
- Configured for Python 3.10 runtime
