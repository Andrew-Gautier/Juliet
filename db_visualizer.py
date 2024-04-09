import matplotlib.pyplot as plt
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from Juliet_DB_loader import Folder, SubFolder, TestCase, sessionmaker, engine

# List of file extensions
extensions = ['.c', '.java', '.cpp', '.cs']  # Removed '.php'

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Query the test_cases table
test_files = session.query(TestCase.file_extension, func.count(TestCase.file_extension)).group_by(TestCase.file_extension).all()

# Prepare data for the bar chart
languages = [row[0] for row in test_files]
counts = [row[1] for row in test_files]

# Create the bar chart
plt.bar(languages, counts)
plt.xlabel('Languages')
plt.ylabel('Number of Test Cases')
plt.title('Test Cases per Language')
plt.show()

# Close the session
session.close()