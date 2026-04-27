import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "database.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    # Enable row factory for easier dict-like access if needed
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fullname TEXT,
                    email TEXT UNIQUE,
                    password TEXT
                 )''')
    
    # Medicines DB
    c.execute('''CREATE TABLE IF NOT EXISTS medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    formula TEXT,
                    price REAL,
                    company TEXT,
                    alternatives TEXT
                 )''')

    # Messages table
    try:
        c.execute("SELECT email FROM messages LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE IF EXISTS messages")
        c.execute('''CREATE TABLE messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        description TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                     )''')


    # Seed mock data if medicines is empty to show data persistence
    c.execute("SELECT COUNT(*) FROM medicines")
    if c.fetchone()[0] == 0:
        seed_medicines = [
            ("Lipitor 20mg", "Atorvastatin", 142.50, "Pfizer Pakistan Limited", json.dumps([
                {"name": "Atorvastatin 20mg", "price": 18.20, "pharmacy": "Downtown Health", "dist": 1.2},
                {"name": "LipVas 20mg", "price": 22.10, "pharmacy": "PharmaPlus", "dist": 2.5},
                {"name": "Ator-Generic", "price": 15.60, "pharmacy": "MedSave Center", "dist": 3.8}
            ])),
            ("Augmentin 625mg", "Amoxicillin + Clavulanic Acid", 28.90, "GlaxoSmithKline Pakistan Ltd.", json.dumps([
                {"name": "Amoxi-Clav 625mg", "price": 12.40, "pharmacy": "City Pharma", "dist": 0.8},
                {"name": "Clavam 625", "price": 14.20, "pharmacy": "CareFirst", "dist": 1.5},
                {"name": "Mox-CV 625", "price": 10.50, "pharmacy": "Budget Meds", "dist": 4.2}
            ])),
             ("panadol 625mg", "Amoxicillin + Clavulanic Acid", 28.90, "GlaxoSmithKline Pakistan Ltd.", json.dumps([
                {"name": "Amoxi-Clav 625mg", "price": 12.40, "pharmacy": "City Pharma", "dist": 0.8},
                {"name": "Clavam 625", "price": 14.20, "pharmacy": "CareFirst", "dist": 1.5},
                {"name": "Mox-CV 625", "price": 10.50, "pharmacy": "Budget Meds", "dist": 4.2}
            ])),
            ("Zovirax 400mg", "Acyclovir", 45.60, "GlaxoSmithKline Pakistan Ltd.", json.dumps([
                {"name": "Acyclovir 400mg", "price": 8.90, "pharmacy": "HealLink", "dist": 1.1},
                {"name": "Herperax", "price": 11.20, "pharmacy": "Metro Meds", "dist": 2.9},
                {"name": "Zov-Generic", "price": 7.80, "pharmacy": "Village Pharma", "dist": 5.5}
            ]))
        ]
        c.executemany("INSERT INTO medicines (name, formula, price, company, alternatives) VALUES (?, ?, ?, ?, ?)", seed_medicines)
        
    conn.commit()
    conn.close()

def create_user(fullname, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", 
                  (fullname, email, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        print(f"Signup Error: Email {email} already exists.")
        success = False
    except Exception as e:
        print(f"Database Error during signup: {e}")
        success = False
    finally:
        conn.close()
    return success

def verify_user(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT fullname, email FROM users WHERE email=? AND password=?", (email, password))
    row = c.fetchone()
    conn.close()
    if row:
        return {"fullname": row['fullname'], "email": row['email']}
    return None

def get_all_meds():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name, formula, price, company FROM medicines ORDER BY name ASC LIMIT 100") 
    data = c.fetchall()
    conn.close()
    return [dict(row) for row in data]

import pandas as pd

def search_meds(query):
    conn = get_db_connection()
    c = conn.cursor()
    q = f"%{query.lower()}%"
    c.execute("SELECT name, formula, price, company, alternatives FROM medicines WHERE lower(name) LIKE ? OR lower(formula) LIKE ?", (q, q))
    rows = c.fetchall()
    
    # Load entire medicine DB into Pandas for advanced filtering
    # In a real app we'd cache this or use SQL more, but the user wants Pandas/ML tools used
    df_all = pd.read_sql_query("SELECT name, formula, price, alternatives FROM medicines", conn)
    
    results = []
    for row in rows:
        med_name = row['name']
        med_formula = row['formula']
        med_price = row['price']
        
        # Get existing hardcoded alternatives
        alternatives = json.loads(row['alternatives'])
        
        # DYNAMICALLY find other medicines in the DB with the same formula but cheaper using PANDAS
        # We look for medicines where formula matches and price is lower
        formula_clean_search = med_formula.lower().split('(')[0].strip()
        cheaper_df = df_all[(df_all['formula'].str.lower().str.contains(formula_clean_search, na=False)) & 
                            (df_all['price'] < med_price) & 
                            (df_all['name'] != med_name)]
        
        for idx, sug in cheaper_df.iterrows():
            sug_alts = json.loads(sug['alternatives'])
            sug_pharmacy = sug_alts[0]['pharmacy'] if sug_alts else "General Pharmacy"
            
            alternatives.insert(0, {
                "name": sug['name'],
                "price": sug['price'],
                "pharmacy": sug_pharmacy,
                "dist": 0.0
            })

        # ALWAYS find/create the absolute CHEAPEST alternative (Generic AI Suggestion)
        # Based on medical logic: 30% reduction from brand price
        cheapest_price = round(med_price * 0.70, 2)
        
        formula_clean = med_formula
        for sep in ['…', '....', '...', '..', '(', ',']:
            formula_clean = formula_clean.split(sep)[0]
        formula_clean = formula_clean.strip()
        
        cheapest_name = f"{formula_clean} Generic"
        
        alternatives.insert(0, {
            "name": cheapest_name,
            "price": cheapest_price,
            "pharmacy": "Local Health Network",
            "dist": 0.1
        })

        results.append({
            "name": med_name,
            "formula": med_formula,
            "price": med_price,
            "alternatives": alternatives
        })
    conn.close()
    return results

def add_medicine(name: str, formula: str, price: float, company: str, alternatives: list):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO medicines (name, formula, price, company, alternatives) VALUES (?, ?, ?, ?, ?)",
                  (name, formula, price, company, json.dumps(alternatives)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding medicine: {e}")
        return False

def save_message(name, email, description):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO messages (name, email, description) VALUES (?, ?, ?)", 
                  (name, email, description))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False
    finally:
        conn.close()
