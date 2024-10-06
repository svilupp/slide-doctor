import numpy as np
from typing import List
from .client import MistralClientWrapper
from .models import DetectedIssue

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


def deduplicate_issues(client: MistralClientWrapper, model: str, issues: List[DetectedIssue]) -> List[DetectedIssue]:
    # Extract issue descriptions
    descriptions = [issue.extracted_issue.issue_description for issue in issues]
    
    # Get embeddings using the client
    model = "mistral-embed"  # Specify the appropriate embedding model
    embeddings = client.get_embeddings(model, descriptions)
    
    # Extract severities
    severities = [issue.extracted_issue.severity for issue in issues]
    severities_points = {'low':1, 'medium': 2, 'high': 3}
    severities_int = [severities_points[sev] for sev in severities]
    
    # Calculate cosine similarities and drop the dupes
    keep_issues = dedupe_by_similarity(embeddings, severities_int, similarity_threshold = 0.9)
    
    # Create a new list with deduplicated issues
    deduplicated_issues = [issue for issue, keep in zip(issues, keep_issues) if keep]
    
    return deduplicated_issues