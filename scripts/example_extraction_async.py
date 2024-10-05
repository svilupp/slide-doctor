import os
import asyncio
from typing import List
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
# from langchain_community.chat_models import ChatOpenAI
# from langchain_openai import ChatOpenAI # depends on langchain_community
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image
import base64
import io
from enum import Enum
from tqdm.asyncio import tqdm
import csv
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

# Initialize the Mistral client with instructor
api_key = os.getenv("MISTRAL_API_KEY")
model = "pixtral-12b-2409"  # Using Pixtral model for image analysis
semaphore = asyncio.Semaphore(4)

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

async def extract_issues(llm: ChatMistralAI, base64_image: str, image_format: str) -> ExtractionResult:
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
    structured_llm = llm.with_structured_output(ExtractionResult)

    prompt = [
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


    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=1, max=10))
    async def invoke_with_retry(structured_llm, prompt):
        return await structured_llm.ainvoke(prompt)

    response = await invoke_with_retry(structured_llm, prompt)
    return response

async def process_image(llm: ChatMistralAI, image_path: str, semaphore: asyncio.Semaphore) -> ExtractionResult:
    async with semaphore:
        base64_image, image_format = encode_image(image_path)
        result = await extract_issues(llm, base64_image, image_format)
        return result

async def main():
    image_path = "data/01-coastal-presentation003.png"
    llm = ChatMistralAI(mistral_api_key=api_key, model=model)

    # Assuming semaphore is defined elsewhere in the script
    tasks = [process_image(llm, image_path, semaphore) for _ in range(10)]
    results = await tqdm.gather(*tasks, total=len(tasks))
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    response = results[0]
    print(response)
    print("\nExtracted Issues:")
    for j, issue in enumerate(response.issues, 1):
        print(f"\nIssue {j}:")
        print(f"  Object Type: {issue.object_type}")
        print(f"  Category: {issue.issue_category}")
        print(f"  Label: {issue.issue_label}")


# Save results to a CSV file
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# csv_filename = f"scripts/extraction_results_{timestamp}.csv"

# with open(csv_filename, 'w', newline='') as csvfile:
#     fieldnames = ['Result_Number', 'Issue_Number', 'Object_Type', 'Category', 'Label']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
#     writer.writeheader()
#     for result_num, response in enumerate(results, 1):
#         for issue_num, issue in enumerate(response.issues, 1):
#             writer.writerow({
#                 'Result_Number': result_num,
#                 'Issue_Number': issue_num,
#                 'Object_Type': issue.object_type.value,
#                 'Category': issue.issue_category,
#                 'Label': issue.issue_label
#             })

# print(f"Results saved to {csv_filename}")

## Show one example in STDOUT

# if __name__ == "__main__":
#     asyncio.run(main())
