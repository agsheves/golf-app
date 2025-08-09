from ._anvil_designer import DetailedViewTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class DetailedView(DetailedViewTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Fill in fields
    self.label_name.text = f"Name: {self.item['name']}"
    self.label_address.text = f"Address: {self.item['address']}"
    self.label_phone.text = f"Phone: {self.item['phone_number']}"
    self.label_cost.text = f"Cost: {self.item['cost']}"
    self.image_thumbnail.source = self.item['thumbnail']
    self.label_rating_google.text = f"rating_google: {self.item['rating_google']}"
    self.label_walking_rates.text = f"walking_rates: {self.item['walking_rates']}"
    self.label_weekend_rate.text = f"weekend_rate: {self.item['weekend_rate']}"
    self.label_course_Slope.text = f"course_Slope: {self.item['course_Slope']}"
    self.label_rent_cart_price.text = f"rent_cart_price: {self.item['rent_cart_price']}"
    self.label_website.text = f"website: {self.item['website']}"
    self.label_state.text = f"state: {self.item['state']}"
    self.label_weekday_rate.text = f"weekday_rate: {self.item['weekday_rate']}"
    self.label_rating_grint.text = f"rating_grint: {self.item['rating_grint']}"
    self.label_scorecard.text = f"scorecard: {self.item['scorecard']}"
    self.label_amenities.text = f"amenities: {self.item['amenities']}"
    self.label_twlight_rate.text = f"twlight_rate: {self.item['twlight_rate']}"
    self.label_rating_golf_pass.text = f"rating_golf_pass: {self.item['rating_golf_pass']}"
    self.label_description.text = f"description: {self.item['description']}"
    self.label_course_length.text = f"course_length: {self.item['course_length']}"
    self.label_thumbnail.text = f"thumbnail: {self.item['thumbnail']}"
    self.label_zip_code.text = f"Cozip_codest: {self.item['zip_code']}"
    self.label_rating.text = f"rating: {self.item['rating']}"