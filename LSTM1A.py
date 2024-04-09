import numpy as np
import torch
import sentencepiece as spm
import tensorflow as tf
from keras import models, layers
from Juliet2_Schema import VLW, engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
import matplotlib.pyplot as plt



# Load the trained SentencePiece model
sp = spm.SentencePieceProcessor()
sp.Load("m.model")

# Define the vocabulary size and embedding dimension
vocab_size = len(sp)
embedding_dim = 100  # Adjust this dimension based on your requirements

# Define the LSTM model
Juliet = models.Sequential([
    layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim),  # Input layer for token embeddings
    layers.Bidirectional(layers.LSTM(units=128, return_sequences=True)),  # Bidirectional LSTM layer
    layers.TimeDistributed(layers.Dense(units=1, activation='sigmoid'))  # Time-distributed Dense layer for token classification
])

# Compile the model
Juliet.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Generate training data (example, replace with your data)
# TODO: Query the datatbase for training data, label it, and then tokenize it
session = sessionmaker(bind=engine)
session = session()
index = 21
token = 'VULNERABILITY'
training_records = session.query(VLW).filter(VLW.model_id == 0).filter(VLW.vlw_content).all()
testing_records = session.query(VLW).filter(VLW.model_id == 1).filter(VLW.vlw_content).all()
num_train=5000
num_test=1000
train_texts = []
test_texts = []
print(len(training_records))
print(len(testing_records))
# Get Training Data
for record in training_records:
    if (record.cwe_int == 1):
        vlw_content_list = record.split('\n')    
        if len(vlw_content_list) > 21:  # Ensure there are at least 20 lines
            vlw_content_list.insert(21, token)
        # Join the list back into a string with newlines between elements
        vlw_content_str = '\n'.join(vlw_content_list)
        # Append the string to train_texts
        train_texts.append(vlw_content_str)
# Get Testing Data
for record in testing_records:
    if (record.cwe_int == 1):
        vlw_content_list = record.split('\n')    
        test_texts.append(vlw_content_list)
        
torch.manual_seed(620)
# Tokenize training texts and pad sequences
train_sequences = [sp.EncodeAsIds(text) for text in train_texts]
train_sequences_padded = tf.keras.preprocessing.sequence.pad_sequences(train_sequences, padding='post')
train_labels = [[1 if token == "VULNERABILITY" else 0 for token in sp.EncodeAsPieces(text)] for text in train_texts]  # Example: Label 1 for occurrence of "TOKEN"

# Train the model
epochs = 10
batch_size = 32
# Lists to store training loss and epoch number for plotting
losses = []
epochs_list = []

# Iterate over the epochs and wrap the loop with tqdm for progress visualization
for epoch in tqdm(range(epochs), desc="Training Epochs"):
    # Inside the loop, call model.fit() for each epoch
    history = Juliet.fit(train_sequences_padded, np.array(train_labels), epochs=1, batch_size=batch_size, verbose=0)

    # Check if history.history['loss'] is not empty before appending
    if history.history['loss']:
        losses.append(history.history['loss'][0])
        epochs_list.append(epoch + 1)
    
    # Print the current loss
        print(f"Epoch {epoch+1}/{epochs}, Loss: {history.history['loss'][0]}")
    else:
        print(f"Epoch {epoch+1}/{epochs}, No loss recorded.")
    
    # Append the training loss and epoch number to lists
    losses.append(history.history['loss'][0])
    epochs_list.append(epoch + 1)

    # Print the current loss
    print(f"Epoch {epoch+1}/{epochs}, Loss: {history.history['loss'][0]}")

# Plot the loss graph over epochs
plt.plot(epochs_list, losses)
plt.title('Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.show()