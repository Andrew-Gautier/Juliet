import xml.etree.ElementTree as ET
from Juliet_DB_loader import Folder, SubFolder, TestCase, sessionmaker, engine
import os
import glob

def parse_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    info_list = []

    for testcase in root.iter('testcase'):
        for file in testcase.iter('file'):
            file_path = file.get('path')
            cwe = None
            start_lines = []
            for flaw in file.iter('flaw'):
                cwe = flaw.get('name')
                start_line = flaw.get('line')
                if start_line is not None:
                    start_lines.append(start_line)
            if cwe is not None and start_lines:
                info_list.append((cwe, start_lines, file_path))

    return info_list


def subfolder_maker(root_dir):
    subfolder_paths = []
    for root, dirs, files  in os.walk(root_dir):
        for dir in dirs:
            subfolder_path = os.path.join(root, dir)
            subfolder_paths.append(subfolder_path)
    return subfolder_paths

def test_case_filepath(subfolder_path):
    filepaths = []
    for extension in ['*.java', '*.c', '*.cpp']:
        for file_path in glob.glob(os.path.join(subfolder_path, extension)):
            if os.path.basename(file_path).startswith('CWE'):
                filepaths.append(file_path)
    return filepaths

def main():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Initialize Folder
    new_folder = Folder(folder_name='Juliet Java')
    session.add(new_folder)
    session.commit()
    #Initialize SubFolders
    subfolder_paths = subfolder_maker('C:\\Users\\Andrew\\OneDrive\\Documents\\Juliet Java 1.3\\src\\testcases')
    for path in subfolder_paths:
        new_subfolder = SubFolder(folder_name=path, parent_folder_id=new_folder.id)
        session.add(new_subfolder)
    session.commit()
    # Initialize TestCases 
    # Parse the XML file
    xml_file_path = 'C:\\Users\\Andrew\\OneDrive\\Documents\\Juliet Java 1.3\\manifest.xml'
    info_list = parse_xml(xml_file_path)
    
    # Create a dictionary from info_list
    info_dict = {os.path.basename(codepath): (cwe, start_line) for cwe, start_line, codepath in info_list}

    print("Starting loop over subfolders")
    for subfolder in new_folder.subfolders:
        print(f"Processing subfolder: {subfolder.folder_name}")
        filepaths = test_case_filepath(subfolder.folder_name)
        for filepath in filepaths:
            print(f"Processing file: {filepath}")
            # Look up the CWE and start line in info_dict
            info = info_dict.get(os.path.basename(filepath))
            if info is not None:
                cwe, start_lines = info
                start_lines_str = ','.join(start_lines)
                try:
                    print(f"Creating TestCase for file: {filepath}")
                    new_test_case = TestCase(
                        subfolder_id=subfolder.id,
                        file_name=os.path.basename(filepath),
                        file_extension=os.path.splitext(filepath)[1],
                        file_content=open(filepath, 'r').read(),
                        cwe=cwe,
                        vulnerability_location=start_lines_str
                    )
                    session.add(new_test_case)
                except Exception as e:
                    print(f"Exception caught: {e}")
    print("Finished loop over subfolders")
    session.commit()

if __name__ == '__main__':
    main()