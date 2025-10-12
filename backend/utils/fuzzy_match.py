"""
Fuzzy matching utilities for detecting similar company names
"""
import difflib
from typing import List, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings
    Returns the minimum number of edits (insertions, deletions, substitutions) needed
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """
    Calculate similarity ratio between two strings (0.0 to 1.0)
    1.0 means identical, 0.0 means completely different
    """
    # Normalize strings
    s1 = normalize_string(s1)
    s2 = normalize_string(s2)
    
    if not s1 or not s2:
        return 0.0
    
    # Use difflib's SequenceMatcher for better Persian text handling
    return difflib.SequenceMatcher(None, s1, s2).ratio()


def normalize_string(s: str) -> str:
    """
    Normalize string for comparison
    - Convert to lowercase
    - Remove extra spaces
    - Remove common business suffixes
    """
    if not s:
        return ""
    
    s = s.strip().lower()
    
    # Remove common Persian business suffixes
    suffixes = [
        'شرکت', 'مجموعه', 'گروه', 'موسسه', 'سازمان', 
        'تعاونی', 'بنگاه', 'واحد', 'مرکز',
        'company', 'group', 'organization', 'co', 'inc', 'ltd'
    ]
    
    for suffix in suffixes:
        if s.startswith(suffix + ' '):
            s = s[len(suffix):].strip()
        if s.endswith(' ' + suffix):
            s = s[:-len(suffix)].strip()
    
    # Remove extra whitespace
    s = ' '.join(s.split())
    
    return s


def find_similar_names(name: str, existing_names: List[str], threshold: float = 0.8) -> List[Tuple[str, float]]:
    """
    Find similar names from a list of existing names
    
    Args:
        name: The name to check
        existing_names: List of existing names to compare against
        threshold: Similarity threshold (0.0 to 1.0), default 0.8
        
    Returns:
        List of tuples (similar_name, similarity_score) where score >= threshold
    """
    similar = []
    
    normalized_name = normalize_string(name)
    
    for existing_name in existing_names:
        ratio = similarity_ratio(name, existing_name)
        
        if ratio >= threshold:
            similar.append((existing_name, ratio))
    
    # Sort by similarity score (highest first)
    similar.sort(key=lambda x: x[1], reverse=True)
    
    return similar


def check_company_name_similarity(name: str, existing_names: List[str], threshold: float = 0.8) -> dict:
    """
    Check if a company name is similar to existing names
    
    Args:
        name: The company name to check
        existing_names: List of existing company names
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        Dictionary with:
        - has_similar: bool
        - similar_names: list of similar names
        - highest_similarity: float (0.0 to 1.0)
    """
    similar_names = find_similar_names(name, existing_names, threshold)
    
    return {
        'has_similar': len(similar_names) > 0,
        'similar_names': [name for name, score in similar_names],
        'similarity_scores': {name: score for name, score in similar_names},
        'highest_similarity': similar_names[0][1] if similar_names else 0.0
    }

