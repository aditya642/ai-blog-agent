from fastapi import FastAPI, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import uuid
import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver
from workflows.blog_graph import create_blog_graph

app = FastAPI(title="AI Blog Agent API")

# Setup templates
templates = Jinja2Templates(directory="api/templates")

class TopicRequest(BaseModel):
    topic: str

def get_db():
    conn = sqlite3.connect("storage/checkpoints.db", check_same_thread=False)
    return conn

def get_graph(conn):
    memory = SqliteSaver(conn)
    workflow = create_blog_graph()
    return workflow.compile(checkpointer=memory, interrupt_before=["publisher"])

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = get_db()
    graph = get_graph(conn)
    
    # This is a bit of a hack to list threads in LangGraph, 
    # normally you'd track these in a separate DB table.
    # For now, we'll just show what's in the checkpoints.
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
    threads = [row[0] for row in cursor.fetchall()]
    
    pending_tasks = []
    for tid in threads:
        state = graph.get_state({"configurable": {"thread_id": tid}})
        if state.next and "publisher" in state.next:
            pending_tasks.append({
                "thread_id": tid,
                "values": state.values
            })
            
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pending_tasks": pending_tasks
    })

@app.get("/review/{thread_id}", response_class=HTMLResponse)
async def review_page(request: Request, thread_id: str):
    conn = get_db()
    graph = get_graph(conn)
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    
    return templates.TemplateResponse("review.html", {
        "request": request,
        "task": {"thread_id": thread_id, "values": state.values}
    })

@app.post("/approve/{thread_id}")
async def approve_task(thread_id: str, request: Request):
    form_data = await request.form()
    scheduled_time_str = form_data.get("scheduled_time")
    scheduled_time = None
    if scheduled_time_str:
        from datetime import datetime
        try:
            scheduled_time = datetime.fromisoformat(scheduled_time_str)
        except ValueError:
            pass

    conn = get_db()
    graph = get_graph(conn)
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update state to approved and set scheduled time
    graph.update_state(config, {"approved": True, "scheduled_time": scheduled_time})
    
    # Resume the graph in the background
    # Since we are in a request handler, we should run it as a background task
    import threading
    def resume():
        for event in graph.stream(None, config):
            pass
            
    thread = threading.Thread(target=resume)
    thread.start()
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/generate")
async def generate_blog(request: TopicRequest, background_tasks: BackgroundTasks):
    thread_id = str(uuid.uuid4())
    background_tasks.add_task(run_background_workflow, request.topic, thread_id)
    return {"message": "Blog generation started", "thread_id": thread_id}

def run_background_workflow(topic: str, thread_id: str):
    conn = get_db()
    graph = get_graph(conn)
    
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
    
    for event in graph.stream(initial_state, config):
        pass

@app.get("/status/{thread_id}")
async def get_status(thread_id: str):
    conn = get_db()
    graph = get_graph(conn)
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    
    if not state.values:
        return {"status": "not_found"}
        
    return {
        "next": state.next,
        "values": state.values
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
