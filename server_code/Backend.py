import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.files
from anvil.files import data_files
import anvil.server
import sqlite3
import requests

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

@anvil.server.callable
def login(username, passwort):
  connection = sqlite3.connect(data_files["database.db"])
  cursor = connection.cursor()

  # Vulnerable SQL query
  query = f"SELECT Username, IsAdmin FROM Users WHERE Username = '{username}' AND Password = '{passwort}'"
  try:
      cursor.execute(query)
  except Exception as e:
      return 0, f"Login failed! {query} {e}"

  user = cursor.fetchone()
  accountNo = None
  anvil.server.session["redirected"] = False
  if user and username == user[0]:
      accountNo = cursor.execute(f"SELECT AccountNo FROM Users WHERE Username = '{username}'").fetchone()
  if user and username == user[0] and user[1] == 1:
      query = f"SELECT Password FROM Users WHERE Username = '{username}' AND Password = '{passwort}'"
      pw = cursor.execute(query).fetchone()
      if pw and passwort == pw[0]:
          return 2, "Congratulations you finished the task!"
  if user:
      anvil.server.session['redirected'] = True
      return 1, accountNo
  else:
      return 0, f"Login failed! {query}"

@anvil.server.callable
def login_with_accountNumber():
  redirected = anvil.server.session["redirected"]
  if not redirected:
    return False, "Not Logged in!"
  
  response = requests.get("https://sql-injection-by-mohi.anvil.app/users")
  print(response.json())