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
  return app_tables.entries.search(
    tables.order_by("created", ascending=False)
  )

@anvil.server.callable
def update_entry(entry, entry_dict):
  # check that the entry given is really a row in the ‘entries’ table
  if app_tables.entries.has_row(entry):
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
  golf_files = app_files.golf_corse_registry
  ws = golf_files["Sheet1"]
  for r in ws.rows:
    name = r['name']
    address = r['address']
    phone_number = r['phone_number']
    thumbnail = r['thumbnail']
    description = r['description']
    website = r['website']
    type = r['type']
    cost = r['cost']
    booking_window_days = r['booking_window_days']
    scorecard = r['scorecard']
    rating_google = r['rating_google']
    rating_grint = r['rating_grint']
    thumbnail = r['thumbnail']
    booking_window_days = r['booking_window_days']
    app_tables.course_info.add_row(
      name=name,
      address=address,
      phone_number=phone_number,
      thumbnail =	thumbnail,
      #description=description,
      website=website,
      type=type,
      cost=cost,
      booking_window_days=booking_window_days,
      scorecard=scorecard,
      rating_google=rating_google,
      rating_grint=rating_grint
    )