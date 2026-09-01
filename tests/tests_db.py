from app import db

print(
    db.query(
        "SELECT current_database() AS db, "
        "(SELECT COUNT(*)::int FROM chunks) AS chunks"
    )
)

db.pool.close()