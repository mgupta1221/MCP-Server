"""
Example Usage of the Issue Tracker Agent (Azure OpenAI version)
Demonstrates various use cases
"""

import asyncio
import os
from agent import IssueTrackerAgent


async def demo_agent():
    """
    Demo script showing various agent capabilities
    """
    
    # Initialize agent with Azure OpenAI
    agent = IssueTrackerAgent(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
        issues_api_key=os.getenv("ISSUES_API_KEY"),
        issues_api_base_url=os.getenv("ISSUES_API_BASE_URL", "http://localhost:3000")
    )
    
    print("=" * 80)
    print("Issue Tracker AI Agent - Azure OpenAI Demo")
    print("=" * 80)
    
    # Example 1: Create assigned bug
    print("\n📌 Example 1: Create a bug and assign to John")
    result = await agent.handle_request(
        "Create a bug for the login issue and assign it to John"
    )
    print(f"Result: {result}\n")
    
    # Example 2: Create unassigned urgent bug
    print("\n📌 Example 2: Create an urgent unassigned bug")
    result = await agent.handle_request(
        "Create an urgent bug for the payment gateway timeout"
    )
    print(f"Result: {result}\n")
    
    # Example 3: Create feature request
    print("\n📌 Example 3: Create a feature request")
    result = await agent.handle_request(
        "Create a feature request for dark mode and assign to Jane"
    )
    print(f"Result: {result}\n")
    
    # Example 4: Search issues
    print("\n📌 Example 4: Search for high priority bugs")
    result = await agent.handle_request(
        "Show me all high priority bugs"
    )
    print(f"Found {result.get('count', 0)} issues\n")
    
    # Example 5: Update issue
    print("\n📌 Example 5: Update issue status")
    result = await agent.handle_request(
        "Mark issue 1 as done"
    )
    print(f"Result: {result}\n")
    
    # Example 6: Smart triage
    print("\n📌 Example 6: Smart bug triage")
    result = await agent.handle_request(
        "We have a critical authentication bug where users can't log in. This is affecting all users and blocking production."
    )
    print(f"Triage result: {result.get('triage_info', {})}\n")
    
    # Example 7: List team members
    print("\n📌 Example 7: List team members")
    result = await agent.handle_request(
        "Who's on the team?"
    )
    print(f"Found {result.get('count', 0)} team members\n")
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


async def example_api_usage():
    """
    Example of using the agent programmatically (without CLI)
    """
    
    agent = IssueTrackerAgent(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
        issues_api_key=os.getenv("ISSUES_API_KEY")
    )
    
    # Create a bug
    result = await agent.handle_request("Create a bug for slow database queries")
    
    if result["success"]:
        issue_id = result["issue"]["id"]
        print(f"Created issue #{issue_id}")
        
        # Update the issue
        update_result = await agent.handle_request(
            f"Assign issue {issue_id} to the backend team lead"
        )
        
        if update_result["success"]:
            print("Issue assigned successfully")
    
    # Search for issues
    search_result = await agent.handle_request(
        "Find all bugs assigned to John that are in progress"
    )
    
    for issue in search_result.get("issues", []):
        print(f"#{issue['id']}: {issue['title']}")


async def example_batch_operations():
    """
    Example of batch operations
    """
    
    agent = IssueTrackerAgent(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
        issues_api_key=os.getenv("ISSUES_API_KEY")
    )
    
    # Create multiple issues from a backlog
    backlog = [
        "Create a bug for the CSS alignment issue on mobile",
        "Add a feature for user profile pictures",
        "Create a task to update documentation for API v2",
        "We need to fix the critical memory leak in the backend",
    ]
    
    results = []
    for item in backlog:
        result = await agent.handle_request(item)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {result.get('message', 'Done')}")
        else:
            print(f"❌ {result.get('error', 'Failed')}")
    
    print(f"\nProcessed {len(results)} items")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_agent())
    
    # Or run specific examples:
    # asyncio.run(example_api_usage())
    # asyncio.run(example_batch_operations())
