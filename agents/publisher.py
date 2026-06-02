import httpx
import markdown
from typing import Dict, Optional
from config import settings
from workflows.state import BlogState
from datetime import datetime

class PublisherAgent:
    def __init__(self):
        self.wp_url = settings.WP_URL
        self.username = settings.WP_USERNAME
        self.password = settings.WP_APP_PASSWORD

    def run(self, state: BlogState) -> Dict:
        print("--- Publishing to WordPress ---")
        
        if not state.approved:
            print("Article not approved for publishing.")
            return {"published_url": None}

        if not self.wp_url or not self.username or not self.password:
            print("WordPress credentials not configured. Skipping publish.")
            return {"published_url": "SKIPPED_CREDENTIALS_MISSING"}

        # Convert Markdown to HTML
        html_content = markdown.markdown(state.draft_blog)
        
        # WordPress Post Data
        post_data = {
            "title": state.seo_data.seo_title if state.seo_data else state.topic,
            "content": html_content,
            "status": "future" if state.scheduled_time else "publish",
            "slug": state.seo_data.slug if state.seo_data else None,
            "excerpt": state.seo_data.meta_description if state.seo_data else None,
        }
        
        if state.scheduled_time:
            # ISO 8601 format required by WP
            post_data["date"] = state.scheduled_time.isoformat()
            print(f"Scheduling post for: {post_data['date']}")

        # Note: Handling featured images requires a separate upload step usually.
        # For this version, we'll embed the image URL at the top of the content.
        if state.image_url:
            post_data["content"] = f'<img src="{state.image_url}" alt="Featured Image"><br>' + html_content

        try:
            response = httpx.post(
                f"{self.wp_url}/wp-json/wp/v2/posts",
                auth=(self.username, self.password),
                json=post_data,
                timeout=30.0
            )
            response.raise_for_status()
            published_data = response.json()
            published_url = published_data.get("link")
            print(f"Published successfully: {published_url}")
            return {"published_url": published_url}
        except Exception as e:
            print(f"Error publishing to WordPress: {e}")
            return {"published_url": f"ERROR: {str(e)}"}
