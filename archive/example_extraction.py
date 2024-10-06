import os
from typing import List
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image
import base64
import io
from enum import Enum

# Initialize the Mistral client with instructor
api_key = os.getenv("MISTRAL_API_KEY")
model = "pixtral-12b-2409"  # Using Pixtral model for image analysis

# Define the output schema
class ObjectType(Enum):
    TITLE = "title"
    TEXT = "text"
    CHART = "chart"
    FOOTER = "footer"
    TABLE = "table"

class Issue(BaseModel):
    object_type: ObjectType = Field(description="The type of object, from the enum: title, text, chart, footer, table")
    issue_category: str = Field(description="The category of the issue")
    issue_label: str = Field(description="The label of the issue")

class ExtractionResult(BaseModel):
    issues: List[Issue] = Field(description="List of extracted issues")


def encode_image(image_path: str) -> tuple[str, str]:
    if image_path.lower().endswith('.png'):
        image_format = "PNG"
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        image_format = "JPEG"
    else:
        raise ValueError("Unsupported image format. Only PNG and JPEG are allowed.")
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format=image_format)
        return base64.b64encode(buffer.getvalue()).decode('utf-8'), image_format

def extract_issues(image_path: str) -> ExtractionResult:
    base64_image, image_format = encode_image(image_path)

    system_prompt = """
    You are an AI specialized in identifying issues in PowerPoint presentation screenshots.
    Your task is to carefully examine the provided image and identify any problems or areas for improvement related to the slide's content, design, and overall effectiveness.
    Focus on detecting issues such as:
    1. Clarity and readability of text
    2. Effectiveness of visual elements (charts, graphs, images)
    3. Layout and organization of information
    4. Consistency in design and formatting
    5. Appropriateness of content for the intended audience
    Provide a comprehensive analysis of the issues present in the screenshot.
    """

    user_prompt = """
    Analyze this slide image and identify issues. For each issue, provide:
    1. The object type (title, text, chart, footer, or table)
    2. The issue category (e.g., "Clarity", "Design", "Content")
    3. A brief label for the issue (e.g., "Text is too small", "Chart is unclear")
    """
    llm  = ChatMistralAI(mistral_api_key=api_key, model=model)
    structured_llm = llm.with_structured_output(ExtractionResult)

    prompt=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=[
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_format.lower()};base64,{base64_image}"
                }
            }
        ])
    ]

    response = structured_llm.invoke(prompt)
    return response

def main():
    image_path = "data/01-coastal-presentation003.png"
    response = extract_issues(image_path)
    
    print(response)

    # Pretty print the extracted issues
    print("\nExtracted Issues:")
    for i, issue in enumerate(response.issues, 1):
        print(f"\nIssue {i}:")
        print(f"  Object Type: {issue.object_type}")
        print(f"  Category: {issue.issue_category}")
        print(f"  Label: {issue.issue_label}")

if __name__ == "__main__":
    main()

