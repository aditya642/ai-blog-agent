import os
from typing import List, Dict
from playwright.sync_api import sync_playwright
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from workflows.state import Source, ResearchNote, BlogState
from bs4 import BeautifulSoup
import json
import time

class ResearchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)

    def run(self, state: BlogState) -> Dict:
        print(f"--- Researching Topic (Playwright): {state.topic} ---")
        
        sources = []
        research_notes = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Search using DuckDuckGo
            search_url = f"https://duckduckgo.com/?q={state.topic.replace(' ', '+')}&ia=web"
            print(f"Searching: {search_url}")
            page.goto(search_url)
            page.wait_for_selector("article")
            
            # Extract top 3-5 links
            links = page.eval_on_selector_all(
                "article a[data-testid='result-title-a']", 
                "elements => elements.map(e => e.href)"
            )[:3]
            
            print(f"Found {len(links)} top links. Visiting...")
            
            for url in links:
                try:
                    print(f"Visiting: {url}")
                    page.goto(url, timeout=30000)
                    time.sleep(2) # Allow for some JS rendering
                    
                    title = page.title()
                    # Get text content and clean it up a bit
                    content = page.inner_text("body")
                    
                    source = Source(
                        title=title,
                        url=url,
                        content=content[:10000] # Limit content to avoid token issues
                    )
                    sources.append(source)
                    
                    # 2. Extract facts/notes using LLM
                    prompt = f"""
                    Extract key facts, statistics, and research notes from the following content about the topic: {state.topic}
                    
                    Content:
                    {source.content}
                    
                    Return the information as a bulleted list of notes.
                    """
                    
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    research_notes.append(ResearchNote(
                        source_url=source.url,
                        note=response.content
                    ))
                except Exception as e:
                    print(f"Error visiting {url}: {e}")
            
            browser.close()

        return {
            "sources": sources,
            "research_notes": research_notes
        }
