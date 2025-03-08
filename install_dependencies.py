# install_dependencies.py
import subprocess
import sys
import nltk
import os

def install_packages():
    """Installs Python packages from requirements.txt."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Successfully installed Python packages.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}", file=sys.stderr)
        sys.exit(1)  # Exit with an error code


def download_nltk_data():
    """Downloads necessary NLTK data if it's not already present."""
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK wordnet data...")
        nltk.download('wordnet')

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK punkt tokenizer data...")
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK stopwords data...")
        nltk.download('stopwords')

if __name__ == "__main__":
    install_packages()
    download_nltk_data()