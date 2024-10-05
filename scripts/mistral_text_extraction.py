import os
from typing import List
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image
import base64
import io
from enum import Enum
from pptx import Presentation
import json

# Initialize the Mistral client with instructor
api_key = os.getenv("MISTRAL_API_KEY")
# model = "pixtral-12b-2409"  # Using Pixtral model for image analysis
model = "mistral-large-latest"


def pptx_to_json(slide_deck_path):
    prs = Presentation(slide_deck_path)
    
    slides_content = []
    
    placeholder_mapping = {
        0: "title",
        1: "subtitle",
        2: "body",
        3: "center_title",
        4: "center_subtitle",
        5: "footer",
        6: "date",
        7: "slide_number",
        8: "header",
    }
    
    # Iterate over slides
    for slide_index, slide in enumerate(prs.slides):
        slide_data = {"slide_index": slide_index, "content": []}
        
        # Iterate over all shapes in the slide
        for shape in slide.shapes:
            # Check if shape has text content
            if shape.has_text_frame:
                # Check if the shape is a placeholder
                if shape.is_placeholder:
                    placeholder_type = shape.placeholder_format.type
                    
                    # Map placeholder to a human-readable type name
                    placeholder_name = placeholder_mapping.get(placeholder_type, "unknown_placeholder")
                    
                    slide_data['content'].append({
                        "type": placeholder_name,
                        "text": shape.text
                    })
                else:
                    # If not a placeholder but has text, consider it a regular shape with text
                    slide_data['content'].append({
                        "type": "shape",
                        "text": shape.text
                    })
            
            # Handle non-text placeholder types (e.g., slide number, date, footer)
            elif shape.is_placeholder:
                placeholder_type = shape.placeholder_format.type
                
                # Map placeholder to a human-readable type name
                placeholder_name = placeholder_mapping.get(placeholder_type, "unknown_placeholder")
                
                if placeholder_name in ["footer", "date", "slide_number"]:
                    slide_data['content'].append({
                        "type": placeholder_name,
                        "text": shape.text if shape.has_text_frame else ""
                    })
        
        slides_content.append(slide_data)
    print('slides_content length: ', len(slides_content))
    
    return slides_content

# Example usage
# slide_deck_path = "your_slide_deck.pptx"
# slides_json = pptx_to_json(slide_deck_path)
# print(slides_json)


# print(slides_json)


# Define the output schema
class ObjectType(Enum):
    TITLE = "title"
    TEXT = "text"
    FOOTER = "footer"
    BODY = "body"

class Issue(BaseModel):
    object_type: ObjectType = Field(description="The type of object, from the enum: title, text, chart, footer, table")
    issue_category: str = Field(description="The category of the issue")
    issue_label: str = Field(description="The label of the issue")
    issue_reason: str = Field(description="Reason behind flagging this as an issue")

class ExtractionResult(BaseModel):
    issues: List[Issue] = Field(description="List of extracted issues")


# def encode_image(image_path: str) -> tuple[str, str]:
#     if image_path.lower().endswith('.png'):
#         image_format = "PNG"
#     elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
#         image_format = "JPEG"
#     else:
#         raise ValueError("Unsupported image format. Only PNG and JPEG are allowed.")
#     with Image.open(image_path) as img:
#         buffer = io.BytesIO()
#         img.save(buffer, format=image_format)
#         return base64.b64encode(buffer.getvalue()).decode('utf-8'), image_format


def extract_issues(slides_text: str) -> ExtractionResult:
    # base64_image, image_format = encode_image(image_path)

    system_prompt = """
    You are an AI specialized in identifying issues in PowerPoint presentation screenshots.
    Your task is to carefully examine the provided text which is extracted from slides of a .pptx file and identify any problems or areas for improvement related to the slide's content and overall effectiveness.
    Focus on detecting issues such as:
    1. Clarity and readability of text
    2. Spelling mistakes and Effectiveness
    3. organization of information
    4. Consistency in formatting
    5. Appropriateness of content for the intended audience
    Provide a comprehensive analysis of the issues present in the text per slide
    """

    user_prompt = """
    Analyze this slide text and identify issues. For each issue, provide:
    1. The object type (title, text, footer, table)
    2. The issue category (e.g., "Clarity", "Content")
    3. A brief label for the issue (e.g., "Text is too small", "Text does not look professional")
    """

    llm  = ChatMistralAI(mistral_api_key=api_key, model=model)
    structured_llm = llm.with_structured_output(ExtractionResult)

    prompt=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=[
            {"type": "text", "text": user_prompt},
            # {
            #     "type": "image_url",
            #     "image_url": {
            #         "url": f"data:image/{image_format.lower()};base64,{base64_image}"
            #     }
            # }
        ])
    ]

    response = structured_llm.invoke(prompt)
    return response

def main():

    slide_deck_path = "../data/01-coastal-presentation.pptx"
    slides_json = pptx_to_json(slide_deck_path)

    print('slides_json: ', slides_json)

    print("slides_json length: ", len(slides_json))

    for idx, slide_json in enumerate(slides_json):
        print(f'SLIDE {idx}')
        print('-------------------------------------')
        print('slide_json: ', slide_json)
        slide_response = extract_issues(slide_json)
    
    # print(issues)

    # Pretty print the extracted issues
        print("\nExtracted Issues:")
        for i, issue in enumerate(slide_response.issues, 1):
            print(f"\nIssue {i}:")
            print(f"  Object Type: {issue.object_type}")
            print(f"  Category: {issue.issue_category}")
            print(f"  Label: {issue.issue_label}")
            print(f"  Reason: {issue.issue_reason}")

if __name__ == "__main__":
    main()

