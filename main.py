# Python
import os
import fnmatch
import shutil

def find_source_code_files(directory, extensions):
    for root, dirnames, filenames in os.walk(directory):
        for extension in extensions:
            for filename in fnmatch.filter(filenames, '*.' + extension):
                yield os.path.join(root, filename)

# List of common source code file extensions
extensions = ['py', 'js', 'java', 'cpp', 'c', 'cs', 'go', 'rb', 'php']

# Replace 'your_directory' with the path to the directory you want to search
# Replace 'output_directory' with the path to the directory where you want to copy the files
for filename in find_source_code_files(r'C:\Users\Andrew\Desktop\C++ mini test', extensions):
    shutil.copy2(filename, r'C:\Users\Andrew\Desktop\Cleaned C++ mini output')