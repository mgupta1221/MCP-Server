# Issue Tracker AI Agent (Azure OpenAI Version)

A production-level AI agent using **Azure OpenAI (GPT-4)** to orchestrate issue tracker operations through natural language.


This version uses **Azure OpenAI (GPT-4)** instead of Anthropic Claude:


## 📋 Prerequisites


## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```


You: Create a bug for the payment timeout
You: List all high priority issues
You: Update issue 5 to mark as in progress
```

### Single Command Mode

```bash
python cli.py "Create urgent bug for database crash"
```
### ✅ Complete Orchestration
```python
Agent handles:
1. Find user "John" → users-list
2. Find "bug" tag → tags-list
3. Create issue → issues-create
All in one request!
```
=================================================================

## 🌐 Deployment

### Azure App Service

```bash
# 1. Create App Service
az webapp create --name my-issue-agent --resource-group myResourceGroup

# 2. Configure environment variables
az webapp config appsettings set --name my-issue-agent \
  --settings AZURE_OPENAI_ENDPOINT="..." \
             AZURE_OPENAI_API_KEY="..." \
             AZURE_OPENAI_DEPLOYMENT="gpt-4"

# 3. Deploy
az webapp up --name my-issue-agent
```

### Azure Container Apps

```bash
# Build container
docker build -t issue-agent-azure .

# Push to Azure Container Registry
az acr build --registry myregistry --image issue-agent-azure .

# Deploy to Container Apps
az containerapp create --name issue-agent \
  --resource-group myResourceGroup \
  --environment myEnvironment \
  --image myregistry.azurecr.io/issue-agent-azure:latest
```

## 📈 Monitoring

### Azure Application Insights

Add to your agent:

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-key'
))
```
