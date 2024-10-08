import asyncio
from mistralai import Mistral
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, wait_exponential
import json
import weave
from pydantic import BaseModel
from typing import Any, Dict, List
from .image_utils import get_image_data_url, encode_image
import numpy as np

class MistralClientWrapper:
    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)

    @staticmethod
    def build_tools_and_choice(ResponseModel: BaseModel) -> Dict[str, Any]:
        return {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "ExtractData",
                        "description": "A function to process and return the structured response.",
                        "parameters": ResponseModel.model_json_schema(),
                    },
                }
            ],
            "tool_choice": {
                "type": "function",
                "function": {"name": "ExtractData"},
            }
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type((ValueError, json.JSONDecodeError))
    )
    @weave.op()
    async def complete_with_retry(self, model: str, messages: list, ResponseModel: BaseModel) -> BaseModel:
        tools = self.build_tools_and_choice(ResponseModel)
        
        res = await self.client.chat.complete_async(
            model=model,
            messages=messages,
            **tools
        )
        
        try:
            content = res.choices[0].message.tool_calls[0].function.arguments
            # Validate the response using Pydantic
            validated_response = ResponseModel.model_validate_json(content)
            return validated_response
        except Exception as e:
            ## TODO: fix to change retry strategy for different errors
            raise  # This will be caught by the retry decorator

    @staticmethod
    def build_messages(system_prompt: str, user_prompt: str, image_path: str = None) -> list:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": []
            }
        ]
        
        # Add text content to user message
        messages[1]["content"].append({
            "type": "text",
            "text": user_prompt
        })
        
        # Add image content if provided
        if image_path:
            encoded_image, image_format = encode_image(image_path)
            image_data_url = get_image_data_url(encoded_image, image_format)
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": image_data_url
                }
            })
        
        return messages

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
    )
    def get_embeddings(self, model: str, texts: List[str]) -> List[np.ndarray]:
        """
        Get embeddings for a list of strings.

        Args:
            model (str): The model to use for generating embeddings.
            texts (List[str]): A list of strings to embed.

        Returns:
            List[np.ndarray]
        """
        try:
            embeddings_batch_response = self.client.embeddings.create(
                model=model,
                inputs=texts,
            )
            return [np.array(embedding.embedding) for embedding in embeddings_batch_response.data]
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            raise