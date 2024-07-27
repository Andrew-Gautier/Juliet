from Juliet_DB_loader import TestCase, Folder, SubFolder, sessionmaker, engine
from sqlalchemy import and_, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from comment_cleaner import strip
from comment_cleaner import remove_empty_lines
import random, os
Session = sessionmaker(bind=engine)
session = Session()

def get_test_cases(session, file_extension, num_cases):
    query = session.query(TestCase)

    test_cases = query.filter(TestCase.file_extension == file_extension).limit(num_cases).all()

    test_case_ids = [test_case.id for test_case in test_cases]
    return test_cases, test_case_ids

c_test_cases, c_ids = get_test_cases(session, '.c', 3000)
cpp_test_cases, cpp_ids = get_test_cases(session, '.cpp', 3000)
java_test_cases, java_ids = get_test_cases(session, '.java', 3000)

all_cases = c_test_cases + cpp_test_cases + java_test_cases
corpus_file_path = 'test_cases_RCM/corpus.txt'

os.makedirs('test_cases_RCM', exist_ok=True)
for i, case in enumerate(all_cases):
    # Process the file content
    lines = case.file_content.split('\n')
    case.file_content = '\n'.join(lines)

    # Write the processed content to a new file
    with open(f'test_cases_RCM/test_case_{i}.txt', 'w') as f:
        f.write(case.file_content)

    # Append the processed content to the corpus file
    with open(corpus_file_path, 'a', encoding='utf-8') as corpus_file:
        corpus_file.write(case.file_content + '\n')
