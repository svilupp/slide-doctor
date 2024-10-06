import numpy as np
from typing import List

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return (dot_product / (norm_a * norm_b))

def dedupe_by_similarity(embeddings, severities, similarity_threshold=0.95):
    """Calculate pairwise cosine distances for a list of embeddings."""
    num_embeddings = len(embeddings)
    
    keep_issues = [True] * num_embeddings
    
    for i in range(num_embeddings):
        if not keep_issues[i]:
            continue
        for j in range(i+1, num_embeddings):
            if not keep_issues[j]:
                continue
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim > similarity_threshold: 
                if severities[i] >= severities[j]:
                    keep_issues[j] = False
                else:
                    keep_issues[i] = False
    
    return keep_issues