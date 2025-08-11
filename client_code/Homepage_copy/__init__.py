from ._anvil_designer import Homepage_copyTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..EntryEdit import EntryEdit
from ..EntryView import EntryView


class Homepage_copy(Homepage_copyTemplate):
  def __init__(self, **properties):
    print(self.multi_select_drop_down_1.selected)
    amenities = anvil.server.call("list_all_unique_amenities")
    self.multi_select_drop_down_1.items = ""
    self.multi_select_drop_down_1.items = amenities

    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    self.refresh_entries()
    # Set an event handler on the RepeatingPanel (our 'entries_panel')
    self.entries_panel.set_event_handler("x-delete-entry", self.delete_entry)
    print(self.multi_select_drop_down_1.selected)

  def add_entry_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Initialise an empty dictionary to store the user inputs
    new_entry = {}
    # Open an alert displaying the 'EntryEdit' Form
    save_clicked = alert(
      content=EntryEdit(item=new_entry),
      title="Add Entry",
      large=True,
      buttons=[("Save", True), ("Cancel", False)],
    )
    # If the alert returned 'True', the save button was clicked.
    if save_clicked:
      anvil.server.call("add_entry", new_entry)
      self.refresh_entries()

  def refresh_entries(self):
    # Load existing entries from the Data Table,
    # and display them in the RepeatingPanel
    self.entries_panel.items = anvil.server.call("get_entries")

  def delete_entry(self, entry, **event_args):
    # Delete the entry
    anvil.server.call("delete_entry", entry)
    # Refresh entry to remove the deleted entry from the Homepage
    self.refresh_entries()

  def search_button_click(self, **event_args):
    search_text = self.search_box.text
    type = self.type_of_search.selected_value
    results = anvil.server.call("search_items", search_text, type)
    self.entries_panel.items = results

  def multi_select_drop_down_1_change(self, **event_args):
    selected = self.multi_select_drop_down_1.selected
    print(self.multi_select_drop_down_1.items)
    if selected and selected != "Select an amenity...":
      filtered_courses = anvil.server.call("get_courses_by_amenity", selected)
      self.entries_panel.items = filtered_courses

  def multi_select_drop_down_1_opened(self, **event_args):
    """This method is called when the dropdown menu is opened"""
    pass

  def link_1_click(self, **event_args):
    open_form("Homepage")
    pass
