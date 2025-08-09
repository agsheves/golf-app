from ._anvil_designer import EntryViewTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..EntryEdit import EntryEdit


class EntryView(EntryViewTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
   

   

    # Any code you write here will run when the form opens.

 
    
  
  def edit_entry_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Create a copy of the existing entry from the Data Table 
    entry_copy = dict(self.item)
    # Open an alert displaying the 'EntryEdit' Form
    # set the `self.item` property of the EntryEdit Form to a copy of the entry to be updated
    save_clicked = alert(
      content=EntryEdit(item=entry_copy),
      title="Update Entry",
      large=True,
      buttons=[("Save", True), ("Cancel", False)]
    )
    # Update the entry if the user clicks save
    if save_clicked:
      anvil.server.call('update_entry', self.item, entry_copy)
  
      # Now refresh the page
      self.refresh_data_bindings()

  def delete_entry_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Get the user to confirm if they wish to delete the entry
    # If yes, raise the 'x-delete-entry' event on the parent 
    # (which is the entries_panel on Homepage)
    if confirm(f"Are you sure you want to delete {self.item['title']}?"):
      self.parent.raise_event('x-delete-entry', entry=self.item)

  def link_1_click(self, **event_args):
    """This method is called when the row is clicked"""
    from anvil import alert
    # Create a formatted string with the data
    details = f"""
      name: {self.item['name']}
      address: {self.item['address']}
      phone_number: {self.item['phone_number']}
      walking_rates: {self.item['walking_rates']}
      rating_google: {self.item['rating_google']}
      weekend_rate: {self.item['weekend_rate']}
      course_Slope: {self.item['course_Slope']}
      cost: {self.item['cost']}
      rent_cart_price: {self.item['rent_cart_price']}
      website: {self.item['website']}
      state: {self.item['state']}
      weekday_rate: {self.item['weekday_rate']}
      rating_grint: {self.item['rating_grint']}
      scorecard: {self.item['scorecard']}
      amenities: {self.item['amenities']}
      twlight_rate: {self.item['twlight_rate']}
      rating_golf_pass: {self.item['rating_golf_pass']}
      description: {self.item['description']}
      course_length: {self.item['course_length']}
      thumbnail: {self.item['thumbnail']}
      zip_code: {self.item['zip_code']}
      rating: {self.item['rating']}
      """
    alert(details, title="Entry Details", large=True, dismissible=True)
