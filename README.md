# Juliet

This is the repository for the NASA West Virginia Space Grant Consortium 2023-2024 funded research grant entitled: _Semantic Positional Encoding for Better Vulnerability Detection_. The final report submitted to NASA is available here for further details about the motivation for this project.

Juliet is a sequence to sequence (Seq2Seq) encoder decoder classification model inspired by an established deep learning architecture, Long-Short-Term-Memory(LSTM) based Recurrent Neural Networks (RNN). Juliet was created out of a desire for proof of concept that natural language modeling techniques can also be used to learn sequential positioning features from source code. In particular we hope that this will be a proof of concept for creating more robust static analysis tools for vulnerability detection. This first version of Juliet with a self-attention layer has achieved early validation results of a AUROC score of 94% in an experiment for binary line classifications.

| ![attention_AUC-ROC](https://github.com/user-attachments/assets/3c541bc0-3448-4ddd-aa91-2f84a3129d93) | ![attention_loss_plot](https://github.com/user-attachments/assets/161c1b18-58dc-4f38-93fb-c4bced7761a0) |
| --- | --- |
| ![image](https://github.com/user-attachments/assets/ba9fea1e-f27a-4d4e-88b7-66dad33ea9e8) | |

I complied the Juliet corpus used in training these model from the Juliet test suites accessed from the NIST Software Assurance Reference Dataset [https://samate.nist.gov/SARD/](url). Shown above are the 10 largest subgroups of CWE's in the corpus, and the entire corpus contains over 65,000 program files and 12 million lines of code.  In 2024 I intend to publicly release this dataset to be used for language modeling researchers looking to fine tune models for vulnerability identification.

A special thanks to the aix-coder-7b team for allowing their model weights and tokenizer to be used for research endeavors like this. [https://github.com/aixcoder-plugin/aiXcoder-7B](url)
