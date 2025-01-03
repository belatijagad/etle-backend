# scripts/cleanup.py
import os
import sys
import shutil

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlmodel import Session, SQLModel
from app.core.db import engine, init_db
from app.core.config import settings

def cleanup_database():
  print("Cleaning up database...")
  
  # Close all connections
  engine.dispose()
  
  # Remove the database file
  db_path = os.path.join(project_root, "sql_app.db")
  if os.path.exists(db_path):
    os.remove(db_path)
    print("Existing database file removed.")
  
  # Initialize fresh database
  init_db()
  print("Database cleaned and reinitialized successfully!")

def cleanup_images():
  print("Cleaning up uploaded images...")
  # Clean uploaded images
  uploads_dir = os.path.join(project_root, settings.UPLOAD_DIR)
  if os.path.exists(uploads_dir):
    shutil.rmtree(uploads_dir)
  os.makedirs(uploads_dir)
  print("Uploaded images directory cleaned and recreated!")

  print("Cleaning up predicted images...")
  # Clean predicted/cropped images
  cropped_dir = os.path.join(project_root, settings.CROPPED_IMAGES_DIR)
  if os.path.exists(cropped_dir):
    shutil.rmtree(cropped_dir)
  os.makedirs(cropped_dir)
  print("Predicted images directory cleaned and recreated!")

def main():
  print("Starting cleanup process...")
  try:
    cleanup_database()
    cleanup_images()
    print("Cleanup completed successfully!")
  except Exception as e:
    print(f"Error during cleanup: {str(e)}")
    raise e

if __name__ == "__main__":
  main()