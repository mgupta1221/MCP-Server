"""
CLI Interface for Issue Tracker Agent (Azure OpenAI version)
Allows interactive conversation with the AI agent
"""

import asyncio
import os
from dotenv import load_dotenv
from agent import IssueTrackerAgent
from typing import Optional

load_dotenv()


class AgentCLI:
    def __init__(self):
        # Get API keys from environment
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        issues_key = os.getenv("ISSUES_API_KEY")
        
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
        if not azure_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable not set")
        if not azure_deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable not set")
        if not issues_key:
            raise ValueError("ISSUES_API_KEY environment variable not set")
        
        self.agent = IssueTrackerAgent(
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_key,
            azure_deployment_name=azure_deployment,
            issues_api_key=issues_key,
            issues_api_base_url=os.getenv("ISSUES_API_BASE_URL", "http://localhost:3000")
        )
    
    def print_result(self, result: dict):
        """Pretty print the result"""
        print(f"\n{'='*60}")
        
        if result.get("success"):
            print("✅ SUCCESS")
            
            if "message" in result:
                print(f"\n{result['message']}")
            
            if "issue" in result:
                issue = result["issue"]
                print(f"\n📋 Issue Details:")
                print(f"  ID: #{issue['id']}")
                print(f"  Title: {issue['title']}")
                print(f"  Status: {issue['status']}")
                print(f"  Priority: {issue['priority']}")
                if issue.get('assigned_user_name'):
                    print(f"  Assigned: {issue['assigned_user_name']}")
                if issue.get('description'):
                    print(f"  Description: {issue['description']}")
            
            if "issues" in result:
                issues = result["issues"]
                print(f"\n📋 Found {result['count']} issues:")
                for issue in issues[:10]:  # Show first 10
                    status_emoji = {"done": "✅", "in_progress": "🔄", "not_started": "⏸️"}.get(issue['status'], "📋")
                    priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(issue['priority'], "⚪")
                    print(f"  {status_emoji} {priority_emoji} #{issue['id']}: {issue['title']}")
                    if issue.get('assigned_user_name'):
                        print(f"      → Assigned to: {issue['assigned_user_name']}")
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more")
            
            if "users" in result:
                users = result["users"]
                print(f"\n👥 Found {result['count']} team members:")
                for user in users:
                    print(f"  • {user['name']} ({user['email']})")
            
            if "triage_info" in result:
                info = result["triage_info"]
                print(f"\n🚨 Triage Information:")
                print(f"  Priority: {info['priority']}")
                print(f"  Status: {info['status']}")
                if info.get('assigned_to'):
                    print(f"  Assigned to: {info['assigned_to']}")
                print(f"  Tags: {', '.join(info['tags'])}")
        
        else:
            print("❌ ERROR")
            print(f"\n{result.get('error', 'Unknown error occurred')}")
        
        print(f"{'='*60}\n")
    
    async def run_interactive(self):
        """Run interactive CLI"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║   Issue Tracker AI Agent - Azure OpenAI (GPT-4)         ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print("\nType your requests in natural language.")
        print("Examples:")
        print("  • Create a bug for the login issue and assign to John")
        print("  • List all high priority bugs")
        print("  • Update issue 5 to mark as done")
        print("  • We have a critical auth bug affecting all users")
        print("\nType 'exit' or 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                # Process the request
                result = await self.agent.handle_request(user_input)
                
                # Display result
                self.print_result(result)
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
    
    async def run_single(self, command: str):
        """Run a single command"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║   Issue Tracker AI Agent - Azure OpenAI (GPT-4)         ║")
        print("╚══════════════════════════════════════════════════════════╝\n")
        
        result = await self.agent.handle_request(command)
        self.print_result(result)


async def main():
    """Main entry point"""
    import sys
    
    cli = AgentCLI()
    
    # Check if running with command argument
    if len(sys.argv) > 1:
        # Run single command mode
        command = " ".join(sys.argv[1:])
        await cli.run_single(command)
    else:
        # Run interactive mode
        await cli.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
