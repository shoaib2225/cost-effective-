from database import add_medicine
import json

# Add a much cheaper version of Lipitor (Atorvastatin)
add_medicine("Atorva Generic 20mg", "Atorvastatin", 35.0, [
    {"name": "Generic Atorva", "price": 32.0, "pharmacy": "City Health", "dist": 0.5}
])

# Add a cheaper version of Augmentin
add_medicine("Amoxi-Clav 625mg Plus", "Amoxicillin + Clavulanic Acid", 18.0, [
    {"name": "Amoxi Cost-Saver", "price": 14.0, "pharmacy": "Budget Meds", "dist": 4.1}
])

print("Test data inserted successfully.")
