# Complete Setup Guide - Using Actual mcp-issue-tracker Backend

## ✅ What You Have

- ✅ Backend running at: `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend`
- ✅ Backend running on: `http://localhost:3000` (via `npm run dev`)
- ✅ Frontend running on: `http://localhost:5173` (optional, for UI)
- ✅ API endpoints at: `http://localhost:3000/api/...`

## ❌ What You DON'T Need

- ❌ **mock_backend.py** - You have the real backend!
- ❌ **Anthropic API credits** - You'll use Azure OpenAI instead

---

## 🚀 Complete Setup Steps

### Step 1: Verify Backend is Running

```bash
# Open Command Prompt or PowerShell
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend"

# Start backend (if not already running)
npm run dev

# You should see:
# Server running on http://localhost:3000
```

**Test the backend:**

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test API endpoint
curl http://localhost:3000/api/users

# If curl doesn't work, open in browser:
# http://localhost:3000/health
```

### Step 2: Find Your Backend API Key

The mcp-issue-tracker backend likely uses one of these auth methods:

#### Method A: Check if API key is in backend .env

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend"
type .env
```

Look for:
- `API_KEY=...`
- `MASTER_API_KEY=...`
- Or any key that looks like `issues_...`

#### Method B: Try the key from our conversation

```bash
# This key was mentioned earlier:
issues_dsoVueKdajVuiNQagdPYABsaldceseDlJfyNGKPPbPQBSehpPzGZSQRZivEUZLPL
```

#### Method C: Check backend source code

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend"

# Search for API key handling
findstr /s /i "apikey" src\*.ts
findstr /s /i "authorization" src\*.ts
```

#### Method D: Create a test user

```bash
# Sign up via API
curl -X POST http://localhost:3000/api/auth/sign-up/email ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\",\"name\":\"Test User\"}"

# Sign in to get token
curl -X POST http://localhost:3000/api/auth/sign-in/email ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"

# The response will contain a session token
```

### Step 3: Create Project Directory for Agent

```bash
# Create a new directory for your agent
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server"
mkdir issue-agent-azure
cd issue-agent-azure
```

### Step 4: Copy Agent Files

Copy these files to `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure\`:

- ✅ `agent.py`
- ✅ `cli.py`
- ✅ `tool_server.py`
- ✅ `examples.py`
- ✅ `requirements.txt`
- ✅ `.env.example`
- ✅ `README.md`

**DO NOT copy:**
- ❌ `mock_backend.py` - Not needed!

### Step 5: Install Python Dependencies

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure"

# Install dependencies
pip install -r requirements.txt

# You should see installations for:
# - openai (Azure OpenAI SDK)
# - httpx
# - fastapi
# - uvicorn
# - pydantic
```

### Step 6: Configure Environment Variables

Create `.env` file:

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure"

# Create .env file (use notepad or your favorite editor)
notepad .env
```

Add this content to `.env`:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Issues Backend Configuration
# IMPORTANT: Backend is on port 3000, NOT 5173!
# Port 5173 is for the React frontend (optional)
ISSUES_API_BASE_URL=http://localhost:3000/api
ISSUES_API_KEY=issues_dsoVueKdajVuiNQagdPYABsaldceseDlJfyNGKPPbPQBSehpPzGZSQRZivEUZLPL
```

