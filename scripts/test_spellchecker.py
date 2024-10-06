import os, sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
import asyncio
import weave
from utils.client import MistralClientWrapper
from utils.models import ExtractedIssueList
weave.init("slide-doctor-spellchecker")

async def main():
    # Initialize the client with your API key
    client = MistralClientWrapper(api_key=os.getenv("MISTRAL_API_KEY"))
    # model = "pixtral-12b-2409"
    # image_path="data/03-dickinson-basic002.png"
    ## TODO: change to powerpoint text
    model="mistral-large-latest"
    image_path=None
    
    # Define system and user prompts
    issue_category = "spellchecker" ## determine by checker type
    user_context="Investor presentation for our business, Dickinson. Very professional."
    ## Task details -- spellchecker
    checker_task = "identify spelling and grammar errors, inconsistency, bad punctuation and bad spacing"
    checker_list="""
    - Spelling: Wrong spelling of common words, ignore any specialized words that can be brands and names
    - Language Consistency: Mix of British and American English in the same text
    - Capitalization: All titles should be title-cased (eg, "Key Message"). For other text, ensure the capitalization is consistent.
    - Punctuation: Wrong use of punctuation marks (eg, "..")
    - Spacing: Double spacing between words, hidden whitespace characters, too many new lines

    Out of scope: Ignore any chart-specific issues, focus purely on the text problems.
    """
    
    system_prompt = f"""You are assisting the user with improving their presentation for the given use case and audience.
    
    Your task is to {checker_task} in the provided materials.
    
    Context of the presentation: {user_context}

    ### Criteria{checker_list}

    ### Instructions
    - You must follow the provided criteria, any other issues should be ignored.
    - Extract at most five most important issues that you can detect. It's okay to extract fewer, you must prioritize the most severe problems.
    - If there are no important issues, just return an empty list. 
    - Describe clearly the issue based on the provided criteria.
    - Provide severity (low, medium, high) of the issue using the context of the presentation.
    - Return only UNIQUE issues. Issues of the same type and same description (eg, formatting of units), need to be raised only once. 
      Do not create an issue for each value with the same problem. Deduplicate issues with the same description.

    Remember to only extract the issues described in the above criteria.    
    Be very selective and return only the MOST important issues that require immediate attention.
    If no issues are critical, you return an empty list.
    """
    user_prompt = "Please help me improve this presentation slide."
    
    # Build messages
    messages = client.build_messages(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_path=image_path
    )
    
    try:
        # Call the API with retry logic
        result = await client.complete_with_retry(
            model=model,
            messages=messages,
            ResponseModel=ExtractedIssueList
        )
        
        # Print the result
        print(f"Number of issues detected: {len(result.issues)}")
        for i, issue in enumerate(result.issues, 1):
            print(f"\nIssue {i}:")
            print(f"Category: {issue_category}")
            print(f"Location: {issue.element_location}")
            print(f"Description: {issue.issue_description}")
            print(f"Element Identification (Contains Text): {issue.element_identification_contains_text}")
            print(f"Element Identification (Verbatim): {issue.element_identification_verbatim}")
            print(f"Severity: {issue.severity}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

asyncio.run(main())

# if __name__ == "__main__":
#     asyncio.run(main())
