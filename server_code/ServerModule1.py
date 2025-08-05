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