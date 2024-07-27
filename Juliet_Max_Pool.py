import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from torchmetrics.classification import BinaryAUROC
from torch.optim import Adam
import tqdm
import os
import numpy

BATCH_SIZE = 40
LEARNING_RATE = 0.001
EPOCHS = 20
LSTM_NODES = 256
NUM_SENTENCES = 40
SENTENCE_LENGTH = 98
VOCAB_SIZE = 49152
EMBEDDING_SIZE = 4096
NUM_EPOCHS = 20

train_sequences_tensor = torch.load("vlw2_train_sequences_tensor.pt")
train_labels = torch.load("vlw2_train_labels.pt") 
train_dataset = TensorDataset(train_sequences_tensor, train_labels)
train_loader = DataLoader(train_dataset, batch_size = BATCH_SIZE, shuffle = True, drop_last = True)

test_sequences_tensor = torch.load('vlw2_test_sequences_tensor.pt')
test_labels = torch.load('vlw2_test_labels.pt') 
test_dataset = TensorDataset(test_sequences_tensor, test_labels)
test_loader = DataLoader(test_dataset, batch_size = BATCH_SIZE, shuffle = True, drop_last = True)

cuda_available = torch.cuda.is_available()
print("CUDA Available:", cuda_available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(696)

# TODO: Model checkpoints, Model saving
try:
    pretrained_weights = torch.load('aix3-7b-base (1).pt')
    print("Weights loaded successfully.")
except Exception as e:
    print(f"Failed to load weights: {e}")

# Once you've identified the key for the embeddings, you can extract them like this:
word_vectors = pretrained_weights['tok_embeddings.weight']
print(word_vectors.shape)

def save_checkpoint(state, epoch, checkpoint_path="/seed694_checkpoints"):
    if not os.path.exists(checkpoint_path):
        os.makedirs(checkpoint_path)
    filename = os.path.join(checkpoint_path, f"checkpoint_epoch_{epoch}.pth")
    torch.save(state, filename)

# Define the LSTM model
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
).to(device)

print(model)

model.eval()

with torch.no_grad():
    # Get the first batch of data from the training loader
    batch_sequences, batch_labels = next(iter(train_loader))
        
    # Pass the batch of sequences through the model
    outputs = model(batch_sequences)
    
def train(model, iterator, optimizer, criterion, epoch, device, checkpoint_path="696_model_checkpoints"):
    epoch_loss = 0
    model.train()
    
    for batch_sequences, batch_labels in tqdm.tqdm(iterator, desc='Training'):
        # Move data to the device
        batch_sequences, batch_labels = batch_sequences.to(device), batch_labels.to(device)
        
        optimizer.zero_grad()
        predictions = model(batch_sequences)
        
        predictions = predictions.view(-1, 40).float()  # Flatten if necessary
        batch_labels = batch_labels.view(-1, 40).float()  # Ensure labels are correctly shaped
        
        loss = criterion(predictions, batch_labels)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
        
    # Save checkpoint after the epoch
    save_checkpoint({
        'epoch': epoch,
        'state_dict': model.state_dict(),
        'optimizer': optimizer.state_dict(),
        'loss': epoch_loss / len(iterator),
    }, epoch, checkpoint_path=checkpoint_path)    
    
    return epoch_loss / len(iterator)

def evaluate(model, iterator, criterion, device):
    epoch_loss = 0
    model.eval()
    auroc = BinaryAUROC().to(device)  # Initialize AUROC metric

    with torch.no_grad():
        for batch_sequences, batch_labels in tqdm.tqdm(iterator, desc='Evaluation'):
            # Move data to the device
            batch_sequences, batch_labels = batch_sequences.to(device), batch_labels.to(device)
            
            predictions = model(batch_sequences)
            predictions = predictions.view(-1, 40).float()  # Flatten if necessary
            batch_labels = batch_labels.view(-1, 40).float()  # Ensure labels are correctly shaped
            
            probabilities = torch.sigmoid(predictions)  # Convert logits to probabilities
            
            # Update AUROC computation
            auroc.update(probabilities, batch_labels.int())
            
            loss = criterion(predictions, batch_labels)
            epoch_loss += loss.item()
    
    auroc_score = auroc.compute()  # Compute the final AUROC score
    auroc.reset()  # Reset AUROC metric for future use
    
    return epoch_loss / len(iterator), auroc_score.item()

# MAIN TRAINING LOOP


optimizer = torch.optim.Adam(model.parameters())
criterion = nn.BCELoss()

# Define the number of epochs
N_EPOCHS = 40
# Implement a basic early stopping counter
best_valid_loss = float('inf')
epochs_since_improvement = 0
# Store the loss values for plotting
train_losses = []
valid_losses = []
valid_aurocs = []

for epoch in range(N_EPOCHS):
    train_loss = train(model, train_loader, optimizer, criterion, epoch, device)
    valid_loss, valid_auroc = evaluate(model, test_loader, criterion, device)
    train_losses.append(train_loss)
    valid_losses.append(valid_loss)
    valid_aurocs.append(valid_auroc)
    print(f'Epoch: {epoch+1}, Train Loss: {train_loss:.3f}, Val. Loss: {valid_loss:.3f}, Val. AUROC: {valid_auroc:.3f}')
    
    if valid_loss < best_valid_loss:
        best_valid_loss = valid_loss
        epochs_since_improvement = 0  # Reset counter
    else:
        epochs_since_improvement += 1  # Increment counter
    
    # Stop training if validation loss hasn't improved for 3 consecutive epochs
    if epochs_since_improvement == 3:
        print("Stopping early due to no improvement in validation loss for 3 consecutive epochs.")
        break

# Plot the training and validation loss
plt.figure(figsize=(10, 5))
plt.plot(train_losses, label='Train Loss')
plt.plot(valid_losses, label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.savefig('696_loss_plot.png')
plt.close()

# Plot the validation AUROC scores
plt.figure(figsize=(10, 5))
plt.plot(valid_aurocs, label='Validation AUROC')
plt.xlabel('Epochs')
plt.ylabel('AUROC')
plt.legend()
plt.ylim(0.5, 1.0)  # Set the y-axis to scale between 0.5 and 1
plt.xlim(0, 20)  # Set the x-axis to scale between 0 and 20
plt.savefig('696_auroc_plot.png')
plt.close()