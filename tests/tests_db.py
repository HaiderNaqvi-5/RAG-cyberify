from app import db

rows = db.query("SELECT current_database() AS db, COUNT(*)::int AS chunks FROM chunks;")

print(rows)