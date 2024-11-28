from ._anvil_designer import LoginPageTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class LoginPage(LoginPageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def check_box_eingabe_sichern_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    pass

  def button_anmelden_click(self, **event_args):
    """This method is called when the button is clicked"""
    state, response = anvil.server.call('login', self.text_box_username.text, self.text_box_passwort.text)
    self.label_response.text = response
    if state == 1:
      open_form("LoggedInPage", response=response)
    elif state == 2:
      print("Done")