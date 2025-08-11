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
  
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
  
    
  def link_1_click(self, **event_args):
    open_form("Homepage_copy")
    pass
     

  
  


