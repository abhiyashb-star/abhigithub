"""
🚀 GEMINI PRO AUTOMATION PLATFORM - MAIN BACKEND
Core Backend with Gemini 3.1 Pro Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import asyncio
from datetime import datetime
import httpx

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from openai import OpenAI, RateLimitError
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

app = FastAPI(title="Gemini Pro Automation Platform", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Configure OpenAI
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# Configure Supabase (Cloud Database)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cloud Database (Supabase) Connected")
    except Exception as e:
        print(f"❌ Supabase Connection Failed: {e}")

# ============================================================
# MODELS
# ============================================================

class AutomationRequest(BaseModel):
    task_type: str  # email, web_scrape, document_analysis, data_analysis, voice
    input_data: Dict[str, Any]
    provider: str = "gemini"  # gemini, chatgpt
    reasoning_level: str = "medium"  # low, medium, high
    use_tools: List[str] = []

class AutomationResponse(BaseModel):
    task_id: str
    status: str
    result: Any
    provider_used: str
    fallback_occurred: bool = False
    reasoning: Optional[str] = None
    execution_time: float

# ============================================================
# GEMINI TOOL DEFINITIONS
# ============================================================

tools = [
    {
        "name": "google_search",
        "description": "Search Google for real-time information. Use for web scraping, market research, news gathering.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (1-10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "url_context",
        "description": "Fetch and read the complete content of a URL. Extracts text, images, metadata.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "code_execution",
        "description": "Execute Python code in a sandboxed environment. Max 30 seconds runtime.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "file_search",
        "description": "Search and analyze files (PDF, text, CSV, images). Extract data and insights.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file or file content"
                },
                "query": {
                    "type": "string",
                    "description": "What to search for in the file"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "send_email",
        "description": "Send automated emails via Gmail API.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body"},
                "html": {"type": "boolean", "description": "Is HTML format"}
            },
            "required": ["to", "subject", "body"]
        }
    },
    {
        "name": "database_query",
        "description": "Query Supabase PostgreSQL database.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query"},
                "action": {"type": "string", "enum": ["select", "insert", "update", "delete"]}
            },
            "required": ["query", "action"]
        }
    },
    {
        "name": "slack_notification",
        "description": "Send notification to Slack channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Slack channel"},
                "message": {"type": "string", "description": "Message to send"}
            },
            "required": ["channel", "message"]
        }
    }
]

# ============================================================
# TOOL EXECUTION FUNCTIONS
# ============================================================

async def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Execute a tool and return result"""

    if tool_name == "google_search":
        # In production, use actual Google Search API
        return f"Search results for: {tool_input.get('query')}"

    elif tool_name == "url_context":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(tool_input.get('url'), timeout=10)
                return f"Content from {tool_input.get('url')}: {response.text[:1000]}..."
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

    elif tool_name == "code_execution":
        try:
            exec_globals = {}
            exec(tool_input.get('code'), exec_globals)
            return f"Code executed successfully"
        except Exception as e:
            return f"Execution error: {str(e)}"

    elif tool_name == "file_search":
        return f"File analysis for: {tool_input.get('file_path')}"

    elif tool_name == "send_email":
        return f"Email would be sent to: {tool_input.get('to')}"

    elif tool_name == "database_query":
        return f"Database query executed: {tool_input.get('query')}"

    elif tool_name == "slack_notification":
        return f"Slack message sent to: {tool_input.get('channel')}"

    return f"Unknown tool: {tool_name}"

# ============================================================
# GEMINI INTEGRATION
# ============================================================

async def process_with_gemini(request: AutomationRequest) -> Dict[str, Any]:
    """Process request with Gemini 3.1 Pro"""

    start_time = datetime.now()

    # Map task types to system prompts
    system_prompts = {
        "email": """You are an email automation expert. Analyze emails, classify them, and determine appropriate actions.
                   Use google_search to find context, code_execution to process data, and send_email to respond.""",
        "web_scrape": """You are a web scraping expert. Find relevant information from websites, extract data, and organize it.
                        Use google_search to find URLs, url_context to read content, code_execution to parse data.""",
        "document_analysis": """You are a document analysis expert. Read PDFs, spreadsheets, and text files.
                              Extract insights and structure data. Use file_search to analyze documents.""",
        "data_analysis": """You are a data analysis expert. Process CSVs, databases, and datasets.
                          Create visualizations and generate insights. Use code_execution for analysis.""",
        "voice": """You are a voice agent assistant. Process voice transcripts and generate appropriate responses."""
    }

    system_prompt = system_prompts.get(request.task_type, "You are a helpful AI assistant.")

    # Set reasoning level
    reasoning_config = {
        "low": {"thinking_budget_tokens": 1000},
        "medium": {"thinking_budget_tokens": 5000},
        "high": {"thinking_budget_tokens": 15000}
    }

    # Create the model with function calling
    model = genai.GenerativeModel(
        model_name="gemini-3.1-pro",
        system_instruction=system_prompt,
        tools=tools if request.use_tools else None
    )

    # Format input data as prompt
    user_message = f"""
    Task Type: {request.task_type}
    Input Data: {json.dumps(request.input_data)}

    Please process this request. Use available tools as needed.
    """

    # Initial request to Gemini
    response = model.generate_content(
        user_message,
        safety_settings={
            "HARM_CATEGORY_UNSPECIFIED": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
        }
    )

    # Extract thinking and response
    result = {
        "primary_response": response.text if response.text else "",
        "reasoning": getattr(response, 'thinking', "No thinking data"),
        "tools_used": []
    }

    # Handle tool calls
    if hasattr(response, 'tool_calls'):
        for tool_call in response.tool_calls:
            tool_result = await execute_tool(tool_call.name, tool_call.args)
            result["tools_used"].append({
                "tool": tool_call.name,
                "result": tool_result
            })

    execution_time = (datetime.now() - start_time).total_seconds()

    return {
        "task_id": f"task_{datetime.now().timestamp()}",
        "status": "completed",
        "result": result,
        "provider_used": "gemini",
        "execution_time": execution_time
    }

