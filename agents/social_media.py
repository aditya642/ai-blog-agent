from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import BlogState, SocialMediaPosts
import json

class SocialMediaAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)

    def run(self, state: BlogState) -> Dict:
        print("--- Generating Social Media Posts ---")
        
        prompt = f"""
        Generate social media posts for the following blog article.
        
        Topic: {state.topic}
        Draft: {state.draft_blog[:5000]}
        
        Create:
        1. A Twitter (X) post (max 280 characters, with hashtags).
        2. A LinkedIn post (professional, insightful, with hashtags).
        3. An Instagram caption (engaging, visual-focused, with hashtags).
        
        Return the output as a JSON object with keys:
        - twitter
        - linkedin
        - instagram
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a social media manager expert. Return only valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            social_json = json.loads(content)
            social_posts = SocialMediaPosts(**social_json)
        except Exception as e:
            print(f"Error parsing social media posts: {e}")
            social_posts = None

        return {
            "social_posts": social_posts
        }
