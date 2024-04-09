# Python
import os
import re
from sarif_om import SarifLog
import json
from Project_1.old_db_loader import Folder, SourceCodeFile, Manifest, Vulnerability, sessionmaker, engine
from sqlalchemy import text

def remove_comments(root_dir):
    for dir_name, _, file_list in os.walk(root_dir):
        for file_name in file_list:
            if file_name.endswith(('.c', '.php', '.cpp', '.java', '.cs')):
                file_path = os.path.join(dir_name, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                in_multi_line_comment = False

                for i, line in enumerate(lines):
                    # Handle multi-line comments
                    if '/*' in line:
                        in_multi_line_comment = True
                        lines[i] = re.sub(r'/\*.*$', '', line)
                        continue

                    if in_multi_line_comment:
                        if '*/' in line:
                            in_multi_line_comment = False
                            lines[i] = re.sub(r'^.*\*/', '', line)
                        else:
                            lines[i] = ''
                        continue

                    # Handle single-line comments
                    lines[i] = re.sub(r'//.*|^\s*#.*', '', line)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(lines)

def remove_files_except_code_and_sarif(root_dir):
                        code_extensions = ['.c', '.cpp', '.php', '.java', '.cs']
                        manifest_file = 'manifest.sarif'

                        for dir_name, _, file_list in os.walk(root_dir):
                            for file_name in file_list:
                                file_path = os.path.join(dir_name, file_name)
                                file_extension = os.path.splitext(file_name)[1]

                                if file_extension.lower() not in code_extensions and file_name != manifest_file:
                                    os.remove(file_path)
class SarifLog:
    def __init__(self, state, start_line, codepath):
        self.state = state
        self.start_line = start_line
        self.codepath = codepath

# 11-29 I am experimenting with using this class to store the information from the sarif file.
# class Info:
#     def __init__(self, state, start_line, codepath):
#         self.state = state
#         self.start_line = start_line
#         self.codepath = codepath        

def read_sarif_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file, strict=False)
    except IOError:
        print(f"Cannot open file: {file_path}")
        return []

    # Extract the state from the data
    state = data['runs'][0]['properties']['state']

    # Initialize an empty list to hold the SarifLog objects
    sarif_logs = []

    # Iterate over the results
    for result in data['runs'][0]['results']:
        # Iterate over the locations in each result
        for location in result['locations']:
            # Extract the startLine and codepath from the location
            start_line = location['physicalLocation']['region']['startLine']
            codepath = location['physicalLocation']['artifactLocation']['uri']

            # Create a new SarifLog object and add it to the list
            sarif_log = SarifLog(state, start_line, codepath)
            sarif_logs.append(sarif_log)

    return sarif_logs

def extract_info(sarif_logs):
    state = sarif_logs.state
    start_line = sarif_logs.start_line
    codepath = sarif_logs.codepath  
    return state, start_line, codepath  

def sarifparser(root_dir): 
    info_list = []
    for dir_name, _, file_list in os.walk(root_dir):
        for file_name in file_list:
            if file_name == 'manifest.sarif':
                file_path = os.path.join(dir_name, file_name)
                sarif_logs = read_sarif_file(file_path)
                if sarif_logs is None:
                    continue
                for sarif_log in sarif_logs:
                    state, start_line, codepath = extract_info(sarif_log)  
                    info_list.append((state, start_line, codepath))  
    return info_list



def main():
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(text("PRAGMA foreign_keys=ON"))
    root_dir = 'C:\\Users\\Andrew\\Desktop\\C# Vulnerability Test Suite (sample)'


    remove_files_except_code_and_sarif(root_dir)
    info_list = sarifparser(root_dir)
 
    new_folder = Folder(folder_name='C# Vulnerability Test Suite (sample)')
    session.add(new_folder)
    session.commit()
    session.execute(text("PRAGMA foreign_keys=ON"))
    # Walk the directory structure once
    for dirpath, _, filenames in os.walk(root_dir):
        for file_name in filenames:
            file_extension = os.path.splitext(file_name)[1]
            path = os.path.join(dirpath, file_name)
            with open(path, 'r') as file_obj:
                file_content = file_obj.read()

            new_file = SourceCodeFile(folder=new_folder, file_name= file_name, file_extension=file_extension, file_content=file_content)
            session.add(new_file)
            new_manifest = Manifest(source_code_file=new_file, sarif_content=file_content)
            session.add(new_manifest)
            session.commit()
            session.execute(text("PRAGMA foreign_keys=ON"))
            for info in info_list:
                state, start_line, codepath = info
                
                if os.path.basename(codepath) == file_name:
                    existing_vulnerability = session.query(Vulnerability).filter_by(manifest_id=new_manifest.manifest_id, line_number=start_line, vulnerability_type=state).first()
                    if not existing_vulnerability:
                        new_vulnerability = Vulnerability(manifest_id=new_manifest.manifest_id, line_number=start_line, vulnerability_type=state)
                        session.add(new_vulnerability)
 

    session.commit()
    session.execute(text("PRAGMA foreign_keys=ON"))

if __name__ == '__main__':
    main()
    
