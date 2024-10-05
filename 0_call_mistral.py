# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "asyncio",
#     "base64",
#     "io",
#     "langchain_mistralai",
#     "langchain_core",
#     "pillow",
# ]
# ///
import os
import asyncio
from PIL import Image
import base64
import io
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

# Initialize the Mistral client
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"
chat = ChatMistralAI(mistral_api_key=api_key, model=model)

# Define a simple prompt
prompt = "Hello, Mistral! How are you today?"

# Call the model
response = chat.invoke([HumanMessage(content=prompt)])

# Print the response
print("Mistral's response:")
print(response.content)

def encode_image(image_path):
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

async def analyze_image(chat, base64_image, system_prompt, user_prompt):
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=[
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ])
    ]
    
    response = await chat.ainvoke(messages)
    
    return response.content

chat_pixtral = ChatMistralAI(mistral_api_key=api_key, model="pixtral-12b-2409")
image_path = "xxx.png"
base64_image = encode_image(image_path)

system_prompt = "You are an AI specialized in reading images."
user_prompt = "What do you see in this image?"

async def main():
    result = await analyze_image(chat_pixtral, base64_image, system_prompt, user_prompt)
    print("Pixtral's response:")
    print(result)

asyncio.run(main())
