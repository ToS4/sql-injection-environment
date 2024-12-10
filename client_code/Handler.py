from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

level = anvil.server.call('get_level')
print(level)

if level or level == 1:
  open_form('Level1')

if level == 2:
  open_form('Level2')
