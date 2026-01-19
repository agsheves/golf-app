"""
Golf Course Scraper using FireCrawl API

Multi-step search approach:
1. Search for golf courses in a state
2. Identify if results are aggregator articles vs actual course websites
3. For aggregator articles, extract individual course names
4. Search for each individual course to find its actual website
5. Scrape and parse the actual course website
"""
import os
import re
import time
from typing import Optional
from pydantic import BaseModel, Field
from firecrawl import Firecrawl

RATE_LIMIT_DELAY = 12


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
    r'/parks/',
    r'/departments/',
    r'/administration/',
    r'/activities',
    r'/facilities',
    r'/public-golf',
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


def get_firecrawl_client() -> Firecrawl:
    """Initialize FireCrawl client with API key from environment."""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")
    return Firecrawl(api_key=api_key)


def is_aggregator_url(url: str, title: str) -> bool:
    """
    Check if a URL/title is from an aggregator site (articles about courses)
    vs an actual golf course website.
    
    Returns True if this appears to be an aggregator/article, False if it looks
    like an actual golf course website.
    """
    url_lower = url.lower()
    title_lower = title.lower()
    
    for domain in AGGREGATOR_DOMAINS:
        if domain in url_lower:
            return True
    
    for pattern in AGGREGATOR_PATTERNS:
        if re.search(pattern, title_lower):
            return True
    
    return False


def is_directory_or_listing(url: str, title: str) -> bool:
    """
    Check if URL is a directory or listing page (multiple courses).
    """
    url_lower = url.lower()
    title_lower = title.lower()
    
    for pattern in DIRECTORY_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True
    
    for pattern in DIRECTORY_TITLE_PATTERNS:
        if re.search(pattern, title_lower):
            return True
    
    return False


def is_likely_course_website(url: str, title: str) -> bool:
    """
    Check if URL is likely an actual individual golf course website.
    
    Must match positive signals AND not match negative signals.
    Positive: Domain/title indicates a specific course
    Negative: Aggregators, directories, listings
    """
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


def search_web(query: str, limit: int = 10) -> list[dict]:
    """
    Perform a web search and return results.
    
    Args:
        query: Search query string
        limit: Maximum number of results
        
    Returns:
        List of search results with title, url, description
    """
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
    """
    Extract individual golf course names from an aggregator article.
    
    Args:
        url: URL of the article (e.g., "Top 25 courses in Florida")
        
    Returns:
        List of golf course names found in the article
    """
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
    """
    Search for a specific golf course's website.
    
    Args:
        course_name: Name of the golf course
        state: State where the course is located
        
    Returns:
        Dict with course info if found, None otherwise
    """
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


def scrape_course_details(url: str) -> dict:
    """
    Scrape detailed information from a golf course website.
    
    Args:
        url: URL of the golf course website
        
    Returns:
        Dictionary with scraped course data
    """
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
            if metadata and hasattr(metadata, 'description') and metadata.description:
                data['description'] = metadata.description[:500]
                
    except Exception as e:
        print(f"  Error scraping {url}: {e}")
    
    return data


def search_and_scrape_courses(state: str, limit: int = 5) -> list[dict]:
    """
    Multi-step search and scrape for golf courses.
    
    Step 1: Search for golf courses in state
    Step 2: Separate direct course sites from aggregator articles
    Step 3: For aggregators, extract individual course names
    Step 4: Search for each course's actual website
    Step 5: Scrape course details
    
    Args:
        state: US state name
        limit: Target number of courses to find
        
    Returns:
        List of course data dictionaries
    """
    print(f"Searching for golf courses in {state}...")
    
    search_results = search_web(f"public golf course {state}", limit=limit * 2)
    
    direct_courses = []
    aggregator_urls = []
    
    for result in search_results:
        url = result.get('url', '')
        title = result.get('title', '')
        
        if not url:
            continue
        
        if is_likely_course_website(url, title):
            print(f"  Found course site: {title[:50]}...")
            direct_courses.append({
                'name': title,
                'url': url,
                'description': result.get('description', ''),
            })
        elif is_aggregator_url(url, title):
            aggregator_urls.append(url)
    
    extracted_names = []
    if len(direct_courses) < limit and aggregator_urls:
        print(f"  Extracting course names from {len(aggregator_urls)} article(s)...")
        
        for agg_url in aggregator_urls[:2]:
            names = extract_course_names_from_article(agg_url)
            print(f"    Found {len(names)} course names")
            extracted_names.extend(names)
    
    seen_names = set(c['name'].lower() for c in direct_courses)
    unique_extracted = []
    for name in extracted_names:
        if name.lower() not in seen_names:
            seen_names.add(name.lower())
            unique_extracted.append(name)
    
    courses_needed = limit - len(direct_courses)
    if unique_extracted and courses_needed > 0:
        print(f"  Searching for {min(len(unique_extracted), courses_needed)} individual courses...")
        
        for course_name in unique_extracted[:courses_needed]:
            found = search_for_course_website(course_name, state)
            if found:
                print(f"    Found: {course_name[:40]} -> {found['url'][:50]}...")
                direct_courses.append(found)
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
            'raw_data': {
                'search_result': course_info,
                'scraped_content': details.get('raw_content', '')[:1000],
            },
        }
        
        courses.append(course_data)
    
    print(f"Found {len(courses)} courses in {state}")
    return courses
