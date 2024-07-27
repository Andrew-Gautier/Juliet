from Juliet2_Schema import Cases, engine
from sqlalchemy import and_, func
from sqlalchemy.orm import relationship, sessionmaker
import rcmpy
import tqdm
Session = sessionmaker(bind=engine)
session = Session()

# This function will need to be more developed for getting everything into the training, testing, and validation sets. 
# Function to get 10 random test cases for a given file extension
def get_corpus(session):
    with open("Juliet2_Corpus.txt", "w") as write_file:
        Files = session.query(Cases.file_content).all()
        print(len(Files))
        for file_content in Files:
            clean_lines = rcmpy.keep_nothing(file_content[0]).split('\n')
            for line in clean_lines:
                write_file.write(line + '\n')

# Call the function with the desired parameters
get_corpus(session)


