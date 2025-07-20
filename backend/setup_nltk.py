import nltk

def setup():
    """Downloads the necessary NLTK data models."""
    print("Starting NLTK data download...")
    # Added 'punkt_tab' to the list of required packages
    packages = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    for package in packages:
        try:
            print(f"-> Downloading '{package}'...")
            nltk.download(package)
        except Exception as e:
            print(f"Error downloading {package}: {e}")
    print("NLTK setup complete. ✅")

if __name__ == '__main__':
    setup()