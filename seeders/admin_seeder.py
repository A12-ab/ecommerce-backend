import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash
from app.database import Base


def seed_admin():
    """Seed admin user"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            print("Admin user already exists")
            return

        # Create admin user with a password within bcrypt's 72-byte limit
        admin_password = "admin123"  # 8 characters, well within limit
        admin = User(
            email="admin@example.com",
            password_hash=get_password_hash(admin_password),
            name="Admin User",
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print(f"Password: {admin_password}")
    except Exception as e:
        print(f"Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
