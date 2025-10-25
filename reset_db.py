from app import app, db, User, Service, ServiceProvider, ServiceRequest, ClientResponse

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        print("Database reset complete!")
        
        # Reinitialize with sample data
        from app import initialize_database
        initialize_database()

if __name__ == '__main__':
    reset_database()