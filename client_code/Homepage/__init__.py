from ._anvil_designer import HomepageTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..EntryEdit import EntryEdit
from ..EntryView import EntryView

class Homepage(HomepageTemplate):
  def __init__(self, **properties):
    self.images=app_tables.images.search()
    self.image_index=0
    self.image_1.source=self.images[self.image_index]['image']


    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
  
    
  def timer_1_tick(self, **event_args):
    with anvil.server.no_loading_indicator:
      self.image_1.source=self.images[self.image_index]['image']
      self.image_index += 1
      if self.image_index == len(self.images):
        self.image_index = 0

  
  


