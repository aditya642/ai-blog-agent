from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import BlogState
import json
import openai

class ImageGenAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    def run(self, state: BlogState) -> Dict:
        print("--- Generating Image Prompt and Image ---")
        
        prompt_request = f"""
        Based on the following blog topic and draft, create a detailed, high-quality prompt for DALL-E 3 to generate a featured image for this blog post.
        The image should be professional, modern, and visually striking.
        
        Topic: {state.topic}
        Draft Snippet: {state.draft_blog[:1000]}
        
        Return ONLY the prompt string.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert at creating visual AI prompts."),
            HumanMessage(content=prompt_request)
        ])
        
        image_prompt = response.content.strip()
        image_url = "https://via.placeholder.com/1024x1024.png?text=AI+Generated+Image+Placeholder"
        
        if self.client:
            try:
                print(f"Calling DALL-E 3 with prompt: {image_prompt[:100]}...")
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
            except Exception as e:
                print(f"Error generating image with OpenAI: {e}")
        else:
            print("OpenAI API Key not found. Using placeholder image.")

        return {
            "image_prompt": image_prompt,
            "image_url": image_url
        }
