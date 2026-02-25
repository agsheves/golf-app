"""
Golf Course Scraper using FireCrawl API

Multi-step search approach:
1. Search for golf courses in a state
2. Identify if results are aggregator articles vs actual course websites
3. For aggregator articles, extract individual course names
4. Search for each individual course to find its actual website
5. Scrape and parse the actual course website

Batching strategy:
- Rotates through different search queries on each pass
- Checks database BEFORE any expensive API call to avoid re-scraping
- Tracks all discovered URLs in ScrapeLog to prevent re-discovery costs
"""
import os
import re
import time
from typing import Optional
from pydantic import BaseModel, Field
from firecrawl import Firecrawl

RATE_LIMIT_DELAY = 12

SEARCH_QUERY_TEMPLATES = [
    "public golf course {state}",
    "municipal golf course {state}",
    "golf club {state} tee times",
    "affordable public golf {state}",
    "city golf course {state}",
    "county golf course {state}",
    "public golf links {state}",
    "golf course {state} green fees",
    "best value public golf {state}",
    "18 hole public golf course {state}",
    "9 hole public golf course {state}",
    "public golf {state} driving range",
]


class GolfCourseData(BaseModel):
    """Schema for extracting golf course information from websites."""
    name: str = Field(description="Name of the golf course")
    address: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State abbreviation (e.g., CA, TX)")
    zip_code: Optional[str] = Field(default=None, description="ZIP code")
    phone_number: Optional[str] = Field(default=None, description="Phone number")
    website: Optional[str] = Field(default=None, description="Website URL")
    green_fee: Optional[str] = Field(default=None, description="Green fee or price range")
    cart_fee: Optional[str] = Field(default=None, description="Cart rental fee")
    course_length: Optional[str] = Field(default=None, description="Course length in yards")
    course_slope: Optional[str] = Field(default=None, description="Course slope rating")
    course_rating: Optional[str] = Field(default=None, description="Course rating")
    amenities: Optional[list[str]] = Field(default=None, description="List of amenities")
    description: Optional[str] = Field(default=None, description="Course description")


class ExtractedCourseNames(BaseModel):
    """Schema for extracting golf course names from aggregator articles."""
    course_names: list[str] = Field(description="List of golf course names mentioned in the article")


AGGREGATOR_DOMAINS = [
    'golfpass.com',
    'golfdigest.com',
    'golf.com',
    'golfadvisor.com',
    'top100golfcourses.com',
    'tripadvisor.com',
    'yelp.com',
    'google.com',
    'wikipedia.org',
    'thegrint.com',
    'golfnow.com',
]

AGGREGATOR_PATTERNS = [
    r'top\s*\d+',
    r'best\s+\d+',
    r'best\s+public',
    r'best\s+golf',
    r'\d+\s+best',
    r'guide',
    r'list',
    r'ranking',
]

DIRECTORY_URL_PATTERNS = [
    r'/directory',
    r'/courses[^/]*$',
    r'/golf-courses',
    r'/course-directory',
    r'/course-listing',
    r'/all-courses',
]

DIRECTORY_TITLE_PATTERNS = [
    r'directory',
    r'all\s+courses',
    r'\d+\s+courses',
    r'courses\s+in',
    r'golf\s+courses$',
    r'course\s+listing',
    r'find\s+a\s+course',
]

MUNICIPAL_URL_PATTERNS = [
    r'\.gov/',
    r'/parks/',
    r'/departments/',
    r'/administration/',
    r'/activities',
    r'/facilities',
    r'/recreation/',
    r'/public-golf',
]


def get_firecrawl_client() -> Firecrawl:
    """Initialize FireCrawl client with API key from environment."""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")
    return Firecrawl(api_key=api_key)


def is_aggregator_url(url: str, title: str) -> bool:
    url_lower = url.lower()
    title_lower = title.lower()

    for domain in AGGREGATOR_DOMAINS:
        if domain in url_lower:
            return True

    for pattern in AGGREGATOR_PATTERNS:
        if re.search(pattern, title_lower):
            return True

    return False


def is_municipal_listing(url: str, title: str) -> bool:
    url_lower = url.lower()

    for pattern in MUNICIPAL_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True

    return False


