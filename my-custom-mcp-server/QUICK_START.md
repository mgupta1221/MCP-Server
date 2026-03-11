# Quick Start Guide - Your Specific Setup

## ✅ What You Already Have

1. **Backend running**: `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\mcp-issue-tracker\backend`
   - Running on: `http://localhost:3000`
   - Started with: `npm run dev`
   - API at: `http://localhost:3000/api`

2. **Frontend** (optional): Running on `http://localhost:5173`
   - Just for web UI - not needed for agent!


---

## 🚀 Steps to Run (FINAL VERSION)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create .env File

Create a file named `.env` with this content:

```bash
# Azure OpenAI (get from Azure Portal)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-32-char-key
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Backend (already running!)
ISSUES_API_BASE_URL=http://localhost:3000/api 
#(currently, this url is mcp-issue-tracker's backend project working as API layer connected to DB for this project)

ISSUES_API_KEY=issues_dsoVueKdajVuiNQagdPYABsaldceseDlJfyNGKPPbPQBSehpPzGZSQRZivEUZLPL
```
(ISSUES_API_KEY can be taken from mcp-issue-tracker project's frontend, by
cliking API_Key button)

**IMPORTANT:** Use `http://localhost:3000/api` (backend port), NOT `5173` (frontend port)!

### Step 3: Run the Agent

Open **2 new terminals** (backend already running in terminal 1):

**Terminal 2: Tool Server**
```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\my-custom-mcp-server"
python tool_server.py
```

**Terminal 3: AI Agent**
```bash
cd "C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\my-custom-mcp-server"
python cli.py
```

### Step 4: Test

```bash
You: List team members
You: Create a bug for testing
You: Show all issues
```

---

## 🎯 Terminal Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Terminal 1: Backend (ALREADY RUNNING)                       │
│ Location: mcp-issue-tracker\backend                         │
│ Command:  npm run dev                                       │
│ Port:     3000                                              │
│ Status:   ✅ Keep running                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Terminal 2: Tool Server (NEW)                               │
│ Location: my-custom-mcp-server                                 │
│ Command:  python tool_server.py                            │
│ Port:     8000                                              │
│ Status:   Start this now                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Terminal 3: AI Agent (NEW)                                  │
│ Location: my-custom-mcp-server                                 │
│ Command:  python cli.py                                     │
│ Status:   Start this after Terminal 2                       │
└─────────────────────────────────────────────────────────────┘
```



## 📁 File Checklist

In `C:\Users\mohgupt\OneDrive - Adobe\Desktop\AI\MCP Server\my-custom-mcp-server\`:

- ✅ `agent.py` - Main agent (Azure OpenAI)
- ✅ `cli.py` - Command line interface
- ✅ `tool_server.py` - Tool execution server
- ✅ `examples.py` - Usage examples
- ✅ `requirements.txt` - Dependencies
- ✅ `.env` - Your configuration (CREATE THIS!)
- ✅ `README.md` - Full documentation

---

## 🎯 Summary

### What's Running Where:

| Service | Port | Location |
|---------|------|----------|
| **Backend** (mcp-issue-tracker) | 3000 | Already running ✅ |
| **Frontend** (optional) | 5173 | Optional - for web UI |
| **Tool Server** | 8000 | Start with `python tool_server.py` |
| **AI Agent** | - | Start with `python cli.py` |


### What Happens:
```
You type → AI Agent (GPT-4) → Tool Server → Backend API → Database
   ↑                                                          ↓
   └──────────────────── Response ←─────────────────────────┘
```

---

## 🎉 You're Ready!

Just run:
1.  Run mcp-issue-tracker's backend by running "npm run dev" in that directory(Terminal 1)
2. `python tool_server.py` (Terminal 2)
3. `python cli.py` (Terminal 3)
4. Type: "List team members"

That's it! 🚀
