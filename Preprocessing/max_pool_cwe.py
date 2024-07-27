import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from torchmetrics.classification import BinaryAUROC
from torch.optim import Adam
import tqdm
import os
import numpy
# Script to  evaluate the best max pool model separately 

# Model Parameters
BATCH_SIZE = 40
LEARNING_RATE = 0.001
EPOCHS = 20
LSTM_NODES = 256
NUM_SENTENCES = 40
SENTENCE_LENGTH = 98
VOCAB_SIZE = 49152
EMBEDDING_SIZE = 4096
NUM_EPOCHS = 20 

# Intializing model weights + checkpoint
cuda_available = torch.cuda.is_available()
print("CUDA Available:", cuda_available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(696)

pretrained_weights = torch.load('aix3-7b-base (1).pt')    
word_vectors = pretrained_weights['tok_embeddings.weight']
print(word_vectors.shape)

# Load the checkpoint
checkpoint = torch.load('696_model_checkpoints/checkpoint_epoch_26.pth')
print("Checkpoint's State Dict Keys:", checkpoint['state_dict'].keys())

# Initialize Model Architecture
class LSTMClassifier(nn.Module):    
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim, n_layers, batch_first, bidirectional, dropout, pretrained_weights, batch_size, sentence_length):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim).to(device)
        self.rnn = nn.LSTM(embedding_dim, hidden_dim, num_layers=n_layers, bidirectional=bidirectional, dropout=dropout).to(device)
        self.fc = nn.Linear(hidden_dim * 2, output_dim).to(device)
        self.dropout = nn.Dropout(dropout).to(device)
        self.embedding.weight.data.copy_(pretrained_weights.to(device))

    def forward(self, text):
        text = text.to(device)
        batch_size, sentence_length, num_sentences = text.size()
        text = text.view(batch_size, sentence_length * num_sentences)
        
        embedded = self.dropout(self.embedding(text))
        #print(f"Shape after embedding: {embedded.shape}")
        lstm_output, (hidden, _) = self.rnn(embedded)
        # print(f"Shape after LSTM: {lstm_output.shape}")
        pooled = torch.mean(lstm_output, dim=1)
        # Pass through the fully connected layer
        output = self.fc(self.dropout(pooled))
       
        output = torch.sigmoid(output)
        # print(f"Shape of final output: {output.shape}")
        
        return output
# Instiantiate the model.
model = LSTMClassifier(
    vocab_size=VOCAB_SIZE,
    embedding_dim=EMBEDDING_SIZE,  
    hidden_dim=LSTM_NODES,
    output_dim=40,  
    n_layers=2,
    batch_first=True,
    bidirectional=True,
    dropout=0.5,
    pretrained_weights=word_vectors,
    batch_size=BATCH_SIZE,
    sentence_length=SENTENCE_LENGTH
)
print(model)

model.load_state_dict(checkpoint['state_dict'])

## Main Evaluation Loop

directory = 'tensors/'

for folder in directory:


aurocs = []
# Iterate through each CWE folder
for folder_name in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.isdir(folder_path):
        # Construct paths to the required tensors
        test_labels_path = os.path.join(folder_path, f'{folder_name}_test_labels.pt')
        test_sequences_path = os.path.join(folder_path, f'{folder_name}_test_sequences_tensor.pt')
        train_labels_path = os.path.join(folder_path, f'{folder_name}_train_labels.pt')
        train_sequences_path = os.path.join(folder_path, f'{folder_name}_train_sequences_tensor.pt')
        # Load the tensors
        test_labels = torch.load(test_labels_path)
        test_sequences = torch.load(test_sequences_path)
        train_labels = torch.load(train_labels_path)
        train_sequences = torch.load(train_sequences_path)
        #Make Dataloaders
        train_loader = DataLoader(train_dataset, batch_size = BATCH_SIZE, shuffle = True, drop_last = True)
        test_loader = DataLoader(test_dataset, batch_size = BATCH_SIZE, shuffle = True, drop_last = True)
        
        epoch_loss, auroc_score = evaluate(model, train_loader, criterion, device)
        print(f"{folder_name} - Loss: {epoch_loss:.4f}, AUROC: {auroc_score:.4f}")
    