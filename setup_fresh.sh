#!/bin/bash
# Fresh setup script for LangChain app

# Remove old virtual environment
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages one by one to avoid conflicts
pip install streamlit
pip install pypdf2
pip install python-dotenv
pip install openai
pip install faiss-cpu
pip install sentence-transformers
pip install tiktoken

# Install LangChain ecosystem
pip install langchain
pip install langchain-openai
pip install langchain-community
pip install langchain-text-splitters

echo "Setup complete! Activate with: source venv/bin/activate"