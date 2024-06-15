from Juliet2_Schema import Cases, engine, VLW,VLW2
from sqlalchemy import and_, func, bindparam, text, String, Integer, Text
from sqlalchemy.orm import relationship, sessionmaker
import random

Session = sessionmaker(bind=engine)
session = Session()

# Query the database and get a list of Cases objects for each CWE
records = session.query(Cases).all()
def get_relative_location(vulnerable_location, start, end):
    # Adjust the vulnerable location to be relative to the start of the window
    relative_location = vulnerable_location - start
    return relative_location


# This takes a parameter window size, and returns two random  values for num lines before + after
def get_random_values(window_size):
    num_lines_before = random.randint(1, window_size - 1)
    num_lines_after = window_size - 1 - num_lines_before
    return num_lines_before, num_lines_after

for record in records:
    # Check if the record has only one vulnerability location
    if record.vulnerability_location.count(",") == 0:
        # Migrate the column names over to the VLW table
        vlw_name = record.file_name
        vlw_cwe = record.cwe
        model_id = record.model_id
        codeFile = record.file_content
        
        vulnerable_location = int(record.vulnerability_location)
    
        lines = codeFile.split("\n")
        vlw_lines = []
        window_size = 40
        updated_locations = []
    
        num_lines_before, num_lines_after = get_random_values(window_size)
        
        
        print("Scanning through records...")
        for line_number, line_content in enumerate(lines):
            if line_number == vulnerable_location:
                start = max(0, line_number - num_lines_before)  # Start of the window
                end = min(len(lines), line_number + num_lines_after + 1)  # End of the window
                vlw_lines.extend(lines[start:end])
                
                # Append the lines in the window to vlw_lines
                relative_location = get_relative_location(vulnerable_location, start, end)
                updated_locations.append(relative_location)

        delimiter = '\n'  # Use newline as the delimiter to preserve the original line breaks
        vlw_lines_str = delimiter.join(vlw_lines)
        # Now Call updated location    
        delimiter = ','  # Choose a suitable delimiter
        vulnerable_lines_str = delimiter.join(map(str, updated_locations))
            
        print("Ready to insert...")
        session.add(VLW2(
            file_name=vlw_name,
            cwe=vlw_cwe,
            cwe_int=0,  # Initialize cwe_int to handle cases with no vulnerabilities
            vulnerability_location=vulnerable_lines_str,
            vlw_content=vlw_lines_str,
            offset=0,  # Initialize offset
            model_id=model_id
        ))

session.commit()               
    
session.close()