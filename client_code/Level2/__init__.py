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
    self.check_box_eingabe_sichern.checked = anvil.server.call('isSQLProof')
    
    url=anvil.js.window.location.href
    text = anvil.server.call('login_with_accountNumber', url)
    self.label_1.text = text
    print(text)

  def check_box_eingabe_sichern_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    anvil.server.call('change_sql_proof', state=self.check_box_eingabe_sichern.checked)
