from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Juliet2_Schema import Cases, VLW  # Import your SQLAlchemy models
import os


DATABASE_FILE = '/users/aeg00011/Juliet/Juliet2.db'

DATABASE_URL = f'sqlite:///{DATABASE_FILE}'
engine = create_engine(DATABASE_URL)

# Create a session maker
Session = sessionmaker(bind=engine)

# Function to create a session
def create_session():
    return Session()