def is_directory_or_listing(url: str, title: str) -> bool:
    url_lower = url.lower()
    title_lower = title.lower()

    if is_municipal_listing(url, title):
        return False

    for pattern in DIRECTORY_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True

    for pattern in DIRECTORY_TITLE_PATTERNS:
        if re.search(pattern, title_lower):
            return True

    return False


def is_likely_course_website(url: str, title: str) -> bool:
    url_lower = url.lower()
    title_lower = title.lower()

    if is_aggregator_url(url, title):
        return False

    if is_directory_or_listing(url, title):
        return False

    positive_domain_patterns = [
        r'^https?://[^/]*(?:golf|cc|countryclub|country-club|golfclub|links)[^/]*\.(?:com|org|net)/?$',
        r'^https?://[^/]+\.(?:com|org|net)/$',
    ]

    positive_title_patterns = [
        r'^[A-Z][^|:]+(?:Golf\s*(?:Course|Club)|Country\s*Club|Golf\s*Links|Golf\s*Resort)',
        r':\s*Home$',
        r'–\s*Official',
        r'-\s*Official',
    ]

    has_specific_name = bool(re.match(r'^[A-Z][a-zA-Z\s\-\']+(?:Golf|Country|Club|Links|Resort)', title))

    domain_match = any(re.search(p, url_lower) for p in positive_domain_patterns)
    title_match = any(re.search(p, title) for p in positive_title_patterns)

    if title_match and has_specific_name:
        return True

    if domain_match and has_specific_name:
        return True

    if 'golf' in url_lower and has_specific_name and ':' not in title_lower:
        return True

    return False


def normalize_url(url: str) -> str:
    """Normalize a URL for comparison (strip trailing slashes, lowercase domain)."""
    url = url.strip().rstrip('/')
    url = re.sub(r'^https?://(www\.)?', '', url.lower())
    return url


def get_known_urls_and_names(state: str) -> tuple[set, set]:
    """
    Load all known URLs and course names for a state from the database.
    This is checked BEFORE any API calls to avoid paying for re-discovery.
    """
    from courses.models import Course, ScrapeLog

    known_urls = set()
    known_names = set()

    courses = Course.objects.filter(state__iexact=state).values_list('website', 'name')
    for website, name in courses:
        if website:
            known_urls.add(normalize_url(website))
        if name:
            known_names.add(name.lower().strip())

    logs = ScrapeLog.objects.filter(state__iexact=state)
    for log in logs:
        for url in log.urls_discovered:
            if url:
                known_urls.add(normalize_url(url))

    return known_urls, known_names


def get_next_search_query(state: str) -> str:
    """
    Pick the next unused search query for a state.
    Rotates through SEARCH_QUERY_TEMPLATES, skipping ones already used.
    """
    from courses.models import ScrapeLog

    used_queries = set(
        ScrapeLog.objects.filter(state__iexact=state)
        .values_list('search_query', flat=True)
    )

    for template in SEARCH_QUERY_TEMPLATES:
        query = template.format(state=state)
        if query not in used_queries:
            return query

    return SEARCH_QUERY_TEMPLATES[0].format(state=state)


def is_url_known(url: str, known_urls: set) -> bool:
    """Check if a URL is already known (already discovered or in database)."""
    return normalize_url(url) in known_urls


def is_name_known(name: str, known_names: set) -> bool:
    """Check if a course name is already known in the database for this state."""
    return name.lower().strip() in known_names


def search_web(query: str, limit: int = 10) -> list[dict]:
    client = get_firecrawl_client()

    results = client.search(
        query=query,
        limit=limit,
    )

    items = []
    if results and hasattr(results, 'web') and results.web:
        for item in results.web:
            items.append({
                'title': getattr(item, 'title', '') or '',
                'url': getattr(item, 'url', '') or '',
                'description': getattr(item, 'description', '') or '',
            })

    return items


