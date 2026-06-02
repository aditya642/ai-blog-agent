from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Source(BaseModel):
    title: str
    url: str
    content: str

class ResearchNote(BaseModel):
    source_url: str
    note: str

class Fact(BaseModel):
    claim: str
    source_url: str
    context: Optional[str] = None

class ValidatedFact(BaseModel):
    claim: str
    status: str  # supported, refuted, uncertain
    confidence: float
    reasoning: str

class SEOData(BaseModel):
    seo_title: str
    meta_description: str
    keywords: List[str]
    slug: str

class ReviewReport(BaseModel):
    readability: int
    seo_score: int
    quality_score: int
    issues: List[str]

class SocialMediaPosts(BaseModel):
    twitter: str
    linkedin: str
    instagram: str

class BlogState(BaseModel):
    topic: str
    sources: List[Source] = []
    research_notes: List[ResearchNote] = []
    validated_facts: List[ValidatedFact] = []
    draft_blog: str = ""
    seo_data: Optional[SEOData] = None
    review_report: Optional[ReviewReport] = None
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    social_posts: Optional[SocialMediaPosts] = None
    approved: bool = False
    scheduled_time: Optional[datetime] = None
    published_url: Optional[str] = None
