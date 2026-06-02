from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import BlogState
import json

class WriterAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)

    def run(self, state: BlogState) -> Dict:
        print("--- Writing Blog Draft ---")
        
        facts_summary = "\n".join([f"- {f.claim} (Status: {f.status})" for f in state.validated_facts if f.status == "supported"])
        notes_combined = "\n".join([n.note for n in state.research_notes])
        
        prompt = f"""
        You are a professional blog writer. Write a comprehensive, engaging, and high-quality blog article about: {state.topic}
        
        Target Length: 1500-2500 words.
        
        Use the following validated facts and research notes to inform your writing. 
        DO NOT invent facts. ONLY use the provided information.
        
        Validated Facts:
        {facts_summary}
        
        Research Notes:
        {notes_combined}
        
        Structure:
        1. Title: A compelling and relevant title.
        2. Introduction: Hook the reader and introduce the topic.
        3. Main Sections: Use clear headings and subheadings. Explore the topic in depth.
        4. Examples/Case Studies: Illustrate points with real-world examples from the research.
        5. Key Takeaways: A bulleted list of the most important points.
        6. FAQ: Answer common questions about the topic.
        7. Conclusion: Summarize the article and provide a final thought.
        
        Format the article in Markdown.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert blog writer who specializes in detailed, authoritative, and engaging long-form content."),
            HumanMessage(content=prompt)
        ])
        
        return {
            "draft_blog": response.content
        }
