import pytest
from workflows.state import BlogState

def test_blog_state_initialization():
    state = BlogState(topic="AI Agents")
    assert state.topic == "AI Agents"
    assert state.sources == []
    assert state.approved is False

def test_source_model():
    from workflows.state import Source
    source = Source(title="Test", url="http://test.com", content="Test content")
    assert source.title == "Test"
    assert source.url == "http://test.com"
