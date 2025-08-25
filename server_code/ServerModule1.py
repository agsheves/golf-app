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
  ws = golf_files["REAL DATA"]
  for r in ws.rows:
    name = r['name']
    address = r['address']
    phone_number = r['phone_number']
    rating_golf_now = r['rating_golf_now']
    course_length_tips = r['course_length_tips']
    course_length_forward = r['course_length_forward']
    course_slope = r['course_slope']
    amenities = r['amenities']
    thumbnail = r['thumbnail']
    booking_link = ['booking_link']
    website = r['website']
    cost = r['cost']
    rent_cart_cost = r['rent_cart_cost']
    scorecard = r['scorecard']
    rating_google = r['rating_google']
    rating_grint = r['rating_grint']
  
    app_tables.course_info.add_row(
      name = name,
      address = address,
      phone_number = phone_number,
      rating_golf_now = rating_golf_now,
      course_length_tips = course_length_tips,
      course_length_forward = course_length_forward,
      course_slope = course_slope,
      amenities = amenities,
      thumbnail = thumbnail,
      booking_link = booking_link,
      website = website,
      cost = cost,
      rent_cart_cost = rent_cart_cost,
      scorecard = scorecard,
      rating_google = rating_google,
      rating_grint = rating_grint
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
