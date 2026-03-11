# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│              "Create a bug for John"                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLI Interface (cli.py)                        │
│  - Interactive mode or single command                            │
│  - Formats output for user                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                AI AGENT (agent.py) - THE ORCHESTRATOR            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Intent Parsing (using Claude)                           │ │
│  │    User input → Structured intent                          │ │
│  │    "Create bug for John" →                                 │ │
│  │    {action: "create_issue", title: "...",                  │ │
│  │     issue_type: "bug", assignee_name: "John"}              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                       │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │ 2. Business Logic & Orchestration                          │ │
│  │    - Find user "John" → call users-list tool               │ │
│  │    - Find "bug" tag → call tags-list tool                  │ │
│  │    - Create issue with IDs → call issues-create tool       │ │
│  │    - Apply smart defaults (priority: medium)               │ │
│  │    - Cache frequently accessed data                        │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │                                       │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │ 3. Tool Execution                                          │ │
│  │    Calls tool_server via HTTP                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Tool Server (tool_server.py)                        │
│  - FastAPI server on localhost:8000                              │
│  - Maps tool names to API endpoints                              │
│  - Handles authentication headers                                │
│  - Forwards requests to backend API                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend API (Issues Service)                        │
│  - REST API at https://api.issues.com                            │
│  - Handles database operations                                   │
│  - Returns results                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: "Create bug for John"

```
┌──────────────┐
│ 1. User Input│
│              │
│ "Create a    │
│  bug for the │
│  login issue │
│  and assign  │
│  to John"    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 2. Agent: Parse Intent (Claude API)          │
│                                               │
│ INPUT: Raw text                               │
│ OUTPUT: {                                     │
│   "action": "create_issue",                   │
│   "title": "login issue",                     │
│   "issue_type": "bug",                        │
│   "assignee_name": "John",                    │
│   "priority": "medium"                        │
│ }                                             │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 3. Agent: Find User ID                       │
│                                               │
│ TOOL CALL: users-list                        │
│ RESULT: [                                     │
│   {id: "john123", name: "John Doe"},          │
│   {id: "jane456", name: "Jane Smith"}         │
│ ]                                             │
│ MATCH: "John" → "john123"                     │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 4. Agent: Find Tag ID                        │
│                                               │
│ TOOL CALL: tags-list                         │
│ RESULT: [                                     │
│   {id: 3, name: "bug", color: "#ef4444"},    │
│   {id: 4, name: "feature", ...}              │
│ ]                                             │
│ MATCH: "bug" → ID 3                           │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 5. Agent: Create Issue                       │
│                                               │
│ TOOL CALL: issues-create                     │
│ PAYLOAD: {                                    │
│   title: "login issue",                       │
│   assigned_user_id: "john123",                │
│   priority: "medium",                         │
│   tag_ids: [3]                                │
│ }                                             │
│ RESULT: {id: 8, ...}                          │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ 6. Response  │
│              │
│ "✅ Created  │
│  bug #8:     │
│  login issue │
│  Assigned to │
│  John Doe"   │
└──────────────┘
```

## Comparison: API-Based vs Job-Based

### Current Implementation (API-Based)

```
User: "Create bug for John"
            ↓
        AI Agent
            ↓
    ┌───────┴───────┐
    │               │
    ▼               ▼
users-list    tags-list
(Call 1)      (Call 2)
    │               │
    ▼               ▼
Find "John"   Find "bug"
    │               │
    └───────┬───────┘
            ▼
    issues-create
      (Call 3)

Total: 3 API calls
Agent orchestrates everything
```

### Future Enhancement (Job-Based)

```
User: "Create bug for John"
            ↓
        AI Agent
            ↓
    create-issue-job
    { assignee_name: "John" }
            ↓
        Backend
     (handles all logic)
      ┌─────┴─────┐
      ▼           ▼
  Find John   Find bug tag
      │           │
      └─────┬─────┘
            ▼
      Create issue
      in transaction

Total: 1 API call
Backend orchestrates
```

## Tool Design Pattern

```
┌─────────────────────────────────────────────────────────┐
│                 Flexible Tool Design                     │
│                                                           │
│  create-issue({                                          │
│    title: "required",                                    │
│    issue_type: "required",                               │
│    assignee_name: "optional",  ← Handles variations     │
│    priority: "optional",        ← Smart defaults        │
│    status: "optional"           ← One tool, many uses   │
│  })                                                      │
│                                                           │
│  Handles ALL these cases:                                │
│  ✓ Create assigned bug                                   │
│  ✓ Create unassigned bug                                 │
│  ✓ Create urgent bug                                     │
│  ✓ Create feature                                        │
│  ✓ Create task                                           │
│  ✓ Any combination!                                      │
└─────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
User Input
    ↓
┌───────────────────┐
│ Parse Intent      │
│ (Claude)          │
└─────┬─────────────┘
      │
      ├─ Success → Continue
      │
      └─ Error ─────────┐
                        ▼
                    "I couldn't understand that.
                     Please rephrase."
                        │
                        ↓
                    Return to user

Tool Execution
    ↓
┌───────────────────┐
│ Call API          │
└─────┬─────────────┘
      │
      ├─ Success → Return result
      │
      ├─ 404 (User not found) ──┐
      │                          ▼
      │                      "User 'John' not found.
      │                       Available: Jane, Bob, Alice"
      │                          │
      │                          ↓
      │                      Return to user
      │
      ├─ 500 (Server error) ───┐
      │                         ▼
      │                     Retry with backoff
      │                         │
      │                         ├─ Success → Continue
      │                         │
      │                         └─ Still fails ─┐
      │                                          ▼
      │                                      "Service
      │                                       temporarily
      │                                       unavailable"
      │                                          │
      └──────────────────────────────────────────┘
                                                 │
                                                 ▼
                                            Return to user
```

## Caching Strategy

```
┌─────────────────────────────────────────┐
│         Agent Memory                     │
│                                           │
│  _users_cache: [{id, name, email}, ...]  │
│  _tags_cache: [{id, name, color}, ...]   │
│                                           │
│  TTL: Until agent restart                 │
│  Invalidation: On create/update           │
└─────────────────────────────────────────┘
        ↑                    ↑
        │                    │
   First call           Subsequent calls
   (API fetch)          (From cache)
        │                    │
        ▼                    ▼
   200ms latency         <1ms latency
```

## Integration Points

```
┌────────────────────────────────────────────────┐
│           External Integrations                 │
└────────────────────────────────────────────────┘
              │
     ┌────────┼────────┬──────────┐
     ▼        ▼        ▼          ▼
┌──────┐ ┌──────┐ ┌──────┐  ┌──────────┐
│Slack │ │Discord│ │Email │  │Webhooks  │
└───┬──┘ └───┬──┘ └───┬──┘  └────┬─────┘
    │        │        │           │
    └────────┴────────┴───────────┘
                 │
                 ▼
         ┌──────────────┐
         │  AI Agent    │
         └──────────────┘
                 │
                 ▼
         ┌──────────────┐
         │Backend API   │
         └──────────────┘
```
