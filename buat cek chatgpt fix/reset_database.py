from app import app, db

def reset_all_tables():
    with app.app_context():
        # ... existing code ... 