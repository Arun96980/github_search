# GitHub Neural Search

A minimalist, aesthetic AI-powered search interface for GitHub repositories.

## Features

- **AI Search**: Use natural language to find repositories (powered by Gemini 2.0 Flash).
- **Manual Filters**: Fine-tune your search with specific criteria.
- **Modern UI**: Glassmorphism design, dark mode, and smooth animations.

## Setup

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

2. Ensure your `.env` file has your `GOOGLE_API_KEY`.

## Running the App

Run the server:
```bash
python app.py
```
Or with hot reload:
```bash
uvicorn app:app --reload
```

Open your browser to: `http://localhost:8000`
