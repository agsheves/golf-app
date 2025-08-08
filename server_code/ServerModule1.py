import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import anvil.secrets
import anvil.users
import json
import Homepage


@anvil.server.callable

def search_items(search_text, type):
  from anvil.tables import app_tables
  search_text = search_text.lower()

  # Filter the Data Table
  return [row for row in app_tables.course_info.search()
          if search_text in row[type].lower()]

@anvil.server.callable  
def add_entry(entry_dict):
  app_tables.entries.add_row(
    created=datetime.now(),
    **entry_dict
  )

@anvil.server.callable
def get_entries():
  # Get a list of entries from the Data Table, sorted by 'created' column, in descending order
  return app_tables.course_info.search(
    tables.order_by("address", ascending=False)
  )

@anvil.server.callable
def update_entry(entry, entry_dict):
  # check that the entry given is really a row in the ‘entries’ table@
  entry.update(**entry_dict)
  if app_tables.course_info.has_row(entry):
    entry_dict['updated'] = datetime.now()
    entry.update(**entry_dict)
  else:
    raise Exception("Entry does not exist")

@anvil.server.callable
def delete_entry(entry):
  # check that the entry being deleted exists in the Data Table
  if app_tables.entries.has_row(entry):
    entry.delete()
  else:
    raise Exception("Entry does not exist")

    import anvil.google.auth, anvil.google.drive, anvil.google.mail


@anvil.server.callable
def update_courses():
  app_tables.course_info.delete_all_rows()
  golf_files = app_files.golf_corse_registry
  ws = golf_files["Sheet1"]
  for r in ws.rows:
    state = r['state']
    name = r['name']
    address = r['address']
    zip_code = r['zip_code']
    phone_number = r['phone_number']
    rating_golf_pass = r['rating_golf_pass']
    course_length = r['course_length']
    course_Slope = r['course_Slope']
    rating = r['rating']
    amenities = r['amenities']
    weekday_rate = r['weekday_rate']
    weekend_rate = r['weekend_rate']
    walking_rates = r['walking_rates']
    twlight_rate = r['twlight_rate']
    rent_cart_price = r['rent_cart_price']
    thumbnail = r['thumbnail']
    booking_information = ['booking_information']
    description = r['description']
    website = r['website']
    cost = r['cost']
    scorecard = r['scorecard']
    rating_google = r['rating_google']
    rating_grint = r['rating_grint']
    thumbnail = r['thumbnail']
    
    
    app_tables.course_info.add_row(
      state = state,
      name = name,
      address = address,
      zip_code = zip_code,
      phone_number = phone_number,
      rating_golf_pass = rating_golf_pass,
      course_length = course_length,
      course_Slope = course_Slope,
     rating = rating,
     amenities = amenities,
      weekday_rate = weekday_rate,
      weekend_rate = weekend_rate,
      walking_rates = walking_rates,
      twlight_rate = twlight_rate,
      rent_cart_price = rent_cart_price,
      thumbnail = thumbnail,
      booking_information = booking_information,
      description = description,
      website = website,
      cost = cost,
      scorecard = scorecard,
      rating_google = rating_google,
     rating_grint = rating_grint,
    )

@anvil.server.callable
def list_all_unique_amenities():
  from anvil.tables import app_tables

  def parse_amenities(amenities_value):
    if not amenities_value:
      return []
    if isinstance(amenities_value, list):
      return [a.lower().strip() for a in amenities_value if a.strip()]
    if isinstance(amenities_value, str):
      cleaned = amenities_value.replace(" and ", ", ")
      return [item.lower().strip() for item in cleaned.split(",") if item.strip()]
    return []

  all_amenities = set()

  for row in app_tables.course_info.search():
    amenities = parse_amenities(row['amenities'])
    all_amenities.update(amenities)

 

  return sorted(all_amenities)

@anvil.server.callable  
def get_courses_by_amenity(amenity):
  from anvil.tables import app_tables
  
  if isinstance(amenity, list):
    amenity = [a.lower() for a in amenity if isinstance(a, str)]
  elif isinstance(amenity, str):
    amenity = [amenity.lower()]
  else:
    amenity = []

  results = []
  for row in app_tables.course_info.search():
    amenities = row['amenities']

    # Normalize amenities data from each row
    if isinstance(amenities, str):
      amenities = [a.strip().lower() for a in amenities.replace(" and ", ",").split(",") if a.strip()]
    elif isinstance(amenities, list):
      amenities = [a.lower().strip() for a in amenities if isinstance(a, str)]
    else:
      amenities = []

      # ✅ Match if any selected amenity exists in row
    if any(a in amenities for a in amenity):
      results.append(row)

  return results
