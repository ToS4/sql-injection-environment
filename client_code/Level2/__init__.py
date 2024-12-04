from ._anvil_designer import Level2Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Level2(Level2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    text = anvil.server.call('get_server_msg')
    self.label_1.text = text
    print(text)
