import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.files
from anvil.files import data_files
import anvil.server
import sqlite3

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

def get_db(): 
    return data_files["database.db"]

@anvil.server.callable
def login(username, passwort):
  # Vulnerable SQL query
  query = f"SELECT username FROM Users WHERE username = '{username}' AND password = '{password}'"
  try:
      cursor = get_db().execute(query)
  except Exception as e:
      return f"Login failed!<br>{query}<br>{e}"

  user = cursor.fetchone()