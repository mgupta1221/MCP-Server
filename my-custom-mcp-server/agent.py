"""
Production-Level AI Agent for Issue Tracker
Uses Azure OpenAI (GPT-4) for orchestration
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from openai import AzureOpenAI
import httpx
from pydantic import BaseModel, Field
from enum import Enum


class IssueType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    DOCUMENTATION = "documentation"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class UserImpact(str, Enum):
    BLOCKING = "blocking"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"


class AffectedArea(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    API = "api"
    AUTHENTICATION = "authentication"


# ===== Intent Models =====

class CreateIssueIntent(BaseModel):
    """Intent to create a new issue"""
    action: str = "create_issue"
    title: str
    issue_type: IssueType
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    priority: Optional[Priority] = Priority.MEDIUM
    status: Optional[Status] = Status.NOT_STARTED


class UpdateIssueIntent(BaseModel):
    """Intent to update an existing issue"""
    action: str = "update_issue"
    issue_id: int
    new_assignee_name: Optional[str] = None
    new_priority: Optional[Priority] = None
    new_status: Optional[Status] = None
    add_comment: Optional[str] = None


class SearchIssuesIntent(BaseModel):
    """Intent to search/filter issues"""
    action: str = "search_issues"
    query: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    issue_type: Optional[IssueType] = None


class TriageBugIntent(BaseModel):
    """Intent to smart-triage a bug"""
    action: str = "triage_bug"
    title: str
    description: str
    affected_area: AffectedArea
    user_impact: UserImpact


class ListTeamMembersIntent(BaseModel):
    """Intent to list team members"""
    action: str = "list_team_members"
    team: Optional[str] = "all"


# ===== Main Agent Class =====

class IssueTrackerAgent:
    """
    Production AI Agent using Azure OpenAI (GPT-4)
    """
    
    def __init__(
        self, 
        azure_endpoint: str,
        azure_api_key: str,
        azure_deployment_name: str,
        issues_api_key: str,
        issues_api_base_url: str = "http://localhost:3000"
    ):
        self.client = AzureOpenAI(
            api_key=azure_api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=azure_endpoint
        )
        self.deployment_name = azure_deployment_name
        self.issues_api_key = issues_api_key
        self.api_base_url = issues_api_base_url.rstrip('/')
        
        # Cache for users and tags to reduce API calls
        self._users_cache: Optional[List[Dict]] = None
        self._tags_cache: Optional[List[Dict]] = None
        
    async def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input into structured intent using Azure OpenAI GPT-4
        """
        system_prompt = """
You are an intent parser for an issue tracking system.
Extract structured information from user requests.

Analyze the input and determine which action the user wants:
1. create_issue - Creating a new issue (bug, feature, task)
2. update_issue - Updating an existing issue
3. search_issues - Searching or listing issues
4. triage_bug - Smart triage for critical bugs
5. list_team_members - List available team members

Return ONLY valid JSON matching one of these structures:

For create_issue:
{
  "action": "create_issue",
  "title": "extracted title",
  "issue_type": "bug" | "feature" | "task" | "documentation",
  "description": "details if provided",
  "assignee_name": "name if mentioned",
  "priority": "low" | "medium" | "high" | "urgent",
  "status": "not_started" | "in_progress" | "done"
}

For update_issue:
{
  "action": "update_issue",
  "issue_id": number,
  "new_assignee_name": "name if changing assignee",
  "new_priority": "low" | "medium" | "high" | "urgent",
  "new_status": "not_started" | "in_progress" | "done",
  "add_comment": "comment text if adding note"
}

For search_issues:
{
  "action": "search_issues",
  "query": "search text",
  "assigned_to": "person name",
  "status": "not_started" | "in_progress" | "done",
  "priority": "low" | "medium" | "high" | "urgent",
  "issue_type": "bug" | "feature" | "task"
}

For triage_bug:
{
  "action": "triage_bug",
  "title": "bug title",
  "description": "bug description",
  "affected_area": "frontend" | "backend" | "database" | "api" | "authentication",
  "user_impact": "blocking" | "major" | "minor" | "cosmetic"
}

For list_team_members:
{
  "action": "list_team_members",
  "team": "all" | "frontend" | "backend" | "devops"
}

Only include fields that are present or can be reasonably inferred.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this request: {user_input}"}
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Extract JSON from response
            json_text = response.choices[0].message.content.strip()
            
            intent = json.loads(json_text)
            return intent
            
        except Exception as e:
            raise ValueError(f"Failed to parse intent: {str(e)}")
    
    async def get_users(self, force_refresh: bool = False) -> List[Dict]:
        """Get all users with caching"""
        if self._users_cache and not force_refresh:
            return self._users_cache
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:users-list",
                    "arguments": {"apiKey": self.issues_api_key}
                }
            )
            result = response.json()
            self._users_cache = result.get("data", [])
            return self._users_cache
    
    async def get_tags(self, force_refresh: bool = False) -> List[Dict]:
        """Get all tags with caching"""
        if self._tags_cache and not force_refresh:
            return self._tags_cache
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:tags-list",
                    "arguments": {"apiKey": self.issues_api_key}
                }
            )
            result = response.json()
            self._tags_cache = result.get("data", [])
            return self._tags_cache
    
    async def find_user_by_name(self, name: str) -> Optional[Dict]:
        """Find user by name with fuzzy matching"""
        users = await self.get_users()
        name_lower = name.lower()
        
        # Exact match first
        for user in users:
            if user["name"].lower() == name_lower:
                return user
        
        # Partial match
        for user in users:
            if name_lower in user["name"].lower():
                return user
        
        # Check email
        for user in users:
            if name_lower in user["email"].lower():
                return user
        
        return None
    
    async def find_or_create_tag(self, tag_name: str) -> Dict:
        """Find existing tag or create new one"""
        tags = await self.get_tags()
        
        # Look for existing tag
        for tag in tags:
            if tag["name"].lower() == tag_name.lower():
                return tag
        
        # Create new tag
        color_map = {
            "bug": "#ef4444",
            "feature": "#8b5cf6",
            "task": "#3b82f6",
            "documentation": "#6b7280",
            "enhancement": "#f59e0b",
            "urgent": "#dc2626",
            "frontend": "#06b6d4",
            "backend": "#10b981",
            "database": "#f59e0b",
            "api": "#8b5cf6",
            "authentication": "#ec4899"
        }
        
        color = color_map.get(tag_name.lower(), "#6b7280")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:tags-create",
                    "arguments": {
                        "apiKey": self.issues_api_key,
                        "name": tag_name,
                        "color": color
                    }
                }
            )
            result = response.json()
            new_tag = result.get("data", {})
            
            # Refresh cache
            await self.get_tags(force_refresh=True)
            return new_tag
    
    # ===== Action Handlers =====
    
    async def handle_create_issue(self, intent: CreateIssueIntent) -> Dict:
        """Handle create issue action"""
        print(f"🔧 Creating {intent.issue_type.value}: {intent.title}")
        
        # Find assignee if specified
        assigned_user_id = None
        if intent.assignee_name:
            user = await self.find_user_by_name(intent.assignee_name)
            if not user:
                users = await self.get_users()
                available = ", ".join([u["name"] for u in users[:5]])
                return {
                    "success": False,
                    "error": f"User '{intent.assignee_name}' not found. Available users: {available}"
                }
            assigned_user_id = user["id"]
            print(f"  ✓ Assigned to: {user['name']} ({user['email']})")
        
        # Find or create tag for issue type
        tag = await self.find_or_create_tag(intent.issue_type.value)
        print(f"  ✓ Tagged as: {tag['name']}")
        
        # Create the issue
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:issues-create",
                    "arguments": {
                        "apiKey": self.issues_api_key,
                        "title": intent.title,
                        "description": intent.description,
                        "assigned_user_id": assigned_user_id,
                        "priority": intent.priority.value,
                        "status": intent.status.value,
                        "tag_ids": [tag["id"]]
                    }
                }
            )
            result = response.json()
        
        if result.get("success"):
            issue = result["data"]
            print(f"  ✅ Created issue #{issue['id']}")
            return {
                "success": True,
                "issue": issue,
                "message": f"Created {intent.issue_type.value} #{issue['id']}: {intent.title}"
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Failed to create issue")
            }
    
    async def handle_update_issue(self, intent: UpdateIssueIntent) -> Dict:
        """Handle update issue action"""
        print(f"🔧 Updating issue #{intent.issue_id}")
        
        # Build update payload
        update_data = {
            "apiKey": self.issues_api_key,
            "id": intent.issue_id
        }
        
        # Find new assignee if specified
        if intent.new_assignee_name:
            user = await self.find_user_by_name(intent.new_assignee_name)
            if not user:
                return {
                    "success": False,
                    "error": f"User '{intent.new_assignee_name}' not found"
                }
            update_data["assigned_user_id"] = user["id"]
            print(f"  ✓ Reassigning to: {user['name']}")
        
        if intent.new_priority:
            update_data["priority"] = intent.new_priority.value
            print(f"  ✓ Priority: {intent.new_priority.value}")
        
        if intent.new_status:
            update_data["status"] = intent.new_status.value
            print(f"  ✓ Status: {intent.new_status.value}")
        
        # Update the issue
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:issues-update",
                    "arguments": update_data
                }
            )
            result = response.json()
        
        if result.get("success"):
            print(f"  ✅ Updated issue #{intent.issue_id}")
            return {
                "success": True,
                "issue": result["data"],
                "message": f"Updated issue #{intent.issue_id}"
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Failed to update issue")
            }
    
    async def handle_search_issues(self, intent: SearchIssuesIntent) -> Dict:
        """Handle search issues action"""
        print(f"🔍 Searching issues...")
        
        # Build search parameters
        search_params = {"apiKey": self.issues_api_key}
        print(intent)
        if intent.query:
            search_params["search"] = intent.query
            print(f"  Query: {intent.query}")
        
        if intent.assigned_to:
            user = await self.find_user_by_name(intent.assigned_to)
            if user:
                search_params["assigned_user_id"] = user["id"]
                print(f"  Assigned to: {user['name']}")
        
        if intent.status:
            search_params["status"] = intent.status.value
            print(f"  Status: {intent.status.value}")
        
        if intent.priority:
            search_params["priority"] = intent.priority.value
            print(f"  Priority: {intent.priority.value}")
        
        # Search issues
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:issues-list",
                    "arguments": search_params
                }
            )
            result = response.json()
        
        if result.get("success"):
            issues = result["data"]
            print(f"  ✅ Found {len(issues)} issues")
            return {
                "success": True,
                "issues": issues,
                "count": len(issues)
            }
        else:
            return {
                "success": False,
                "error": "Failed to search issues"
            }
    
    async def handle_triage_bug(self, intent: TriageBugIntent) -> Dict:
        """Handle smart bug triage"""
        print(f"🚨 Triaging bug: {intent.title}")
        
        # Determine priority based on user impact
        priority_map = {
            UserImpact.BLOCKING: Priority.URGENT,
            UserImpact.MAJOR: Priority.HIGH,
            UserImpact.MINOR: Priority.MEDIUM,
            UserImpact.COSMETIC: Priority.LOW
        }
        priority = priority_map[intent.user_impact]
        print(f"  ✓ Priority: {priority.value} (impact: {intent.user_impact.value})")
        
        # Determine initial status
        status = Status.IN_PROGRESS if intent.user_impact == UserImpact.BLOCKING else Status.NOT_STARTED
        print(f"  ✓ Status: {status.value}")
        
        # Find best assignee based on affected area
        users = await self.get_users()
        assignee = users[0] if users else None
        assigned_user_id = assignee["id"] if assignee else None
        
        if assignee:
            print(f"  ✓ Auto-assigned to: {assignee['name']}")
        
        # Create tags
        bug_tag = await self.find_or_create_tag("bug")
        area_tag = await self.find_or_create_tag(intent.affected_area.value)
        tag_ids = [bug_tag["id"], area_tag["id"]]
        
        if intent.user_impact == UserImpact.BLOCKING:
            urgent_tag = await self.find_or_create_tag("urgent")
            tag_ids.append(urgent_tag["id"])
        
        print(f"  ✓ Tags: {', '.join([bug_tag['name'], area_tag['name']])}")
        
        # Create the issue
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/tool/call",
                json={
                    "tool_name": "issues-server:issues-create",
                    "arguments": {
                        "apiKey": self.issues_api_key,
                        "title": intent.title,
                        "description": f"{intent.description}\n\nAffected Area: {intent.affected_area.value}\nUser Impact: {intent.user_impact.value}",
                        "assigned_user_id": assigned_user_id,
                        "priority": priority.value,
                        "status": status.value,
                        "tag_ids": tag_ids
                    }
                }
            )
            result = response.json()
        
        if result.get("success"):
            issue = result["data"]
            print(f"  ✅ Triaged as issue #{issue['id']}")
            
            return {
                "success": True,
                "issue": issue,
                "message": f"Bug triaged as {priority.value} priority issue #{issue['id']}",
                "triage_info": {
                    "priority": priority.value,
                    "assigned_to": assignee["name"] if assignee else None,
                    "tags": [bug_tag["name"], area_tag["name"]],
                    "status": status.value
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to triage bug"
            }
    
    async def handle_list_team_members(self, intent: ListTeamMembersIntent) -> Dict:
        """Handle list team members action"""
        print(f"👥 Listing team members (team: {intent.team})")
        
        users = await self.get_users()
        
        print(f"  ✅ Found {len(users)} team members")
        return {
            "success": True,
            "users": users,
            "count": len(users)
        }
    
    # ===== Main Handler =====
    
    async def handle_request(self, user_input: str) -> Dict:
        """
        Main entry point - parse intent and execute action
        """
        print(f"\n{'='*60}")
        print(f"📝 User Input: {user_input}")
        print(f"{'='*60}\n")
        
        try:
            # Parse intent
            intent_data = await self.parse_intent(user_input)
            print(f"🧠 Parsed Intent: {intent_data.get('action')}")
            
            # Route to appropriate handler
            action = intent_data.get("action")
            
            if action == "create_issue":
                intent = CreateIssueIntent(**intent_data)
                return await self.handle_create_issue(intent)
            
            elif action == "update_issue":
                intent = UpdateIssueIntent(**intent_data)
                return await self.handle_update_issue(intent)
            
            elif action == "search_issues":
                intent = SearchIssuesIntent(**intent_data)
                return await self.handle_search_issues(intent)
            
            elif action == "triage_bug":
                intent = TriageBugIntent(**intent_data)
                return await self.handle_triage_bug(intent)
            
            elif action == "list_team_members":
                intent = ListTeamMembersIntent(**intent_data)
                return await self.handle_list_team_members(intent)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