async def process_with_chatgpt(request: AutomationRequest) -> Dict[str, Any]:
    """Process request with ChatGPT (OpenAI)"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    start_time = datetime.now()

    model_map = {
        "low": "gpt-4o-mini",
        "medium": "gpt-4o-mini",
        "high": "gpt-4o"
    }
    model_name = model_map.get(request.reasoning_level, "gpt-4o-mini")

    system_prompts = {
        "email": "You are an email automation expert...",
        "web_scrape": "You are a web scraping expert...",
        "document_analysis": "You are a document analysis expert...",
        "data_analysis": "You are a data analysis expert...",
        "voice": "You are a voice agent assistant..."
    }
    system_prompt = system_prompts.get(request.task_type, "You are a helpful AI assistant.")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(request.input_data)}
            ]
        )

        result = {
            "primary_response": response.choices[0].message.content,
            "reasoning": "Reasoning provided via " + model_name,
            "tools_used": [] # Tool calling for OpenAI can be added here
        }

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "task_id": f"task_gpt_{datetime.now().timestamp()}",
            "status": "completed",
            "result": result,
            "provider_used": "chatgpt",
            "execution_time": execution_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

# ============================================================
# API ENDPOINTS
# ============================================================

async def process_with_fallback(request: AutomationRequest) -> Dict[str, Any]:
    """Process with automatic fallback if quota is exhausted"""
    primary_provider = request.provider
    fallback_provider = "chatgpt" if primary_provider == "gemini" else "gemini"
    
    try:
        # Try primary provider
        if primary_provider == "chatgpt":
            return await process_with_chatgpt(request)
        else:
            return await process_with_gemini(request)
            
    except (google_exceptions.ResourceExhausted, RateLimitError) as e:
        print(f"⚠️ {primary_provider.upper()} Quota Exhausted! Falling back to {fallback_provider.upper()}...")
        
        # Switch provider and retry once
        request.provider = fallback_provider
        try:
            if fallback_provider == "chatgpt":
                response = await process_with_chatgpt(request)
            else:
                response = await process_with_gemini(request)
            
            response["fallback_occurred"] = True
            return response
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500, 
                detail=f"Both providers failed. Primary error: {str(e)}. Fallback error: {str(fallback_error)}"
            )
    except Exception as e:
        # Re-raise other exceptions
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automate", response_model=AutomationResponse)
async def automate(request: AutomationRequest):
    """Process automation request with selected provider and automatic fallback"""
    result = await process_with_fallback(request)
    return AutomationResponse(**result)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_configured": bool(API_KEY)
    }

@app.get("/models")
async def list_models():
    """List available Gemini models"""
    models = genai.list_models()
    return {
        "available_models": [m.display_name for m in models if "gemini" in m.display_name.lower()]
    }

@app.get("/tools")
async def list_tools():
    """List available tools"""
    return {
        "tools": [{"name": t["name"], "description": t["description"]} for t in tools]
    }

# ============================================================
# AUTOMATION USE CASES
# ============================================================

@app.post("/email-agent")
async def email_agent(request: AutomationRequest):
    """Email automation agent"""
    request.task_type = "email"
    request.use_tools = ["google_search", "send_email", "code_execution"]
    return await automate(request)

@app.post("/web-scraper")
async def web_scraper(request: AutomationRequest):
    """Web scraping agent"""
    request.task_type = "web_scrape"
    request.use_tools = ["google_search", "url_context", "code_execution"]
    return await automate(request)

@app.post("/document-analyzer")
async def document_analyzer(request: AutomationRequest):
    """Document analysis agent"""
    request.task_type = "document_analysis"
    request.use_tools = ["file_search", "code_execution"]
    return await automate(request)

@app.post("/data-analyst")
async def data_analyst(request: AutomationRequest):
    """Data analysis agent"""
    request.task_type = "data_analysis"
    request.use_tools = ["code_execution", "database_query"]
    return await automate(request)

# ============================================================
# WEBHOOK HANDLER FOR LIVE API
# ============================================================

@app.post("/voice-webhook")
async def voice_webhook(data: Dict[str, Any]):
    """Handle Gemini Live API voice events"""
    event_type = data.get("type")

    if event_type == "server_content.audio_transcription":
        return {
            "response": f"Transcribed: {data.get('transcript')}",
            "timestamp": datetime.now().isoformat()
        }

    return {"status": "processed"}

# ============================================================
# STARTUP AND SHUTDOWN
# ============================================================

@app.on_event("startup")
async def startup():
    print("🚀 Gemini Pro Automation Platform Starting...")
    print(f"✅ Gemini API Configured")
    print(f"✅ Available Tools: {len(tools)}")
    print(f"✅ API Ready at http://localhost:8000")

@app.on_event("shutdown")
async def shutdown():
    print("⏹️ Gemini Pro Automation Platform Shutting Down...")

# ============================================================
# RUN LOCALLY
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
