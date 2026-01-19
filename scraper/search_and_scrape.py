from django.db import models
# pip install firecrawl-py
import os
from firecrawl import Firecrawl
from wikipedia import WikipediaPage

firecrawl = Firecrawl(os.getenv("FIRECRAWL_API_KEY"))

def get_all_states():
  # get list of states from a public trusted list - wikipedia or a database
  states = WikipediaPage.("List of states and territories of the United States")
  for state in states:
    state_list.append(state)
    
    return sorted(state_list)

def get_all_cities_by_state(state):
  # get list of cities from a public trusted list - wikipedia or a database
   cities = WikipediaPage.("List of cities in {state}")
   for city in cities:
      city_list_by_state.append(city)
      return sorted(city_list_by_state)


state_list = get_all_states()
city_list_by_state = get_all_cities_by_state(state)
city_state_list = {state: city} #make a =json dictionary of states and cities

def city_state_query_recipe(city, state):
  city_state_query = f"Public golf courses in or near {city}, {state}"

results = firecrawl.search(
    query=city_state_query,
    limit=3,
)
print(results)