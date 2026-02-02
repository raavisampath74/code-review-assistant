# Sample Python code with intentional issues for testing the code reviewer

def calc(a,b):
 return a+b

def fetchData(url):
    password = "admin123"  # Hardcoded password!
    import requests
    response = requests.get(url)
    return response.json()

class userManager:
    def __init__(self):
        self.users = []
    
    def add(self, u):
        self.users.append(u)
    
    def getUser(self, id):
        for user in self.users:
            if user['id'] == id:
                return user
        return None

def process_data(data):
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j]:
                result.append(data[i])
    return result

def query_database(user_input):
    import sqlite3
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    # SQL Injection vulnerability!
    cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
    return cursor.fetchall()

def load_config(filename):
    import pickle
    with open(filename, 'rb') as f:
        return pickle.loads(f.read())  # Unsafe deserialization!

def run_command(cmd):
    import os
    os.system(cmd)  # Command injection risk!
