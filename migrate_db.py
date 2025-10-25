from app import app, db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        try:
            # Check if service_type column exists
            inspector = db.inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('user')]
            
            if 'service_type' not in cols:
                print("Adding service_type column to user table...")
                with db.engine.connect() as conn:
                    if 'sqlite' in db.engine.url.drivername:
                        conn.execute(text("ALTER TABLE user ADD COLUMN service_type VARCHAR(100)"))
                    else:
                        conn.execute(text("ALTER TABLE user ADD COLUMN service_type VARCHAR(100)"))
                    conn.commit()
                print("Migration completed successfully!")
            else:
                print("service_type column already exists.")
                
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate_database()