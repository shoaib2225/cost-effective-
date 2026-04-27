import pandas as pd
import sqlite3
import os
import json
from database import init_db, DB_FILE

CSV_FILE = os.path.join(os.path.dirname(__file__), "file.csv")

def clean_price(price_str):
    if pd.isna(price_str) or not price_str:
        return 0.0
    # Strip "Rs. ", commas, and whitespace
    clean_str = str(price_str).replace("Rs.", "").replace(",", "").strip()
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def import_csv():
    # Initialize DB schema first
    init_db()
    
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    # Use Pandas to read CSV
    df = pd.read_csv(CSV_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    
    # Process each row
    medicines_to_insert = []
    for _, row in df.iterrows():
        brand = row.get('Brand Name')
        formula = row.get('Formulation')
        company = row.get('Company Name')
        mrp = row.get('MRP')

        if not brand or not formula:
            continue

        price = clean_price(mrp)
        
        # Create a mock alternative
        formula_base = str(formula).split('(')[0].split('...')[0].strip()
        alternatives = [
            {
                "name": f"Generic {formula_base}",
                "price": round(price * 0.7, 2),
                "pharmacy": f"Regional Health Network",
                "dist": 1.0
            }
        ]

        medicines_to_insert.append((brand, formula, price, company, json.dumps(alternatives)))

    # Use executemany for performance
    c = conn.cursor()
    c.executemany("INSERT INTO medicines (name, formula, price, company, alternatives) VALUES (?, ?, ?, ?, ?)", 
                  medicines_to_insert)
    
    conn.commit()
    conn.close()
    print(f"Successfully imported {len(medicines_to_insert)} medicines using Pandas.")

if __name__ == "__main__":
    import_csv()
