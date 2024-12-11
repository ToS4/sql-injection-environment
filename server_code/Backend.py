import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.files
from anvil.files import data_files
import anvil.server
import sqlite3
import requests
import urllib
import re

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
def get_login_state():
  if "login" in anvil.server.session:
    return anvil.server.session["login"]
  return False

@anvil.server.callable
def get_accountNo():
  if "accountNo" in anvil.server.session:
    return anvil.server.session["accountNo"]
  return None
  
@anvil.server.callable
def change_sql_proof(state):
  print(state)
  anvil.server.session["sqlProof"] = state

@anvil.server.callable
def isSQLProof():
  if "sqlProof" not in anvil.server.session:
    anvil.server.session["sqlProof"] = False
  return anvil.server.session["sqlProof"]
  

@anvil.server.callable
def login(username, passwort):
  if isSQLProof():
    pattern = r'^[a-zA-Z0-9]+$'
    if not re.match(pattern, username):
      return 0, "Error: Username should only contain letters and numbers!"
  
    connection = sqlite3.connect(data_files["database.db"])
    cursor = connection.cursor()
    
    try:
      cursor.execute(
        "SELECT Username, IsAdmin FROM Users WHERE Username = ? AND Password = ?",
        (username, passwort)
      )
      user = cursor.fetchone()
      
      if not user:
        connection.close()
        return 0, "Login failed! Invalid username or password."
      
      accountNo = None
      anvil.server.session['login'] = True
      
      if user[0] == username:
        cursor.execute(
          "SELECT AccountNo FROM Users WHERE Username = ?",
          (username,)
        )
        accountNo = cursor.fetchone()

      if user[0] == username and user[1] == 1:
        cursor.execute(
          "SELECT Password FROM Users WHERE Username = ? AND Password = ?",
          (username, passwort)
        )
        pw = cursor.fetchone()
        if pw and passwort == pw[0]:
          connection.close()
          return 2, "Congratulations you finished the task!"

      anvil.server.session["accountNo"] = accountNo[0]
      connection.close()
      return 1, accountNo
    except Exception as e:
      connection.close()
      return 0, f"Login failed! Error: {e}"
      
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
  anvil.server.session['login'] = True
  if user and username == user[0]:
    accountNo = cursor.execute(f"SELECT AccountNo FROM Users WHERE Username = '{username}'").fetchone()
  if user and username == user[0] and user[1] == 1:
    query = f"SELECT Password FROM Users WHERE Username = '{username}' AND Password = '{passwort}'"
    pw = cursor.execute(query).fetchone()
    if pw and passwort == pw[0]:
      connection.close()
      return 2, "Congratulations you finished the task!"
  if user:
    anvil.server.session["accountNo"] = accountNo[0]
    connection.close()
    return 1, accountNo
  else:
    connection.close()
    return 0, f"Login failed! {query}"
  

@anvil.server.callable
def get_accountNumber_from_query(url):
  query_string = url.split('?')[-1] if '?' in url else ''
  if query_string:
    query_params = urllib.parse.parse_qs(query_string)
    if "AccountNo" in query_params:
      return query_params["AccountNo"][0]
  return None


@anvil.server.callable
def login_with_accountNumber(url):
  loggedIn = get_login_state()
  
  if not loggedIn:
    return "Not Logged in!"

  AccountNo = get_accountNumber_from_query(url)

  if isSQLProof():
    pattern = r'^[0-9]+$'
    if not re.match(pattern, AccountNo):
        return "Error: AccountNo should only contain numbers!"

  connection = sqlite3.connect(data_files["database.db"])
  cursor = connection.cursor()
  
  if AccountNo:
    query_balance = f"SELECT Balance FROM Balances WHERE AccountNo = {AccountNo}"
    query_user = f"SELECT Username FROM Users WHERE AccountNo = {AccountNo}"

    try:
      balance = cursor.execute(query_balance).fetchall()
      user = cursor.execute(query_user).fetchall()
    except Exception as e:
      connection.close()
      return f"User not found.{query_user} {query_balance} {e}"

    user = [u[0] for u in user if isinstance(u, tuple)]
    balance = [b[0] for b in balance if isinstance(b, tuple)]
    user = user[0] if len(user) == 1 else user
    balance = balance[0] if len(balance) == 1 else balance

    if user:
      connection.close()
      return f"Welcome {user}! Your balance is {balance}."
    else:
      connection.close()
      return f"User not found. {query_user} {query_balance}"

  connection.close()
  return "Login successful but 'AccountNo' was not passed."

@anvil.server.http_endpoint("/", methods=["POST"])
def login_via_http_post():
    request = anvil.server.request

    json_data = request.json
    if json_data:
        name = json_data.get("username")
        age = json_data.get("password")
        return {"message": f"Hello {name}, you are {age} years old."}

    raw_body = request.body.get_bytes().decode("utf-8")
    return {"message": "Received raw data", "data": raw_body}