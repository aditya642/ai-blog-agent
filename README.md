# AI Autonomous Blog System

A production-quality multi-agent system built with LangGraph, LangChain, and Gemini to research, write, and publish high-quality blog posts.

## Features
- **Research Agent**: Deep web search using Tavily.
- **Fact Validation**: Cross-referencing claims for accuracy.
- **AI Blog Writer**: Long-form, engaging content generation (1500-2500 words).
- **SEO Optimization**: Metadata and slug generation.
- **Editorial Review**: Quality scoring and issue identification.
- **Human-in-the-Loop**: Approval step before publishing.
- **WordPress Integration**: Direct publishing via REST API.

## Installation

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys:
   - `GOOGLE_API_KEY`: Get from Google AI Studio.
   - `TAVILY_API_KEY`: Get from Tavily.
   - WordPress credentials (optional).

## Usage

### CLI
Run for a specific topic:
```bash
python main.py --topic "The Future of Generative AI"
```

Interactive mode:
```bash
python main.py --interactive
```

### API
Start the FastAPI server:
```bash
python api/server.py
```
Then use the `/generate` endpoint to trigger workflows.

## Project Structure
- `agents/`: Individual agent implementations.
- `workflows/`: LangGraph workflow definition.
- `outputs/`: Saved research, drafts, and reviews.
- `storage/`: SQLite database for state persistence.

## Docker
Build and run using Docker Compose:
```bash
docker-compose up --build
```
