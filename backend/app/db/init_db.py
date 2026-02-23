"""Database initialization utilities."""
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User


def init_db(db: Session) -> None:
    """Initialize database with default data."""
    # Check if admin user exists
    admin = db.query(User).filter(User.username == "admin").first()

    if not admin:
        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@surveillance.dev",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        print("Created default admin user: admin / admin123")

    # Check if demo security user exists
    demo_user = db.query(User).filter(User.username == "security").first()

    if not demo_user:
        security_user = User(
            username="security",
            email="security@surveillance.dev",
            password_hash=get_password_hash("security123"),
            role="security_personnel",
            is_active=True,
        )
        db.add(security_user)
        db.commit()
        print("Created demo security user: security / security123")
