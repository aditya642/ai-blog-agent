from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import BlogState, SEOData
import json

class SEOAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)

    def run(self, state: BlogState) -> Dict:
        print("--- Generating SEO Data ---")
        
        prompt = f"""
        Analyze the following blog draft and generate SEO metadata.
        
        Blog Draft:
        {state.draft_blog[:5000]}  # Send a snippet if too long
        
        Generate:
        1. SEO Title (max 60 chars)
        2. Meta Description (max 160 chars)
        3. 5-10 Keywords
        4. A URL slug
        
        Return the output as a JSON object with keys:
        - seo_title
        - meta_description
        - keywords (list)
        - slug
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an SEO expert. Return only valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            seo_json = json.loads(content)
            seo_data = SEOData(**seo_json)
        except Exception as e:
            print(f"Error parsing SEO data: {e}")
            seo_data = None

        return {
            "seo_data": seo_data
        }
