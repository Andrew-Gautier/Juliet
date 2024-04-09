# Python
import sentencepiece as spm
import os
import re
import shutil
from sarif_om import SarifLog
import json

def remove_comments(root_dir):
    for dir_name, _, file_list in os.walk(root_dir):
        for file_name in file_list:
            if file_name.endswith(('.c', '.php', '.cpp', '.java', '.cs')):
                file_path = os.path.join(dir_name, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Remove single-line comments
                content = re.sub(r'//.*|^\s*#.*', '', content, flags=re.MULTILINE)

                # Remove multi-line comments
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

class SarifLog:
    def __init__(self, state, start_line, codepath):
        self.state = state
        self.start_line = start_line
        self.codepath = codepath

def read_sarif_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file, strict=False)

        # Extract the state and startLine from the data
        state = data['runs'][0]['properties']['state']
        start_line = data['runs'][0]['results'][0]['locations'][0]['physicalLocation']['region']['startLine']
        codepath = data['runs'][0]['results'][0]['locations'][0]['physicalLocation']['artifactLocation']['uri']  
        sarif_log = SarifLog(state, start_line, codepath)
    
        return sarif_log
    except Exception as e:
        print(f"Error decoding SARIF in file {file_path}: {e}")
        return None       

def extract_info(sarif_log):
    state = sarif_log.state
    start_line = sarif_log.start_line
    codepath = sarif_log.codepath  
    return state, start_line, codepath  

def sarifparser(root_dir, output_dir): 
    info_list = []
    for dir_name, _, file_list in os.walk(root_dir):
        for file_name in file_list:
            if file_name == 'manifest.sarif':
                file_path = os.path.join(dir_name, file_name)
                sarif_log = read_sarif_file(file_path)
                if sarif_log is None:
                    continue
                state, start_line, codepath = extract_info(sarif_log)  
                info_list.append((state, start_line, codepath))  
    return info_list        


def tokenize_file(file_path, sp):
    with open(file_path, 'r') as file:
        text = file.read()
    tokens = sp.encode_as_pieces(text)
    return tokens

def main():

    

    remove_comments(root_dir)
    # sarif_file_path = os.path.join(root_dir, 'manifest.sarif')
    # read_sarif_file(sarif_file_path)
    # extract_info(root_dir)
    # Call sarifparser function
    info_list = sarifparser(root_dir, output_dir)
    for info in info_list:
        print(info)
    # Train SentencePiece model
    file_paths = []
    for dir_name, _, file_list in os.walk(root_dir):
        for filename in file_list:
            if filename.endswith(('.cpp', '.php', '.cs', '.c', '.java')):
                file_path = os.path.join(dir_name, filename)
                file_path = str(file_path)  # Convert to raw string
                file_paths.append(file_path)
    try:
        with open(file_path, 'r') as file:
            pass
    except IOError:
        print(f"Cannot open file: {file_path}")

    file_paths = [file_path.replace(',', '_') for file_path in file_paths]
    with open('file_names.txt', 'w') as file:
        for file_path in file_paths:
            file.write(file_path + '\n')
    
    # Here is where I was having troubles, see https://stackoverflow.com/questions/77513113/sentencepiece-tokenizer-incorrectly-concatenating-input-files?noredirect=1#comment136728628_77513113
    # Update this may have been solved check the issue I created here: https://github.com/google/sentencepiece/issues/939#issuecomment-1868233193 
    spm.SentencePieceTrainer.train(f'--input={",".join(file_paths)} --model_prefix=m --vocab_size=499 --model_type=bpe')
 
    sp = spm.SentencePieceProcessor()
    sp.load('m.model')

    # Tokenize files
    for file_path in file_paths:
        tokens = tokenize_file(file_path, sp)
        output_filename = os.path.basename(file_path)
        # Note use 'a' for append mode
        with open(os.path.join(output_dir, output_filename), 'w', encoding='utf-8') as file:
            for token in tokens:
                file.write(token + '\n')

        # Insert tokens based on info_list
        # Info[2] = relative path to source code file
        for info in info_list:
            file_path = os.path.join(root_dir, info[2])
            with open(file_path, 'r+') as file:
                lines = file.readlines()
                if info[0] == 'good':
                    lines[info[1] - 1] = '<GOOD>' + lines[info[1] - 1]
                elif info[0] == 'bad':
                    lines[info[1] - 1] = '<BAD>' + lines[info[1] - 1]
                file.seek(0)
                file.writelines(lines)

if __name__ == '__main__':
    main()

