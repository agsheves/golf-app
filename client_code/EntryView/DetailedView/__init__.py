from ._anvil_designer import DetailedViewTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class DetailedView(DetailedViewTemplate):
  def __init__(self, row_data, **properties):

    self.init_components(**properties)

    self.item = row_data  # store the row
    
    # Fill in fields
    self.label_name.text = self.item['name']
    self.label_address.text = self.item['address']
    self.label_phone.text = self.item['phone_number']
    self.label_cost.text = self.item['cost']
    self.image_thumbnail.source = self.item['thumbnail']
    self.label_rating_google.text = self.item['rating_google']
    self.label_walking_rates.text = self.item['walking_rates']
    self.label_weekend_rate.text = self.item['weekend_rate']
    self.label_course_Slope.text = self.item['course_Slope']
    self.label_rent_cart_price.text = self.item['rent_cart_price']
    self.label_website.text = self.item['website']
    self.label_state.text = self.item['state']
    self.label_weekday_rate.text = self.item['weekday_rate']
    self.label_rating_grint.text = self.item['rating_grint']
    self.label_scorecard.text = self.item['scorecard']
    self.label_amenities.text = self.item['amenities']
    self.label_twlight_rate.text = self.item['twlight_rate']
    self.label_rating_golf_pass.text = self.item['rating_golf_pass']
    self.label_description.text = self.item['description']
    self.label_course_length.text = self.item['course_length']
    self.label_zip_code.text = self.item['zip_code']
    self.label_rating.text = self.item['rating']

    