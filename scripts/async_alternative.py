# Asynchronous Example
import asyncio
from mistralai import Mistral
import os
from pydantic import BaseModel, Field
from typing import List

class Painter(BaseModel):
    name: str = Field(description="The name of the French painter")

async def get_best_french_painter():
    s = Mistral(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
    )
    res = await s.chat.complete_async(model="mistral-small-latest", messages=[
        {
            "content": "Who is the best French painter? Answer in one short sentence.",
            "role": "user",
        },
    ], 
    response_format="json_object", **get_tools_and_choice(Painter))
    
    return res.choices[0].message.content if res else None

async def get_tools_and_choice(ResponseModel):
    return {
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
        },
    }

async def main():
    tasks = [get_best_french_painter() for _ in range(50)]
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}: {result}")

if __name__ == "__main__":
    asyncio.run(main())