"""
Seed Script — Insert default data into the database.
Run once after creating tables: python -m db.seed
"""

from db.database import get_db_session, init_db
from db.models import User, AlertCriteria

# Using bcrypt: pip install bcrypt
# For now, we'll use a placeholder hash. Replace with real bcrypt in production.
DEFAULT_PASSWORD_HASH = "$2b$12$LJ3m4ys3Lz0QBz0z0z0z0OeX0X0X0X0X0X0X0X0X0X0X0X0X0X0"


def seed():
    init_db()

    with get_db_session() as db:
        # ── Default Users ─────────────────────────────────
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(
                username="admin",
                password_hash=DEFAULT_PASSWORD_HASH,
                role="admin",
                full_name="System Administrator",
            ))
            print("✓ Created default admin user (admin / change_me)")

        if not db.query(User).filter_by(username="security01").first():
            db.add(User(
                username="security01",
                password_hash=DEFAULT_PASSWORD_HASH,
                role="security_personnel",
                full_name="Security Officer 1",
            ))
            print("✓ Created default security user (security01 / change_me)")

        # ── Default Alert Criteria (from Table 5.1 in report) ──
        default_rules = [
            {"behavior_type": "running",    "min_confidence": 0.7, "priority": "HIGH"},
            {"behavior_type": "falling",    "min_confidence": 0.7, "priority": "HIGH"},
            {"behavior_type": "suspicious", "min_confidence": 0.8, "priority": "HIGH"},
            {"behavior_type": "bending",    "min_confidence": 0.6, "priority": "MEDIUM"},
            {"behavior_type": "walking",    "min_confidence": 0.5, "priority": "LOW"},
            {"behavior_type": "standing",   "min_confidence": 0.5, "priority": "LOW"},
            {"behavior_type": "sitting",    "min_confidence": 0.5, "priority": "LOW"},
        ]

        existing = db.query(AlertCriteria).count()
        if existing == 0:
            for rule in default_rules:
                db.add(AlertCriteria(**rule))
            print(f"✓ Created {len(default_rules)} default alert criteria rules")

    print("\n✓ Database seeding complete!")


if __name__ == "__main__":
    seed()