def extract_course_names_from_article(url: str) -> list[str]:
    client = get_firecrawl_client()

    try:
        time.sleep(RATE_LIMIT_DELAY)
        result = client.scrape(url)

        if result and getattr(result, 'markdown', None):
            content = result.markdown

            course_names = []

            patterns = [
                r'\*\*([A-Z][^*\n]+(?:Golf|Country|Club|Links|Course|Resort)[^*\n]*)\*\*',
                r'#+\s*\d*\.?\s*([A-Z][^\n]+(?:Golf|Country|Club|Links|Course|Resort)[^\n]*)',
                r'\d+\.\s+\*?\*?([A-Z][^*\n]+(?:Golf|Country|Club|Links|Course|Resort)[^*\n]*)',
                r'\n([A-Z][^\n]{5,50}(?:Golf Course|Golf Club|Country Club|Golf Links|Golf Resort))',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    name = match.strip().rstrip('.')
                    name = re.sub(r'\s+', ' ', name)
                    if 5 < len(name) < 80 and name not in course_names:
                        course_names.append(name)

            return course_names[:20]

    except Exception as e:
        print(f"  Error extracting from {url}: {e}")

    return []


def search_for_course_website(course_name: str, state: str) -> Optional[dict]:
    query = f'"{course_name}" {state} official site'

    results = search_web(query, limit=5)

    for result in results:
        url = result.get('url', '')
        title = result.get('title', '')

        if is_likely_course_website(url, title):
            return {
                'name': course_name,
                'url': url,
                'title': title,
                'description': result.get('description', ''),
            }

    for result in results:
        url = result.get('url', '')
        title = result.get('title', '')

        if not is_aggregator_url(url, title):
            name_words = course_name.lower().split()[:3]
            if any(word in url.lower() for word in name_words if len(word) > 3):
                return {
                    'name': course_name,
                    'url': url,
                    'title': title,
                    'description': result.get('description', ''),
                }

    return None


def pick_best_image(og_image: Optional[str], images: list[str], url: str) -> Optional[str]:
    """
    Pick the best thumbnail image from available sources.
    Priority: og_image > large course-related images > first valid image
    """
    skip_patterns = [
        r'logo', r'icon', r'favicon', r'sprite', r'badge',
        r'button', r'arrow', r'pixel', r'tracking', r'spacer',
        r'1x1', r'widget', r'banner-ad', r'advertisement',
    ]

    good_patterns = [
        r'course', r'golf', r'hole', r'aerial', r'hero',
        r'banner', r'header', r'main', r'feature', r'gallery',
        r'photo', r'scenic', r'fairway', r'green',
    ]

    if og_image and og_image.startswith('http'):
        return og_image

    scored = []
    for img in images:
        if not img or not img.startswith('http'):
            continue
        img_lower = img.lower()
        if any(re.search(p, img_lower) for p in skip_patterns):
            continue
        if not re.search(r'\.(jpg|jpeg|png|webp)', img_lower):
            continue
        score = 0
        if any(re.search(p, img_lower) for p in good_patterns):
            score += 10
        scored.append((score, img))

    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    return None


def scrape_course_details(url: str) -> dict:
    client = get_firecrawl_client()
    data = {'source_url': url}

    try:
        time.sleep(RATE_LIMIT_DELAY)
        result = client.scrape(url)

        if result and getattr(result, 'markdown', None):
            content = result.markdown
            data['raw_content'] = content[:3000]

            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phone_match = re.search(phone_pattern, content)
            if phone_match:
                data['phone_number'] = phone_match.group()

            price_pattern = r'\$\d+(?:\.\d{2})?(?:\s*[-–]\s*\$\d+(?:\.\d{2})?)?'
            price_matches = re.findall(price_pattern, content)
            if price_matches:
                data['cost'] = price_matches[0]

            zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
            zip_match = re.search(zip_pattern, content)
            if zip_match:
                data['zip_code'] = zip_match.group()

            city_state_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2})\s+\d{5}'
            city_match = re.search(city_state_pattern, content)
            if city_match:
                data['city'] = city_match.group(1)
                data['state_abbrev'] = city_match.group(2)

            metadata = getattr(result, 'metadata', None)
            if metadata:
                if hasattr(metadata, 'description') and metadata.description:
                    data['description'] = metadata.description[:500]
                og_image = getattr(metadata, 'og_image', None)
            else:
                og_image = None

            page_images = getattr(result, 'images', None) or []
            thumbnail = pick_best_image(og_image, page_images, url)
            if thumbnail:
                data['thumbnail'] = thumbnail
                print(f"    Found image: {thumbnail[:80]}...")

    except Exception as e:
        print(f"  Error scraping {url}: {e}")

    return data


