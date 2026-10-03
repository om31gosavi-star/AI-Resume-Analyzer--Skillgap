"""Rebuild the database from database/schema.sql + database/seed.sql.
Usage: python init_db.py"""
import db

db.init_db(force=True)
print("Database created at", db.DB_PATH)
