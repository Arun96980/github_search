"""
GitHub Repository Search - Gemini 2.0 Flash Parser
Clean, efficient, production-ready code
"""

import os
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Add it to .env file")

# Initialize Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# GitHub API headers
headers = {"Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def parse_query(user_query: str) -> dict:
    """Parse natural language query using Gemini 2.0 Flash"""
    
    prompt = f"""Convert this GitHub search query to JSON filters.

Available filters:
- language: string (e.g., "python", "javascript")
- topics: array (e.g., ["web", "api"])
- stars: object (e.g., {{"min": 100, "max": 2000}})
- license: string (e.g., "mit")
- issues: object (e.g., {{"good_first_issue": true}})
- updated_after: date (e.g., "2023-01-01")

Handle spelling mistakes intelligently.

Query: "{user_query}"

Return ONLY valid JSON with these defaults:
{{"archived": false, "include_forks": false, "sort": "stars", "order": "desc", "limit": 10}}

JSON:"""

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        
        # Clean markdown if present
        if '```' in json_text:
            json_text = json_text.split('```')[1]
            if json_text.startswith('json'):
                json_text = json_text[4:].strip()
        
        return json.loads(json_text)
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return {"archived": False, "include_forks": False, "sort": "stars", "order": "desc", "limit": 10}


def build_github_query(filters: dict) -> str:
    """Build GitHub search query string from filters"""
    
    parts = []
    
    if filters.get("language"):
        parts.append(f"language:{filters['language']}")
    
    if stars := filters.get("stars"):
        min_s = stars.get("min", 0)
        max_s = stars.get("max", 500000)
        parts.append(f"stars:{min_s}..{max_s}")
    
    for topic in filters.get("topics", []):
        parts.append(f"topic:{topic}")
    
    if filters.get("license"):
        parts.append(f"license:{filters['license']}")
    
    if issues := filters.get("issues"):
        if issues.get("good_first_issue"):
            parts.append("good-first-issues:>0")
        if issues.get("help_wanted"):
            parts.append("help-wanted-issues:>0")
    
    if filters.get("updated_after"):
        parts.append(f"pushed:>{filters['updated_after']}")
    
    if filters.get("created_after"):
        parts.append(f"created:>{filters['created_after']}")
    
    parts.append("fork:false" if not filters.get("include_forks") else "fork:true")
    parts.append("archived:false" if not filters.get("archived") else "archived:true")
    
    return " ".join(parts)


def search_github(filters: dict) -> dict:
    """Search GitHub repositories"""
    
    query = build_github_query(filters)
    
    params = {
        "q": query,
        "sort": filters.get("sort", "stars"),
        "order": filters.get("order", "desc"),
        "per_page": filters.get("limit", 10),
        "page": filters.get("page", 1),
    }
    
    try:
        response = requests.get(
            "https://api.github.com/search/repositories",
            headers=headers,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub API error: {e}")
        return None


def search(user_query: str):
    """Main search function - parse query and search GitHub"""
    
    print(f"\n💬 Query: \"{user_query}\"")
    
    # Parse with Gemini
    filters = parse_query(user_query)
    
    print("\n📋 Filters:")
    for key, value in filters.items():
        if value and key not in ['archived', 'include_forks', 'sort', 'order']:
            print(f"   • {key}: {value}")
    
    # Search GitHub
    print(f"\n🔍 GitHub Query: {build_github_query(filters)}")
    
    data = search_github(filters)
    
    if not data:
        print("\n❌ Search failed")
        return None
    
    total = data.get("total_count", 0)
    items = data.get("items", [])
    
    print(f"\n✅ Found {total} repositories\n")
    
    if items:
        for i, repo in enumerate(items, 1):
            print(f"{i}. {repo['full_name']} ({repo['stargazers_count']} ⭐)")
            print(f"   {repo['html_url']}")
            if desc := repo.get('description'):
                print(f"   {desc}")
            if topics := repo.get('topics'):
                print(f"   🏷️  {', '.join(topics[:5])}")
            print()
    else:
        print("⚠️ No results. Try a different query.")
    
    return data


def interactive():
    """Interactive mode"""
    
    print("\n" + "="*70)
    print("🔍 GitHub Repository Search - Powered by Gemini 2.0 Flash")
    print("="*70)
    print("\nExamples:")
    print('  • "good python first issue"')
    print('  • "pythn machne lerning" (spelling OK!)')
    print('  • "javascript web 500+ stars"')
    print("\nType 'quit' to exit.\n")
    
    while True:
        try:
            query = input("🔎 Search: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            search(query)
            print("-"*70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # CLI mode: python main.py "good python first issue"
        search(" ".join(sys.argv[1:]))
    else:
        # Interactive mode
        interactive()
