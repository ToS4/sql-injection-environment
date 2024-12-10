from ._anvil_designer import Level1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class Level1(Level1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.check_box_eingabe_sichern.checked = anvil.server.call('isSQLProof')

  def check_box_eingabe_sichern_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    anvil.server.call('change_sql_proof', state=self.check_box_eingabe_sichern.checked)

  def button_anmelden_click(self, **event_args):
    """This method is called when the button is clicked"""
    state, response = anvil.server.call('login', self.text_box_username.text, self.text_box_passwort.text)
    self.label_response.text = response
    if state == 1:
      if isinstance(response, list):
        anvil.js.window.location.href += "?AccountNo=" + str(response[0])
      open_form("Level2")
    elif state == 2:
      print("Done")