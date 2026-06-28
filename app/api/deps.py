from app.db.session import get_db

# Re-exported here so routes import dependencies from one place (api/deps.py)
# rather than reaching into db/session.py directly. This is also where
# you'd add an auth dependency later, e.g. get_current_user.
__all__ = ["get_db"]
