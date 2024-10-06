import os, sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
import asyncio
from utils.client import MistralClientWrapper
from utils.models import ExtractedIssue, IssueCategory, ExtractedIssueList
from pydantic import BaseModel

async def main():
    # Initialize the client with your API key
    client = MistralClientWrapper(api_key=os.getenv("MISTRAL_API_KEY"))
    
    # Define system and user prompts
    system_prompt = "You are an AI assistant specialized in analyzing documents for issues."
    user_prompt = "Please analyze this chart for any clarity or accuracy issues."
    
    # Build messages
    messages = client.build_messages(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_path="data/03-dickinson-basic002.png"
    )
    
    try:
        # Call the API with retry logic
        result = await client.complete_with_retry(
            model="pixtral-12b-2409",  # or whichever model you're using
            messages=messages,
            ResponseModel=ExtractedIssueList
        )
        
        # Print the result
        print(f"Number of issues detected: {len(result.issues)}")
        for i, issue in enumerate(result.issues, 1):
            print(f"\nIssue {i}:")
            print(f"Category: {issue.issue_category}")
            print(f"Description: {issue.issue_description}")
            print(f"Severity: {issue.severity}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
