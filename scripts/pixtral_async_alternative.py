# Asynchronous Example with Pixtral Model and Image Description
import asyncio
from mistralai import Mistral
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import json
import os
from pydantic import BaseModel, Field
from typing import List
from PIL import Image
import base64
import io
from enum import Enum

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

def get_tools_and_choice(ResponseModel):
    dictionary = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "ExtractPainterAndDescription",
                    "description": "A function to process and return the structured response including painter and image description.",
                    "parameters": ResponseModel.model_json_schema(),
                },
            }
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": "ExtractPainterAndDescription"},
        }
    }
    return dictionary


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((ValueError, json.JSONDecodeError))
)
async def get_issues_with_retry(client, image_format, encoded_image):
    tools = get_tools_and_choice(ExtractionResult)
    

    res = await client.chat.complete_async(
        model="pixtral-12b-2409",  # Update to use Pixtral model
        messages=[
            {
                "content": "You are a helpful assistant and your task is to extract the requested data.",
                "role": "system",
            },
            {
                "content": [
                    {
                        "type": "text",
                        "text": "What are the issues in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ],
                "role": "user",
            },
        ],
        **tools
    )
    
    content = res.choices[0].message.tool_calls[0].function.arguments
    try:
        # Validate the response using Pydantic
        issues = ExtractionResult.model_validate_json(content)
        return issues
    except Exception as e:
        raise  # This will be caught by the retry decorator
        
async def main():
    client = Mistral(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
    )
    image_path = "data/01-coastal-presentation003.png"
    base64_image, image_format = encode_image(image_path)
    
    tasks = [get_issues_with_retry(client, image_format, base64_image) for _ in range(50)]
    results = await asyncio.gather(*tasks)
    
    # for i, result in enumerate(results, 1):
    #     print(f"Result {i}: Issues: {result.issues}")

    print(f"Results: {results[0].issues}")

if __name__ == "__main__":
    asyncio.run(main())