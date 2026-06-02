from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from workflows.state import BlogState, SocialMediaPosts
from agents.research import ResearchAgent
from agents.validator import ValidatorAgent
from agents.writer import WriterAgent
from agents.seo import SEOAgent
from agents.reviewer import ReviewerAgent
from agents.publisher import PublisherAgent
from agents.image_gen import ImageGenAgent
from agents.social_media import SocialMediaAgent
from utils import save_output

# Define the state for LangGraph
class GraphState(TypedDict):
    topic: str
    sources: List[Any]
    research_notes: List[Any]
    validated_facts: List[Any]
    draft_blog: str
    seo_data: Any
    review_report: Any
    image_url: str
    image_prompt: str
    social_posts: Any
    approved: bool
    scheduled_time: Any
    published_url: str

def create_blog_graph():
    # Initialize agents
    research_agent = ResearchAgent()
    validator_agent = ValidatorAgent()
    writer_agent = WriterAgent()
    seo_agent = SEOAgent()
    reviewer_agent = ReviewerAgent()
    image_agent = ImageGenAgent()
    social_agent = SocialMediaAgent()
    publisher_agent = PublisherAgent()

    # Define nodes
    def research_node(state: GraphState):
        blog_state = BlogState(**state)
        result = research_agent.run(blog_state)
        save_output("research.json", [s.model_dump() for s in result['sources']])
        return result

    def validate_node(state: GraphState):
        blog_state = BlogState(**state)
        result = validator_agent.run(blog_state)
        save_output("validated.json", [f.model_dump() for f in result['validated_facts']])
        return result

    def write_node(state: GraphState):
        blog_state = BlogState(**state)
        result = writer_agent.run(blog_state)
        save_output("draft.md", result['draft_blog'])
        return result

    def seo_node(state: GraphState):
        blog_state = BlogState(**state)
        result = seo_agent.run(blog_state)
        if result['seo_data']:
            save_output("seo.json", result['seo_data'].model_dump())
        return result

    def image_node(state: GraphState):
        blog_state = BlogState(**state)
        result = image_agent.run(blog_state)
        return result

    def social_node(state: GraphState):
        blog_state = BlogState(**state)
        result = social_agent.run(blog_state)
        if result['social_posts']:
            save_output("social.json", result['social_posts'].model_dump())
        return result

    def review_node(state: GraphState):
        blog_state = BlogState(**state)
        result = reviewer_agent.run(blog_state)
        if result['review_report']:
            save_output("review.json", result['review_report'].model_dump())
        return result

    def publisher_node(state: GraphState):
        blog_state = BlogState(**state)
        result = publisher_agent.run(blog_state)
        return result

    # Build graph
    workflow = StateGraph(GraphState)

    workflow.add_node("research", research_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("write", write_node)
    workflow.add_node("seo", seo_node)
    workflow.add_node("image", image_node)
    workflow.add_node("social", social_node)
    workflow.add_node("reviewer", review_node)
    workflow.add_node("publisher", publisher_node)

    # Set edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "validate")
    workflow.add_edge("validate", "write")
    workflow.add_edge("write", "seo")
    workflow.add_edge("seo", "image")
    workflow.add_edge("image", "social")
    workflow.add_edge("social", "reviewer")
    workflow.add_edge("reviewer", "publisher")
    workflow.add_edge("publisher", END)

    return workflow
