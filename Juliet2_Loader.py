import rcmpy
from Juliet_DB_loader import TestCase, engine as engine1
from Juliet2_Schema import Cases, engine as engine2
from sqlalchemy.orm import sessionmaker
# Create sessions for Juliet1.0 and 2.0
Session1 = sessionmaker(bind=engine1)
Juliet1 = Session1()


Session2 = sessionmaker(bind=engine2)
Juliet2 = Session2()

# Helper Functions

def assign_id(cases, split):
    # Calculate the number of cases for each set
    num_cases = len(cases)
    num_training = int(num_cases * split[0] / 100)
    num_testing = int(num_cases * split[1] / 100)
    num_validation = num_cases - num_training - num_testing

    # Split the cases into training, testing, and validation sets
    training_cases = cases[:num_training]
    testing_cases = cases[num_training:num_training + num_testing]
    validation_cases = cases[num_training + num_testing:]

    return [training_cases, testing_cases, validation_cases]

# Query all TestCase instances from the Juliet1 database
cases = Juliet1.query(TestCase).all()
#print(len(cases))

# Separate the cases by language
cases_by_language = {
    'c': [case for case in cases if case.file_extension == '.c'],
    'cpp': [case for case in cases if case.file_extension == '.cpp'],
    'java': [case for case in cases if case.file_extension == '.java'],
}



# For each language, split the cases into training, testing, and validation sets
cases_by_language_and_set = {
    language: {
        'training': [],
        'testing': [],
        'validation': [],
    }
    for language in cases_by_language.keys()
}

for language, cases in cases_by_language.items():
    split_cases = assign_id(cases, split=[70, 20, 10])
    cases_by_language_and_set[language]['training'] = split_cases[0]
    cases_by_language_and_set[language]['testing'] = split_cases[1]
    cases_by_language_and_set[language]['validation'] = split_cases[2]

# For each set, for each language, for each case, clean the code and insert it into the Juliet2 database
for set_name, model_id in zip(['training', 'testing', 'validation'], [0, 1, 2]):
    for language in cases_by_language_and_set.keys():
        print(f"Processing {set_name} cases for language {language}")
        for i, case in enumerate(cases_by_language_and_set[language][set_name]):
            print(f"Processing {set_name} case {i} for language {language}")
            # Clean the code
            code = rcmpy.keep_newlines(case.file_content)
            # Insert into the new database
            Juliet2.add(Cases(
                model_id=model_id,  # Assign model_id based on the set
                file_name=case.file_name,
                vulnerability_location=case.vulnerability_location,
                cwe=case.cwe,
                file_content=code
            ))

# Commit the changes to the new database
try:
    Juliet2.commit()
except Exception as e:
    print("Error occurred:", e)
    Juliet2.rollback()

Juliet2.close()

