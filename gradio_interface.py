import gradio as gr
import shutil
import json
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
from utils.models import ExtractedIssueList, DetectedIssue, IsValidIssue
from utils.pptx_utils import extract_text_from_pptx
from utils.prompts import build_system_prompt, build_user_prompt
from utils.screenshots import convert_pptx_to_images
from utils.image_utils import encode_image, get_image_data_url

IMG_PLACEHOLDER = "https://via.placeholder.com/150"

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

async def validate_issue_description(client: MistralClientWrapper, model:str, issue_description: str) -> bool:
    """
    Validate that the issue description is not useless using Mistral small model.

    Args:
        client (MistralClientWrapper): The Mistral client wrapper.
        issue_description (str): The issue description to validate.

    Returns:
        bool: True if the description is valid, False otherwise.
    """
    
    system_prompt = """
    Your task is to determine if an issue description for a presentation slide is useful or not.
    A useful description should be specific, actionable, and provide clear information about what needs to be fixed.
    Example of invalid description 
    Respond with only 'true' if the description is useful, or 'false' if it's not.
    """
    
    user_prompt = f"Is this  description useful? '{issue_description}'"
    
    messages = client.build_messages(system_prompt=system_prompt, user_prompt=user_prompt)
    
    try:
        result = await client.complete_with_retry(
            model=model,
            messages=messages,
            ResponseModel=IsValidIssue
        )
        return result.is_valid
    except Exception as e:
        print(f"Error validating issue description: {e}")
        return False  # Assume invalid if there's an error

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


async def process_presentation(pptx_path: str, config: Dict, user_context: str, slides_content: dict, screenshots: dict) -> List[DetectedIssue]:
    # Initialize the client
    client = MistralClientWrapper(api_key=os.getenv("MISTRAL_API_KEY"))
    model_text = "mistral-large-latest"
    model_screenshot = "pixtral-12b-2409"
    model_validate = "mistral-small-latest"

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
            for page_id, screenshot_path in screenshots.items():
                all_tasks.append(run_checker(
                    client, model_screenshot,
                    checker, user_context, 
                    None, # no slide content
                    screenshot_path,
                    int(page_id),
                    pptx_path
                ))
    
    # Run all checkers
    results = await tqdm.gather(*all_tasks, desc="Processing all checkers")
    
    # Combine all results
    all_issues = [issue for result in results for issue in result]

    # Prepare tasks for issue validation
    validation_tasks = [validate_issue_description(client, model_validate, issue.extracted_issue.issue_description) for issue in all_issues]

    # Run all validation tasks
    valid_issues = await tqdm.gather(*validation_tasks, desc="Validating issues")
    
    # Filter out invalid issues
    valid_issues = [issue for issue, is_valid in zip(all_issues, valid_issues) if is_valid]
    return all_issues

def create_slide_html(issues_data, merged_dict):
    slides = {}

    # Group issues by slide number (page_id)
    for issue in issues_data:
        slide_number = issue.page_id
        if slide_number not in slides:
            slides[slide_number] = []
        slides[slide_number].append(issue)

    html_content = ""

    # Create the HTML structure for each slide
    for slide_number, issues in slides.items():
        # Access the image path directly from merged_dict
        img_path = merged_dict.get(str(slide_number), {}).get("img_path", IMG_PLACEHOLDER)

        html_content += f"<div style='border:1px solid #ddd; padding: 10px; margin: 10px 0;'><h3>Slide {slide_number}</h3>"
        html_content += f"<img src='{img_path}' alt='Slide {slide_number} Preview' style='width:400px;'/>"
        for i, issue in enumerate(issues, 1):
            issue_description = issue.extracted_issue.issue_description
            severity = issue.extracted_issue.severity.capitalize()
            html_content += f"<p><strong>Issue {i}:</strong> {issue_description} (Severity: {severity})</p>"
        html_content += "</div>"

    return html_content



def process_ppt(context_info, ppt_upload):
    # Generate mock issues data
    config = load_config('config/config.yaml')
    user_context = context_info
    output_folder = 'pics' 

    # Delete the 'pics' folder if it exists
    if os.path.exists('pics'):
        shutil.rmtree('pics')
        print("Deleted 'pics' folder")

    print("FILE: ",ppt_upload.name)

    # Extract text from the uploaded PowerPoint file
    slides_content = extract_text_from_pptx(ppt_upload)
    print("SLIDES ", slides_content)
    # Process screenshots
    img_paths = json.loads(convert_pptx_to_images(ppt_upload, output_folder))
    print("PATHS ", img_paths)

    merged_dict = {}
    for key in slides_content.keys():
        if key in img_paths:
            path=img_paths[str(key)]
            print("query", key, " ",path)
            encoded_image, image_format = encode_image(path)
            img_payload= get_image_data_url(encoded_image, image_format)
            merged_dict[key] = {
                "img_path": img_payload,
                "text": slides_content[str(key)]
            }
 
    issues_data = asyncio.run(process_presentation(ppt_upload.name, config, user_context, slides_content, img_paths))
    
    # Create the HTML content for slide view
    slide_html = create_slide_html(issues_data, merged_dict)
    
    # Generate summary output
    total_issues = len(issues_data)
    high_severity_issues = sum(1 for issue in issues_data if issue.extracted_issue.severity == "high")
    
    summary = f"Total issues detected: {total_issues}\n"
    summary += f"High severity issues: {high_severity_issues}"
    # Return both the summary and the HTML content
    return summary, slide_html

# Building the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("Slide Doctor")

    context_input = gr.Textbox(label="Context Information", placeholder="Enter context for the presentation")
    ppt_upload = gr.File(label="Upload PPT", file_count="single", file_types=[".ppt", ".pptx"])

    generate_button = gr.Button("Analyse")

    gr.Markdown("### Summary")
    summary_output = gr.Textbox(label="Summary", lines=4, interactive=False)

    gr.Markdown("### Page View")
    slide_sections_container = gr.HTML("")  # Use HTML component to dynamically render slide sections

    # Generate Page View on button click
    generate_button.click(
        process_ppt,
        inputs=[context_input, ppt_upload],
        outputs=[summary_output, slide_sections_container]
    )

demo.launch()