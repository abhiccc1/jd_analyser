from collections import Counter

def rank_terms(terms, min_frequency):
    """
    Counts the frequency of terms and ranks them.
    """
    term_counts = Counter(terms)
    # Filter by minimum frequency
    filtered_counts = {term: count for term, count in term_counts.items() if count >= min_frequency}

    # Sort by count in descending order and return as a list of tuples
    ranked_terms = sorted(filtered_counts.items(), key=lambda item: item[1], reverse=True)
    return ranked_terms