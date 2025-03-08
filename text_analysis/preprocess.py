import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import ngrams

def preprocess_text(text, config):
    # 1. Remove HTML tags (if any)
    text = re.sub(r'<[^>]+>', '', text)

    # 2. Lowercase
    text = text.lower()

    # 3. Tokenize
    tokens = word_tokenize(text)

    # 4. Remove stop words and non-alphanumeric tokens
    stop_words = set(stopwords.words('english'))
    # Add custom stop words from config
    custom_stop_words = [word.strip() for word in config['TEXT_ANALYSIS']['custom_stop_words'].split(',')]
    stop_words.update(custom_stop_words)

    filtered_tokens = [token for token in tokens if token not in stop_words and token.isalnum()]

    # 5. Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    # 6. N-gram generation (bigrams and trigrams)
    bigrams = list(ngrams(lemmatized_tokens, 2))
    trigrams = list(ngrams(lemmatized_tokens, 3))
    # Combine tokens and n-grams
    return lemmatized_tokens + [" ".join(gram) for gram in bigrams] + [" ".join(gram) for gram in trigrams]