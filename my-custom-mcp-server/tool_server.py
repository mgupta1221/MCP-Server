"""
FastAPI Server to expose issue tracker tools
Acts as middleware between the agent and the actual backend API

UPDATED FOR: mcp-issue-tracker backend running on localhost:3000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx
import os

app = FastAPI(title="Issue Tracker Tool Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


# Get backend base URL from environment or use default
BACKEND_BASE_URL = os.getenv("ISSUES_API_BASE_URL", "http://localhost:3000/api")
print(f"Backend Base URL: {BACKEND_BASE_URL}")


# Tool registry with ACTUAL backend endpoints
# IMPORTANT: These URLs point to your mcp-issue-tracker backend
TOOL_REGISTRY = {
    "issues-server:issues-list": {
        "method": "GET",
        "url": f"{BACKEND_BASE_URL}/issues"  # http://localhost:3000/api/issues
    },
    "issues-server:issues-create": {
        "method": "POST",
        "url": f"{BACKEND_BASE_URL}/issues"  # http://localhost:3000/api/issues
    },
    "issues-server:issues-get": {
        "method": "GET",
        "url": f"{BACKEND_BASE_URL}/issues/{{id}}"  # http://localhost:3000/api/issues/{id}
    },
    "issues-server:issues-update": {
        "method": "PUT",
        "url": f"{BACKEND_BASE_URL}/issues/{{id}}"  # http://localhost:3000/api/issues/{id}
    },
    "issues-server:issues-delete": {
        "method": "DELETE",
        "url": f"{BACKEND_BASE_URL}/issues/{{id}}"  # http://localhost:3000/api/issues/{id}
    },
    "issues-server:tags-list": {
        "method": "GET",
        "url": f"{BACKEND_BASE_URL}/tags"  # http://localhost:3000/api/tags
    },
    "issues-server:tags-create": {
        "method": "POST",
        "url": f"{BACKEND_BASE_URL}/tags"  # http://localhost:3000/api/tags
    },
    "issues-server:tags-delete": {
        "method": "DELETE",
        "url": f"{BACKEND_BASE_URL}/tags/{{id}}"  # http://localhost:3000/api/tags/{id}
    },
    "issues-server:users-list": {
        "method": "GET",
        "url": f"{BACKEND_BASE_URL}/users"  # http://localhost:3000/api/users
    },
    "issues-server:api-key-verify": {
        "method": "POST",
        "url": f"{BACKEND_BASE_URL}/verify"  # http://localhost:3000/api/verify
    }
}


@app.post("/tool/call")
async def call_tool(request: ToolCallRequest) -> Dict[str, Any]:
    """
    Execute a tool by forwarding to the actual backend API
    
    Flow:
    1. Agent calls: http://localhost:8000/tool/call
    2. This function forwards to: http://localhost:3000/api/{endpoint}
    3. Backend processes and returns data
    4. This function returns data to agent
    """
    tool_name = request.tool_name
    
    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    tool_config = TOOL_REGISTRY[tool_name]
    method = tool_config["method"]
    url_template = tool_config["url"]
    
    print(f"\n{'='*60}")
    print(f"Tool Call: {tool_name}")
    print(f"Method: {method}")
    print(f"URL Template: {url_template}")
    
    # Extract path parameters (e.g., {id})
    url = url_template
    path_params = {}
    if "{id}" in url_template:
        if "id" in request.arguments:
            path_params["id"] = request.arguments["id"]
            url = url_template.format(**path_params)
            # Remove id from arguments as it's now in the URL
            args = {k: v for k, v in request.arguments.items() if k != "id"}
        else:
            raise HTTPException(status_code=400, detail="Missing required parameter: id")
    else:
        args = request.arguments
    
    print(f"Final URL: {url}")
    print(f"Arguments: {args}")
    
    # Prepare request
    headers = {}
    api_key = args.pop("apiKey", None)
    if api_key:
        headers["x-api-key"] = api_key
        print(f"Using API Key: {api_key[:20]}...")
    
    # Make the API call to your actual backend
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                print(f"Making GET request to {url}")
                response = await client.get(url, params=args, headers=headers)
            elif method == "POST":
                print(f"Making POST request to {url}")
                response = await client.post(url, json=args, headers=headers)
            elif method == "PUT":
                print(f"Making PUT request to {url}")
                response = await client.put(url, json=args, headers=headers)
            elif method == "DELETE":
                print(f"Making DELETE request to {url}")
                response = await client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=500, detail=f"Unsupported method: {method}")
            
            print(f"Response Status: {response.status_code}")
            print(f"{'='*60}\n")
            
            # Return the response
            return response.json()
        
        except httpx.ConnectError as e:
            print(f"ERROR: Cannot connect to backend at {url}")
            print(f"ERROR: {str(e)}")
            print(f"{'='*60}\n")
            raise HTTPException(
                status_code=503, 
                detail=f"Cannot connect to backend at {url}. Is the backend running?"
            )
        except httpx.TimeoutException as e:
            print(f"ERROR: Request timeout")
            print(f"{'='*60}\n")
            raise HTTPException(status_code=504, detail="Backend request timeout")
        except httpx.HTTPError as e:
            print(f"ERROR: HTTP error: {str(e)}")
            print(f"{'='*60}\n")
            raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Also check if backend is reachable
    backend_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_BASE_URL.replace('/api', '')}/health")
            if response.status_code == 200:
                backend_status = "healthy"
            else:
                backend_status = f"unhealthy (status: {response.status_code})"
    except Exception as e:
        backend_status = f"unreachable ({str(e)})"
    
    return {
        "status": "healthy",
        "service": "issue-tracker-tool-server",
        "backend_url": BACKEND_BASE_URL,
        "backend_status": backend_status
    }


@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools_list = []
    for tool_name, config in TOOL_REGISTRY.items():
        tools_list.append({
            "name": tool_name,
            "method": config["method"],
            "url": config["url"]
        })
    
    return {
        "backend_url": BACKEND_BASE_URL,
        "tools": tools_list,
        "count": len(tools_list)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Issue Tracker Tool Server Starting...")
    print("="*60)
    print(f"\n📍 Tool Server: http://localhost:8000")
    print(f"📍 Backend API: {BACKEND_BASE_URL}")
    print(f"\n💡 This server forwards requests from agent to backend")
    print(f"\n🔧 Available tools:")
    for tool_name in TOOL_REGISTRY.keys():
        print(f"   - {tool_name}")
    print(f"\n✅ Health check: http://localhost:8000/health")
    print(f"✅ List tools: http://localhost:8000/tools")
    print(f"\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)