from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

loggedIn = anvil.server.call('get_login_state')

if not loggedIn:
  open_form('Level1')
else:
  url =  anvil.js.window.location.href
  state = anvil.server.call('get_accountNumber_from_query', url)
  if not state:
    accountNo = anvil.server.call('get_accountNo')
    if accountNo:
      anvil.js.window.location.href += "?AccountNo=" + str(accountNo)
  open_form("Level2")