def search_and_scrape_courses(state: str, limit: int = 5) -> list[dict]:
    """
    Multi-step search and scrape for golf courses with efficient batching.

    Cost-saving strategy:
    - Loads all known URLs/names from DB BEFORE any API calls
    - Filters out already-known URLs at discovery stage (free) not scrape stage (costly)
    - Rotates search queries across passes to find new results
    - Logs all discovered URLs to prevent re-discovery costs on future passes

    Args:
        state: US state name
        limit: Target number of NEW courses to find

    Returns:
        List of course data dictionaries (only genuinely new courses)
    """
    from courses.models import ScrapeLog

    known_urls, known_names = get_known_urls_and_names(state)
    print(f"Database has {len(known_urls)} known URLs and {len(known_names)} known names for {state}")

    search_query = get_next_search_query(state)
    print(f"Search query: \"{search_query}\"")

    all_discovered_urls = []
    skipped_count = 0

    print(f"Searching for golf courses in {state}...")
    search_results = search_web(search_query, limit=limit * 2)

    direct_courses = []
    aggregator_urls = []

    for result in search_results:
        url = result.get('url', '')
        title = result.get('title', '')

        if not url:
            continue

        all_discovered_urls.append(url)

        if is_url_known(url, known_urls):
            print(f"  [SKIP-URL] Already known: {title[:50]}...")
            skipped_count += 1
            continue

        if is_likely_course_website(url, title):
            if is_name_known(title, known_names):
                print(f"  [SKIP-NAME] Already known: {title[:50]}...")
                skipped_count += 1
                known_urls.add(normalize_url(url))
                continue
            print(f"  Found course site: {title[:50]}...")
            direct_courses.append({
                'name': title,
                'url': url,
                'description': result.get('description', ''),
            })
            known_urls.add(normalize_url(url))
        elif is_aggregator_url(url, title) or is_municipal_listing(url, title):
            if is_url_known(url, known_urls):
                continue
            if is_municipal_listing(url, title):
                print(f"  Found municipal listing: {title[:50]}...")
            aggregator_urls.append(url)
            known_urls.add(normalize_url(url))

    extracted_names = []
    if len(direct_courses) < limit and aggregator_urls:
        print(f"  Extracting course names from {len(aggregator_urls)} article(s)...")

        for agg_url in aggregator_urls[:2]:
            all_discovered_urls.append(agg_url)
            names = extract_course_names_from_article(agg_url)
            print(f"    Found {len(names)} course names")
            extracted_names.extend(names)

    seen_names = set(c['name'].lower() for c in direct_courses)
    unique_extracted = []
    for name in extracted_names:
        name_lower = name.lower()
        if name_lower not in seen_names and not is_name_known(name, known_names):
            seen_names.add(name_lower)
            unique_extracted.append(name)
        elif is_name_known(name, known_names):
            print(f"  [SKIP-NAME] Already known: {name[:50]}")
            skipped_count += 1

    courses_needed = limit - len(direct_courses)
    if unique_extracted and courses_needed > 0:
        print(f"  Searching for {min(len(unique_extracted), courses_needed)} individual courses...")

        for course_name in unique_extracted[:courses_needed]:
            found = search_for_course_website(course_name, state)
            if found:
                url = found['url']
                if is_url_known(url, known_urls):
                    print(f"    [SKIP-URL] Already known: {course_name[:40]}")
                    skipped_count += 1
                    continue
                print(f"    Found: {course_name[:40]} -> {found['url'][:50]}...")
                direct_courses.append(found)
                known_urls.add(normalize_url(url))
                all_discovered_urls.append(url)
            else:
                print(f"    Not found: {course_name[:40]}")

    courses = []
    for course_info in direct_courses[:limit]:
        url = course_info.get('url', '')
        name = course_info.get('name', '')

        print(f"  Scraping: {name[:40]}...")
        details = scrape_course_details(url)

        course_data = {
            'name': name,
            'source_url': url,
            'description': course_info.get('description', details.get('description', '')),
            'phone_number': details.get('phone_number', ''),
            'cost': details.get('cost', ''),
            'zip_code': details.get('zip_code', ''),
            'city': details.get('city', ''),
            'thumbnail': details.get('thumbnail', ''),
            'raw_data': {
                'search_result': course_info,
                'scraped_content': details.get('raw_content', '')[:1000],
            },
        }

        courses.append(course_data)

    ScrapeLog.objects.create(
        state=state,
        search_query=search_query,
        urls_discovered=all_discovered_urls,
        courses_created=len(courses),
        courses_skipped=skipped_count,
    )

    print(f"Found {len(courses)} new courses in {state} (skipped {skipped_count} already known)")
    return courses
