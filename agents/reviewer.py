from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import BlogState, ReviewReport
import json

class ReviewerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)

    def run(self, state: BlogState) -> Dict:
        print("--- Reviewing Blog Article ---")
        
        prompt = f"""
        Review the following blog article for grammar, style, readability, SEO optimization, and factual consistency.
        
        Blog Draft:
        {state.draft_blog[:5000]}
        
        SEO Data:
        {state.seo_data.model_dump_json() if state.seo_data else "None"}
        
        Generate a review report with the following:
        1. Readability Score (0-100)
        2. SEO Score (0-100)
        3. Overall Quality Score (0-100)
        4. A list of specific issues or suggestions for improvement.
        
        Return the output as a JSON object with keys:
        - readability
        - seo_score
        - quality_score
        - issues (list of strings)
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a strict editorial reviewer. Return only valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        try:
            content = response.content.replace("```json", "").replace("```", "").strip()
            review_json = json.loads(content)
            review_report = ReviewReport(**review_json)
        except Exception as e:
            print(f"Error parsing review report: {e}")
            review_report = None

        return {
            "review_report": review_report
        }