**Important Notes:**
- ✅ Backend API is at: `http://localhost:3000/api` (port **3000**)
- ❌ NOT `http://localhost:5173/api` (that's the frontend)
- Frontend (port 5173) is just for the web UI - you don't need it for the agent

### Step 7: Get Azure OpenAI Credentials

#### A. Create Azure OpenAI Resource

1. Go to **Azure Portal**: https://portal.azure.com
2. Search for **"Azure OpenAI"**
3. Click **"Create"**
4. Fill in:
   - **Resource group**: Create new or use existing
   - **Region**: **East US** (has GPT-4)
   - **Name**: `issue-tracker-openai`
   - **Pricing tier**: Standard S0
5. Click **"Review + Create"** → **"Create"**
6. Wait 2-5 minutes

#### B. Deploy GPT-4 Model

1. Go to your OpenAI resource
2. Click **"Model deployments"** → **"Manage Deployments"**
3. Opens **Azure OpenAI Studio**
4. Click **"Create new deployment"**
5. Select:
   - **Model**: `gpt-4` or `gpt-4-turbo`
   - **Deployment name**: `gpt-4` ← **Remember this!**
6. Click **"Create"**

#### C. Get Keys and Endpoint

1. Azure Portal → Your OpenAI resource
2. Click **"Keys and Endpoint"**
3. Copy:
   - **KEY 1**: (32 characters)
   - **Endpoint**: `https://your-resource.openai.azure.com/`

#### D. Update .env File

```bash
# Update your .env with real values:
AZURE_OPENAI_ENDPOINT=https://your-actual-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=paste-your-32-char-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### Step 8: Test Backend Connection

Before running the agent, let's verify the backend works:

```bash
# Test 1: Health check
curl http://localhost:3000/health

# Test 2: List users (with API key)
curl -X GET http://localhost:3000/api/users ^
  -H "Authorization: Bearer issues_dsoVueKdajVuiNQagdPYABsaldceseDlJfyNGKPPbPQBSehpPzGZSQRZivEUZLPL"

# If this works, you'll see a list of users! ✅
```

If you get errors:
- **401 Unauthorized**: API key is wrong, try Method D above
- **Connection refused**: Backend not running, go back to Step 1
- **404 Not found**: Wrong URL, make sure it's `/api/users`

---

## 🎯 Running the Agent

### Terminal Setup

You'll need **3 terminal windows**:

#### Terminal 1: Backend (Already Running)

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend"
npm run dev

# Keep this running!
# Output: Server running on http://localhost:3000
```

#### Terminal 2: Tool Server

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure"
python tool_server.py

# Output:
# INFO: Uvicorn running on http://0.0.0.0:8000
# Keep this running!
```

#### Terminal 3: AI Agent

```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure"
python cli.py

# You should see:
# ╔══════════════════════════════════════════════════════════╗
# ║   Issue Tracker AI Agent - Azure OpenAI (GPT-4)         ║
# ╚══════════════════════════════════════════════════════════╝

# Now you can type commands:
You: List team members
You: Create a bug for login issue
You: Show all issues
```

---

## 🧪 Testing Commands

Try these commands in the agent CLI:

```bash
# 1. List team members
You: List team members

# Expected output:
# 👥 Found X team members:
#   • John Doe (john@example.com)
#   • Jane Smith (jane@example.com)
#   ...

# 2. Create a simple bug
You: Create a bug for testing the agent

# Expected output:
# ✅ SUCCESS
# Created bug #1: testing the agent

# 3. Create assigned bug
You: Create a bug for login issue and assign to John

# Expected output:
# ✅ Created bug #2: login issue
# Assigned to: John Doe

# 4. Search issues
You: Show me all bugs

# Expected output:
# 📋 Found 2 issues:
#   🔄 🟡 #1: testing the agent
#   🔄 🟡 #2: login issue

# 5. Update issue
You: Mark issue 1 as done

# Expected output:
# ✅ Updated issue #1
```

---

## 📁 Final Project Structure

```
C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\
│
├── mcp-issue-tracker\          (Original project)
│   ├── backend\                ← Terminal 1: npm run dev
│   │   └── (running on port 3000)
│   └── frontend\               ← Optional (port 5173)
│
└── issue-agent-azure\          (Your AI agent)
    ├── agent.py                ← Main agent (uses Azure OpenAI)
    ├── cli.py                  ← Terminal 3: python cli.py
    ├── tool_server.py          ← Terminal 2: python tool_server.py
    ├── examples.py             
    ├── requirements.txt        
    ├── .env                    ← Your config (create this!)
    └── README.md               
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Cannot connect to backend"

```bash
# Check backend is running
curl http://localhost:3000/health

# If not running:
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend"
npm run dev
```

### Issue 2: "Invalid API key"

```bash
# Try without Bearer prefix
ISSUES_API_KEY=issues_dsoVueKdajVuiNQagdPYABsaldceseDlJfyNGKPPbPQBSehpPzGZSQRZivEUZLPL

# Or try signing up a new user (Method D from Step 2)
```

### Issue 3: "Azure OpenAI authentication failed"

```bash
# Verify your credentials
# 1. Check endpoint has https:// and ends with /
# 2. Check API key is exactly as shown in Azure Portal
# 3. Check deployment name matches what you created

# Test with curl:
curl https://your-resource.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-02-15-preview ^
  -H "api-key: your-key" ^
  -H "Content-Type: application/json" ^
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hi\"}]}"
```

### Issue 4: "Port 8000 already in use"

```bash
# Kill existing process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Then restart tool_server.py
```

---

## 🎉 Success Checklist

- [ ] Backend running on http://localhost:3000
- [ ] Backend health check works: `curl http://localhost:3000/health`
- [ ] Azure OpenAI resource created
- [ ] GPT-4 model deployed in Azure
- [ ] `.env` file created with correct values
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] Tool server running: `python tool_server.py`
- [ ] Agent CLI running: `python cli.py`
- [ ] Test command works: "List team members"

---

## 📝 Quick Reference

### Backend (mcp-issue-tracker)
- **Location**: `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend`
- **Command**: `npm run dev`
- **Port**: 3000
- **API Base**: `http://localhost:3000/api`

### Tool Server
- **Location**: `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure`
- **Command**: `python tool_server.py`
- **Port**: 8000

### AI Agent
- **Location**: `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\issue-agent-azure`
- **Command**: `python cli.py`
- **Uses**: Azure OpenAI GPT-4

---

## 🚀 Next Steps

Once everything is working:

1. **Try different commands** - See examples.py
2. **Integrate with your workflow** - Slack, Discord, etc.
3. **Deploy to production** - Azure App Service, Container Apps
4. **Add custom tools** - Extend agent.py for your needs

You're all set! Just follow these steps and you'll have a production AI agent running with your actual backend! 🎯
