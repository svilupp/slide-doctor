# Asynchronous Example
import asyncio
from mistralai import Mistral
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import os
from pydantic import BaseModel, Field
from typing import List

class Painter(BaseModel):
    name: str = Field(description="The name of the French painter")

 # @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=1, max=10))
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((ValueError, json.JSONDecodeError))
)
async def get_painter_with_retry(client):
    tools = get_tools_and_choice(Painter)
    res = await client.chat.complete_async(model="mistral-small-latest", messages=[
        {
            "content": f"""You are a helpful assistant that extracts information about painters from a given text.""",
            "role": "system",
        },
        {
            "content": "Who is the best French painter? Answer in one short sentence.",
            "role": "user",
        },
    ], **tools)
    
    content = res.choices[0].message.tool_calls[0].function.arguments
    print(content)
    try:
        # Validate the response using Pydantic
        painter = Painter.model_validate_json(content)
        return painter
    except Exception as e:
        raise  # This will be caught by the retry decorator
        
def get_tools_and_choice(ResponseModel):
    dictionary = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "ExtractPainter",
                    "description": "A function to process and return the structured response.",
                    "parameters": ResponseModel.model_json_schema(),
                },
            }
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": "ExtractPainter"},
        }
    }
    return dictionary

async def main():
    client = Mistral(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
    )
    tasks = [get_painter_with_retry(client) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
    