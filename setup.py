# setup.py
import subprocess
import sys
import os
import venv
import nltk

def check_venv():
    """Checks if a virtual environment exists and is active."""
    return os.path.exists(".venv") and sys.prefix != sys.base_prefix

def create_venv():
    """Creates a virtual environment named '.venv'."""
    print("Creating virtual environment...")
    venv.create(".venv", with_pip=True)
    print("Virtual environment '.venv' created.")

def activate_venv():
    """Activates the virtual environment."""
    # Different activation commands for different shells
    if sys.platform == "win32":
        activate_script = ".venv\\Scripts\\activate.bat"
    else:  # Assume POSIX (Linux, macOS)
        activate_script = ".venv/bin/activate"

    print(f"Activating virtual environment (source {activate_script})...")
    # We can't *really* activate the venv in the *same* process.
    # We can only give instructions to the user.
    print("\n*** IMPORTANT ***")
    if sys.platform == "win32":
      print("Please run the following command in your command prompt to activate the venv:")
      print(f"  {activate_script}")
    else:
      print("Please run the following command in your terminal to activate the venv:")
      print(f"  source {activate_script}")
    print("Then, you can run the main script (python job_analyser.py).\n")
    return activate_script # Return for use by the user


def install_packages():
    """Installs packages from requirements.txt within the active venv."""
    print("Installing packages...")
    try:
        # Use subprocess.check_call for error handling
        subprocess.check_call([".venv/Scripts/python" if sys.platform == "win32" else ".venv/bin/python",
                               "-m", "pip", "install", "-r", "requirements.txt"])
        print("Packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)

def download_nltk_data():
    """Downloads NLTK data, checking if it's already present."""
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
    if not check_venv():
        create_venv()
        activate_venv()
    else:
        activate_script = activate_venv() # Print activation instructions
    install_packages() # This now runs with the venv's Python.
    download_nltk_data()
    print("Setup complete!")