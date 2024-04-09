from Juliet2_Schema import Cases, engine, VLW
from sqlalchemy import and_, func, bindparam, text, String, Integer, Text
from sqlalchemy.orm import relationship, sessionmaker
import random

Session = sessionmaker(bind=engine)
session = Session()

# Query the database and get a list of Cases objects for each CWE
records = session.query(Cases).all()



def update_locations(vulnerable_locations, num_lines_before,  window_size):
    # Update the vulnerable locations to include the surrounding lines
    updated_locations = []
    for location in vulnerable_locations:
        # Adjust the location based on the window size
        adjusted_location = location - num_lines_before
        # Ensure the adjusted location is within the window
        if 0 <= adjusted_location < window_size:
            updated_locations.append(adjusted_location)
    return updated_locations

# This takes a parameter window size, and returns two random  values for num lines before + after
def get_random_values(window_size):
    num_lines_before = random.randint(1, window_size - 1)
    num_lines_after = window_size - 1 - num_lines_before
    return num_lines_before, num_lines_after

for record in records:
    # Migrate the column names over to the VLW table
    vlw_name = record.file_name
    vlw_cwe = record.cwe
    model_id = record.model_id
    codeFile = record.file_content
    
    vulnerable_lines = []
    vulnerable_lines.extend(int(v) for v in record.vulnerability_location.split(","))
    print(vulnerable_lines)
    #print(vlw_name, vlw_cwe, vulnerable_lines)

    
    lines = codeFile.split("\n")
    vlw_lines = []
    window_size = 40
    updated_locations = []
    
    num_lines_before, num_lines_after = get_random_values(window_size)
    updated_locations = update_locations(vulnerable_lines, num_lines_before, window_size)
    
    cwe_int = 0  # Initialize cwe_int to handle cases with no vulnerabilities
    offset = 0  # Initialize offset
    print("Scanning through records...")
    for line_number, line_content in enumerate(lines):
        if line_number in vulnerable_lines:
            start = max(0, line_number - num_lines_before)  # Start of the window
            end = min(len(lines), line_number + num_lines_after + 1)  # End of the window
            vlw_lines.extend(lines[start:end])  # Append the lines in the window to vlw_lines

          
    delimiter = '\n'  # Use newline as the delimiter to preserve the original line breaks
    vlw_lines_str = delimiter.join(vlw_lines)
        
    delimiter = ','  # Choose a suitable delimiter
    
    vulnerable_lines_str = delimiter.join(map(str, updated_locations))
         
    print("Ready to insert...")
    session.add(VLW(
        file_name=vlw_name,
        cwe=vlw_cwe,
        cwe_int=cwe_int,
        vulnerability_location=vulnerable_lines_str,
        vlw_content=vlw_lines_str,
        offset=offset,
        model_id=model_id
    ))

# Commit the changes
session.commit()               
    
session.close()          
                    






        