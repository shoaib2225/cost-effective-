import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import separated logic
from fastapi.middleware.cors import CORSMiddleware
from database import (
    init_db, create_user, verify_user, search_meds, add_medicine, save_message, 
    get_all_meds, get_all_users, delete_user, get_all_messages, delete_message, 
    update_medicine, delete_medicine
)
from models import UserSignup, UserLogin, Medicine, ContactRequest
from analytics import generate_price_distribution_plot, perform_medicine_clustering, get_interactive_chart_data, get_market_statistics

app = FastAPI()

# Allow requests from all origins (cors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB when server boots
init_db()

@app.post("/api/auth/signup")
def signup(user: UserSignup):
    # Pass user data to the DB logic
    success = create_user(user.fullname, user.email, user.password)
    # If the database rejected it (e.g. duplicate email)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return {"message": "Signup successful and data saved into SQLite DB."}

@app.post("/api/auth/login")
def login(user: UserLogin):
    # Verify user via DB logic
    res = verify_user(user.email, user.password)
    if res:
        return {"message": "Login successful", "user": {"fullname": res['fullname'], "email": user.email}}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/medicines/search")
def search_medicines(q: str):
    # Retrieve medicines from DB
    results = search_meds(q)
    return results

@app.get("/api/medicines/all")
def all_medicines():
    return get_all_meds()

@app.post("/api/medicines")
def create_new_medicine(med: Medicine):
    # Convert alternative objects to dicts for JSON storage
    alternatives = [alt.model_dump() if hasattr(alt, 'model_dump') else alt.dict() for alt in med.alternatives]
    success = add_medicine(med.name, med.formula, med.price, med.company, alternatives)
    if success:
        return {"message": "Medicine added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add medicine")

@app.post("/api/contact")
def contact(req: ContactRequest):
    # Log user inquiry for backend terminal monitoring
    print("\n📩 [NEW CONTACT INQUIRY RECEIVED]")
    print(f"User Name: {req.name}")
    print(f"User email: {req.email}")
    print(f"Message: {req.description}")
    print("--------------------------------\n")
    
    # Save the information specifically to our SQLite DB
    success = save_message(req.name, req.email, req.description)
    
    if success:
        return {"message": "Your message has been successfully saved in our database."}
    
    raise HTTPException(status_code=500, detail="Failed to synchronize message to database")

@app.get("/api/analytics/plot")
def get_plot():
    plot_data = generate_price_distribution_plot()
    if plot_data:
        return {"image": plot_data}
    raise HTTPException(status_code=500, detail="Could not generate plot")

@app.get("/api/analytics/clusters")
def get_clusters():
    return perform_medicine_clustering()

@app.get("/api/analytics/chart")
def get_chart():
    return get_interactive_chart_data()

@app.get("/api/analytics/stats")
def get_stats():
    return get_market_statistics()

# ADMIN PANEL ENDPOINTS

@app.post("/api/admin/login")
def admin_login(user: UserLogin):
    # Simple admin check - in a production app this would use a secure methodology
    if user.email == "admin@gmail.com" and user.password == "admin123":
        return {"message": "Admin Login successful", "user": {"fullname": "System Administrator", "email": user.email, "is_admin": True}}
    raise HTTPException(status_code=401, detail="Invalid admin credentials")

@app.get("/api/admin/users")
def admin_get_users():
    return get_all_users()

@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int):
    if delete_user(user_id):
        return {"message": "User deleted"}
    raise HTTPException(status_code=500, detail="Failed to delete user")

@app.get("/api/admin/messages")
def admin_get_messages():
    return get_all_messages()

@app.delete("/api/admin/messages/{msg_id}")
def admin_delete_msg(msg_id: int):
    if delete_message(msg_id):
        return {"message": "Message deleted"}
    raise HTTPException(status_code=500, detail="Failed to delete message")

@app.put("/api/admin/medicines/{med_id}")
def admin_update_med(med_id: int, med: Medicine):
    alternatives = [alt.model_dump() if hasattr(alt, 'model_dump') else alt.dict() for alt in med.alternatives]
    if update_medicine(med_id, med.name, med.formula, med.price, med.company, alternatives):
        return {"message": "Medicine updated"}
    raise HTTPException(status_code=500, detail="Failed to update medicine")

@app.delete("/api/admin/medicines/{med_id}")
def admin_delete_med(med_id: int):
    if delete_medicine(med_id):
        return {"message": "Medicine deleted"}
    raise HTTPException(status_code=500, detail="Failed to delete medicine")

# Set the absolute path for frontend to be reliably served
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
