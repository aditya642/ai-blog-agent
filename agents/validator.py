from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import BlogState, ValidatedFact
import json

class ValidatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)

    def run(self, state: BlogState) -> Dict:
        print("--- Validating Facts ---")
        
        notes_combined = "\n".join([n.note for n in state.research_notes])
        
        prompt = f"""
        You are a fact-checker. Review the following research notes and extract 5-10 specific claims or facts.
        For each claim, validate it against the notes provided.
        Assign a status (supported, refuted, uncertain), a confidence score (0.0 to 1.0), and a brief reasoning.
        
        Research Notes:
        {notes_combined}
        
        Return the output as a JSON list of objects with the following keys:
        - claim
        - status
        - confidence
        - reasoning
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a meticulous fact-checker. Return only valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        # Parse the JSON response
        try:
            # Clean response content in case of markdown formatting
            content = response.content.replace("```json", "").replace("```", "").strip()
            facts_data = json.loads(content)
            validated_facts = [ValidatedFact(**f) for f in facts_data]
        except Exception as e:
            print(f"Error parsing validation response: {e}")
            validated_facts = []

        return {
            "validated_facts": validated_facts
        }
