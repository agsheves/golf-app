from ._anvil_designer import navlistTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class navlist(navlistTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_1_click(self, **event_args):
    open_form('Homepage')
    pass

  def link_2_click(self, **event_args):
    open_form('courses_page')
    pass

  def link_3_click(self, **event_args):
    open_form('About')
    pass

  def link_4_click(self, **event_args):
    open_form('Contact')
  pass
