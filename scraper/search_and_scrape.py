"""
Golf Course Scraper using FireCrawl API

This module provides functions to search for public golf courses
and extract structured data from golf course websites.
"""
import os
import re
import json
from typing import Optional
from pydantic import BaseModel, Field
from firecrawl import Firecrawl


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


def get_firecrawl_client() -> Firecrawl:
    """Initialize FireCrawl client with API key from environment."""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")
    return Firecrawl(api_key=api_key)


def search_golf_courses(state: str, limit: int = 10) -> list[dict]:
    """
    Search for public golf courses in a specific state.
    
    Args:
        state: US state name (e.g., "California", "Texas", "Arizona")
        limit: Maximum number of results to return
        
    Returns:
        List of search results with title, url, and description
    """
    client = get_firecrawl_client()
    query = f"public golf course {state}"
    
    results = client.search(
        query=query,
        limit=limit,
    )
    
    courses = []
    if results and hasattr(results, 'web') and results.web:
        for item in results.web:
            courses.append({
                'title': item.title or '',
                'url': item.url or '',
                'description': item.description or '',
            })
    
    return courses


def extract_course_data(url: str) -> Optional[dict]:
    """
    Extract structured golf course data from a URL.
    
    Args:
        url: URL of the golf course website
        
    Returns:
        Dictionary with extracted course data or None if extraction fails
    """
    client = get_firecrawl_client()
    
    try:
        result = client.extract(
            urls=[url],
            prompt="""Extract golf course information including:
                - Course name
                - Full address (street, city, state, zip)
                - Phone number
                - Green fees/pricing
                - Cart rental fees
                - Course length and slope rating
                - Amenities (driving range, pro shop, restaurant, etc.)
                - Brief description""",
            schema=GolfCourseData
        )
        
        if result and 'data' in result:
            return result['data']
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
    
    return None


def scrape_course_page(url: str) -> Optional[dict]:
    """
    Scrape a golf course page and parse the content.
    
    Args:
        url: URL of the golf course website
        
    Returns:
        Dictionary with scraped content or None if scraping fails
    """
    client = get_firecrawl_client()
    
    try:
        result = client.scrape(
            url,
            formats=['markdown'],
            onlyMainContent=True
        )
        
        if result:
            return {
                'url': url,
                'content': result.get('markdown', ''),
                'title': result.get('metadata', {}).get('title', ''),
            }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return None


def parse_course_from_content(content: str, url: str) -> dict:
    """
    Parse golf course information from scraped markdown content.
    
    Args:
        content: Markdown content from scraped page
        url: Source URL
        
    Returns:
        Dictionary with parsed course data
    """
    data = {
        'source_url': url,
        'raw_content': content[:5000],
    }
    
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, content)
    if phone_match:
        data['phone_number'] = phone_match.group()
    
    price_pattern = r'\$\d+(?:\.\d{2})?(?:\s*-\s*\$\d+(?:\.\d{2})?)?'
    price_matches = re.findall(price_pattern, content)
    if price_matches:
        data['cost'] = price_matches[0]
    
    zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
    zip_match = re.search(zip_pattern, content)
    if zip_match:
        data['zip_code'] = zip_match.group()
    
    return data


def search_and_scrape_courses(state: str, limit: int = 5) -> list[dict]:
    """
    Search for golf courses and scrape their data.
    
    Args:
        state: US state name
        limit: Maximum number of courses to process
        
    Returns:
        List of course data dictionaries
    """
    print(f"Searching for golf courses in {state}...")
    search_results = search_golf_courses(state, limit=limit)
    
    courses = []
    for result in search_results:
        url = result.get('url', '')
        title = result.get('title', '')
        description = result.get('description', '')
        
        if not url or ('golf' not in url.lower() and 'golf' not in title.lower()):
            continue
        
        print(f"  Processing: {title[:50]}...")
        
        course_data = {
            'name': title,
            'source_url': url,
            'raw_data': result,
            'description': description,
        }
        
        if description:
            parsed = parse_course_from_content(description, url)
            course_data.update(parsed)
        
        courses.append(course_data)
    
    print(f"Found {len(courses)} courses in {state}")
    return courses
