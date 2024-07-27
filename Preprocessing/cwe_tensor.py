import sentencepiece as spm 
import torch
import os
import re
import torch.nn as nn
from keras.utils import pad_sequences
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader
from Juliet2_Schema import Session,Cases, VLW, VLW2

sp = spm.SentencePieceProcessor()
sp.Load('tokenizer.model')

from sqlalchemy import create_engine, func
session = Session()
records = session.query(VLW2).all()

query = session.query(VLW2.cwe, func.count(VLW2.cwe).label('total'))\
               .group_by(VLW2.cwe)\
               .order_by(func.count(VLW2.cwe).desc())

save_folder = 'tensors\cwes'    
## Wrapper to repeat this process for each class.
## Repeat the same data split as the VLW2 labels got to ensure no data leaking. 

records = session.query(VLW2).all() 
data = [record.vlw_content for record in records]
labels  = [record.vulnerability_location  for record in records]

# Split the data into train and test sets
train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.2, random_state=42)


for cwe_class in query:
    records = session.query(VLW2).filter(VLW2.cwe == cwe_class.cwe).all() 
    data = [record.vlw_content for record in records]
    labels  = [record.vulnerability_location  for record in records]

    # Split the data into train and test sets
    train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.2, random_state=42)
    # Encode sentences 
    train_sequences = [[sp.EncodeAsIds(line) for line in text.split('\n')[:40]] for text in train_data]
    test_sequences = [[sp.EncodeAsIds(line) for line in text.split('\n')[:40]] for text in test_data]

    # Finding the longest indivudial tokenized sentences
    max_length_train = max(max(len(seq) for seq in text) for text in train_sequences)
    max_length_test = max(max(len(seq) for seq in text) for text in test_sequences)

    # Get the maximum length across both sets
    max_length = max(max_length_train, max_length_test)

    # Convert labels to one-hot vectors

    num_classes = 40  
    train_labels = torch.stack([torch.nn.functional.one_hot(torch.tensor(label), num_classes=num_classes) for label in train_labels])
    test_labels = torch.stack([torch.nn.functional.one_hot(torch.tensor(label), num_classes=num_classes) for label in test_labels])

    print('max_length:', max_length)
    print('Train Labels:', train_labels[0])
    print('Test Labels:', test_labels[0])

    # Pad each individual sequence to a length of 98
    train_sequences_padded = [pad_sequences(text, maxlen=98, padding='post') for text in train_sequences]
    test_sequences_padded = [pad_sequences(text, maxlen=98, padding='post') for text in test_sequences]

    print('Train sequences shape:', train_sequences_padded[0].shape)
    print('Test sequences shape:', test_sequences_padded[0].shape)
    
    # Create a list of indices where the sequence length is not 40
    drop_indices = [i for i, seq in enumerate(train_sequences_padded) if len(seq) != 40]

    # Drop these indices from train_sequences_padded and train_labels
    train_sequences_padded = [seq for i, seq in enumerate(train_sequences_padded) if i not in drop_indices]
    train_labels = [label for i, label in enumerate(train_labels) if i not in drop_indices]

    # Print the number of remaining sequences and labels
    print(f"Number of remaining train sequences: {len(train_sequences_padded)}")
    print(f"Number of remaining train labels: {len(train_labels)}")
    
    drop_indices_test = [i for i, seq in enumerate(test_sequences_padded) if len(seq) != 40]

    # Drop these indices from test_sequences_padded and test_labels
    test_sequences_padded = [seq for i, seq in enumerate(test_sequences_padded) if i not in drop_indices_test]
    test_labels = [label for i, label in enumerate(test_labels) if i not in drop_indices_test]

    # Print the number of remaining sequences and labels
    print(f"Number of remaining test sequences: {len(test_sequences_padded)}")
    print(f"Number of remaining test labels: {len(test_labels)}")
    
    train_sequences_tensor = torch.tensor(train_sequences_padded)
    # Assuming train_labels needs to be stacked for a specific reason
    train_labels = torch.stack(train_labels)  # Keep this if it's necessary for your model
    train_dataset = TensorDataset(train_sequences_tensor, train_labels)

    # Create a DataLoader with a specific batch size and drop_last option
    batch_size = 40
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)

    # Print the shape of the first batch
    first_batch = next(iter(train_loader))
    print('First train batch shape:', first_batch[0].shape)

    test_sequences_tensor = torch.tensor(test_sequences_padded)
    test_labels = torch.stack(test_labels)
    test_dataset = TensorDataset(test_sequences_tensor, test_labels)
    batch_size = 40

    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True, drop_last=True)

    first_batch = next(iter(test_loader))
    print('First test batch shape:', first_batch[0].shape)
    
    print('train_sequences_tensor shape:', train_sequences_tensor.shape)
    print('train_sequences_tensor dtype:', train_sequences_tensor.dtype)
    print('train_labels_tensor shape:', train_labels.shape)
    print('train_labels_tensor dtype:', train_labels.dtype)
    
    # Replace colon and other potentially problematic characters in the directory name
    smatch = re.search(r"CWE-\d+", cwe_class.cwe)
    match = re.search(r"CWE-\d+", cwe_class.cwe)
    if match:
        safe_cwe_class_name = match.group()
    else:
        safe_cwe_class_name = "Unknown_CWE"
    
    # Use the modified, safe directory name
    cwe_save_folder = os.path.join(save_folder, f"cwe_{safe_cwe_class_name}")
    os.makedirs(cwe_save_folder, exist_ok=True)
    
    cwe_description = safe_cwe_class_name
    # Save training sequences and labels
    torch.save(train_sequences_tensor, os.path.join(cwe_save_folder, f'cwe_{cwe_description}_train_sequences_tensor.pt'))
    torch.save(train_labels, os.path.join(cwe_save_folder, f'cwe_{cwe_description}_train_labels.pt'))

    # Save testing sequences and labels
    torch.save(test_sequences_tensor, os.path.join(cwe_save_folder, f'cwe_{cwe_description}_test_sequences_tensor.pt'))
    torch.save(test_labels, os.path.join(cwe_save_folder, f'cwe_{cwe_description}_test_labels.pt'))