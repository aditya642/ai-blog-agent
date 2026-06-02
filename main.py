import argparse
import sys
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from workflows.blog_graph import create_blog_graph
from config import settings
import uuid

def run_workflow(topic: str):
    print(f"Starting blog generation for topic: {topic}")
    
    # Initialize SQLite checkpointer
    conn = sqlite3.connect("storage/checkpoints.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # Create and compile graph
    workflow = create_blog_graph()
    app = workflow.compile(checkpointer=memory, interrupt_before=["publisher"])
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "topic": topic,
        "sources": [],
        "research_notes": [],
        "validated_facts": [],
        "draft_blog": "",
        "seo_data": None,
        "review_report": None,
        "image_url": "",
        "image_prompt": "",
        "social_posts": None,
        "approved": False,
        "scheduled_time": None,
        "published_url": ""
    }
    
    # Execute until interrupt
    print("Executing workflow...")
    for event in app.stream(initial_state, config):
        for node, state in event.items():
            print(f"Finished node: {node}")

    # After interrupt, ask for approval
    state = app.get_state(config)
    print("\n--- Review Required ---")
    print(f"Draft Blog saved to outputs/draft.md")
    print(f"Review Report saved to outputs/review.json")
    
    approval = input("\nApprove for publishing to WordPress? (yes/no): ").lower()
    
    if approval == "yes":
        app.update_state(config, {"approved": True})
        print("Resuming workflow for publishing...")
        for event in app.stream(None, config):
            for node, state in event.items():
                print(f"Finished node: {node}")
    else:
        print("Publishing cancelled.")

def main():
    parser = argparse.ArgumentParser(description="AI Autonomous Blog System")
    parser.add_argument("--topic", type=str, help="Topic for the blog post")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.topic:
        run_workflow(args.topic)
    elif args.interactive:
        topic = input("Enter Topic: ")
        run_workflow(topic)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
