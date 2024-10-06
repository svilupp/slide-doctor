import asyncio
import os
from utils.client import MistralClientWrapper
import numpy as np
from typing import List
from utils.models import DetectedIssue, ExtractedIssue, IssueLocation
from utils.deduplication import dedupe_by_similarity

# def cosine_similarity(a, b):
#     """Calculate cosine similarity between two vectors."""
#     dot_product = np.dot(a, b)
#     norm_a = np.linalg.norm(a)
#     norm_b = np.linalg.norm(b)
#     return (dot_product / (norm_a * norm_b))

# def dedupe_by_similarity(embeddings, severities, similarity_threshold=0.95):
#     """Calculate pairwise cosine distances for a list of embeddings."""
#     num_embeddings = len(embeddings)
    
#     keep_issues = [True] * num_embeddings
    
#     for i in range(num_embeddings):
#         if not keep_issues[i]:
#             continue
#         for j in range(i+1, num_embeddings):
#             if not keep_issues[j]:
#                 continue
#             sim = cosine_similarity(embeddings[i], embeddings[j])
#             print(f"Actions: sim={sim}, i={i}, j={j}, embeddings[i]={embeddings[i]}, embeddings[j]={embeddings[j]}, severities[i]={severities[i]}, severities[j]={severities[j]}, keep_issues={keep_issues}")
#             if sim > similarity_threshold: 
#                 if severities[i] >= severities[j]:
#                     keep_issues[j] = False
#                     print(f"Remove: {j}")
#                 else:
#                     keep_issues[i] = False
#                     print(f"Remove: {i}")
    
#     return keep_issues

# Create toy data to test calculate_cosine_distances
def create_toy_data():
    # Create sample embeddings
    embeddings = [
        np.array([0.1, 0.2, 0.3]),  # Issue 1
        np.array([0.11, 0.21, 0.31]),  # Issue 2 (similar to Issue 1)
        np.array([0.0, -1.0, 0.7]),  # Issue 3 (different)
        np.array([0.51, 0.61, 0.71]),  # Issue 4 (similar to Issue 3)
        np.array([0.9, 0.8, -0.7])  # Issue 5 (different)
    ]
    
    # Create corresponding severities
    severities = ['medium', 'low', 'high', 'medium', 'low']
    severities_points = {'low':1, 'medium': 2, 'high': 3}
    severities_int = [severities_points[sev] for sev in severities]
    
    return embeddings, severities_int

# Test the calculate_cosine_distances function
# embeddings, severities = create_toy_data()
# keep_issues = dedupe_by_similarity(embeddings, severities)

def deduplicate_issues(issues: List[DetectedIssue], client: MistralClientWrapper) -> List[DetectedIssue]:
    # Extract issue descriptions
    descriptions = [issue.extracted_issue.issue_description for issue in issues]
    
    # Get embeddings using the client
    model = "mistral-embed"  # Specify the appropriate embedding model
    embeddings = client.get_embeddings(model, descriptions)
    
    # Extract severities
    severities = [issue.extracted_issue.severity for issue in issues]
    
    # Calculate cosine distances and get keep_issues mask
    keep_issues = dedupe_by_similarity(embeddings, severities)
    
    # Create a new list with deduplicated issues
    deduplicated_issues = [issue for issue, keep in zip(issues, keep_issues) if keep]
    
    return deduplicated_issues

# Create toy examples with DetectedIssues including a few duplicates
def create_toy_detected_issues():
    issues = [
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="Memory leak in function X",
                severity="medium",
                element_location=IssueLocation.BODY_TEXT,
                element_identification_verbatim=None,
                element_identification_contains_text=None,
            ),
            category="Memory",
            page_id=1,
            file="abc.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="Buffer overflow in function Y",
                severity="high",
                element_location=IssueLocation.BODY_TEXT,
                element_identification_verbatim=None,
                element_identification_contains_text=None,
            ),
            category="Security",
            page_id=2,
            file="abc.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="Memory leak in function X",  # Duplicate of first issue
                severity="medium",
                element_location=IssueLocation.BODY_TEXT,
                element_identification_verbatim=None,
                element_identification_contains_text=None,
            ),
            category="Memory",
            page_id=3,
            file="abc.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="Uninitialized variable in function Z",
                severity="low",
                element_location=IssueLocation.BODY_TEXT,
                element_identification_verbatim=None,
                element_identification_contains_text=None,
            ),
            category="Initialization",
            page_id=4,
            file="abc.pptx"
        ),
        DetectedIssue(
            extracted_issue=ExtractedIssue(
                issue_description="Buffer overflow in function Y",  # Duplicate of second issue
                severity="high",
                element_location=IssueLocation.BODY_TEXT,
                element_identification_verbatim=None,
                element_identification_contains_text=None,
            ),
            category="Security",
            page_id=5,
            file="abc.pptx"
        )
    ]
    return issues


if __name__ == "__main__":
    # Example usage:
    toy_issues = create_toy_detected_issues()
    client = MistralClientWrapper(api_key=os.getenv("MISTRAL_API_KEY"))
    # client.get_embeddings("mistral-embed",["say hi", "say hi"])
    deduplicated_toy_issues = deduplicate_issues(toy_issues, client)
    print(f"Original issues: {len(toy_issues)}")
    print(f"Deduplicated issues: {len(deduplicated_toy_issues)}")
