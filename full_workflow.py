import os
import sys
import asyncio
from tqdm.asyncio import tqdm
import json
from typing import List, Dict

# Add the project root directory to the Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root="."
sys.path.insert(0, project_root)

from utils.client import MistralClientWrapper
from utils.utils import load_config, extract_slide_number
from utils.models import ExtractedIssueList, DetectedIssue
from utils.pptx_utils import extract_text_from_pptx
from utils.prompts import build_system_prompt, build_user_prompt

async def run_checker(client: MistralClientWrapper, model: str, checker: dict, user_context: str, slide_content:str|None, image_path: str|None, slide_number: int, pptx_file: str) -> List[DetectedIssue]:
    system_prompt=build_system_prompt(checker['task'], user_context, checker['criteria'])
    user_prompt=build_user_prompt(slide_content)

    messages = client.build_messages(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image_path=image_path
    )
    
    result = await client.complete_with_retry(
        model=model,
        messages=messages,
        ResponseModel=ExtractedIssueList
    )
    
    issues=[
        DetectedIssue(
            extracted_issue=issue,
            category=checker['name'],
            page_id=slide_number,
            file=pptx_file
        ) for issue in result.issues
    ]
    return issues

async def process_presentation(pptx_path: str, config: Dict, user_context: str) -> List[DetectedIssue]:
    # Initialize the client
    client = MistralClientWrapper(api_key=os.getenv("MISTRAL_API_KEY"))
    model_text = "mistral-large-latest"
    model_screenshot = "pixtral-12b-2409"
    
    # Extract text from the presentation
    slides_content = extract_text_from_pptx(pptx_path)

    # Add screenshot extraction
    screenshots = ['data/03-dickinson-basic002.png']
    
    all_tasks = []
    
    # Prepare tasks for text-based checkers
    for checker in config['checkers']:
        if checker['type'] == 'text':
            # For each slide
            for slide_number, slide_content in slides_content.items():
                all_tasks.append(run_checker(
                    client, model_text,
                    checker, user_context, slide_content,
                    None, # no image_path
                    int(slide_number),
                    pptx_path
                ))
    
    # Prepare tasks for screenshot-based checkers
    for checker in config['checkers']:
        if checker['type'] == 'screenshot':
            for screenshot_path in screenshots:
                all_tasks.append(run_checker(
                    client, model_screenshot,
                    checker, user_context, 
                    None, # no slide content
                    screenshot_path,
                    extract_slide_number(screenshot_path),
                    pptx_path
                ))
    
    # Run all checkers
    results = await tqdm.gather(*all_tasks, desc="Processing all checkers")
    
    # Combine all results
    all_issues = [issue for result in results for issue in result]
    
    return all_issues

async def main():
    config = load_config('config/config.yaml')
    pptx_path = 'data/03-dickinson-basic.pptx'
    user_context="Investor presentation for our business, Dickinson. Very professional."

    # Process the presentation and get all issues
    issues = await process_presentation(pptx_path, config, user_context)
    
    print(f"Total issues detected: {len(issues)}")
    for issue in issues:
        print(f"\nIssue on slide {issue.page_id}:")
        print(f"Category: {issue.category}")
        print(f"Description: {issue.extracted_issue.issue_description}")
        print(f"Severity: {issue.extracted_issue.severity}")
        print(f"Location: {issue.extracted_issue.element_location}")
        print(f"File: {issue.file}")

if __name__ == "__main__":
    asyncio.run(main())
