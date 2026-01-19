from django.db import models
# pip install firecrawl-py
import os
app = Firecrawl(api_key=os.getenv('FIRECRAWL_API_KEY'))

# Scrape a website:
app.scrape('firecrawl.dev')