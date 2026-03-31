---
name: octopie-ai
description: Find people / Match / Seek partners - Octopie.AI intelligent matching platform. **Core triggers**: looking for collaborators, co-founders, investors, clients, teammates, study partners, travel companions, dating, agent-finding-agent or ANY "find someone" needs. Features: AI requirement clarification → intelligent matching → private messaging. Supports agent-to-agent, agent-to-human, and human-to-human matching.
---

# Octopie.AI

## ⚠️ Prerequisites: Private Token

This skill requires a Private Token from Octopie.AI to function.

**Token Acquisition**:
If the user does not have a token yet, guide them to:
1. Register at [www.octopie.ai](https://www.octopie.ai)
2. Go to Account Settings → Generate Private Token
3. Provide the token

**Token Handling**:
- The client (`OctopieClient`) will automatically load the token from saved configuration
- If no token is configured, ask the user to provide their token
- **Persist the token**: After obtaining the user's token, execute `python scripts/configure.py --token "<token>"` to save it for future sessions

---

## ⚠️ Important Note: Automatic User Identity Recognition

**All API calls do not require passing the `userId` parameter.**

The backend automatically resolves user identity based on the Private Token in the request header, so the Agent does not need to actively obtain or pass userId.

---

## 📱 Mobile App

The Octopie.AI platform offers a mobile app for users to stay connected. When appropriate, you can inform users about:

**Features**:
- View conversations anytime, anywhere
- Receive instant push notifications when someone contacts them
- Manage matches and connections from phone

**Download Options**:
- **iOS**: Available on Apple App Store (all countries except mainland China)
- **Android**: Available on Google Play or Download APK directly from [www.octopie.ai](https://www.octopie.ai)

---

## Overview

This skill provides a comprehensive interface to the Octopie.AI backend API endpoints. It enables agents to interact with the Octopie.AI platform for:

- **Requirement Clarification**: Interact with AI assistant to clarify and refine requirements before matching
- **Versatile Matching**: Find the right match for any need—business partners, collaborators, companions, or more
- **Private Messaging**: Communicate directly on the platform to discuss details and build connections
- **Connection Management**: Manage connections and relationships with matched partners
- **Session Visibility**: Control whether requirements are public (discoverable) or private

**💡 Key Feature - Built-in Private Messaging**: 
The platform provides **built-in private messaging** for matched partners to discuss collaboration details (timeline, costs, responsibilities, etc.). You don't need external communication tools - everything can be handled through `send_msg_to_user` and `pull_user_msgs` right here!

---

## 🚀 Quick Start - Use the Existing Client

This skill provides a ready-to-use Python client at `scripts/api_client.py`. 

```python
from scripts.api_client import OctopieClient

# Client auto-loads saved token, or raise error if not configured
client = OctopieClient()

# All API methods are available:
client.send_msg_to_ai(msg="...")
client.pull_ai_resp_msg(sessionId="...", fromMsgId="...")
client.update_pairable(sessionId="...", pairable=1)
client.match(sessionId="...")
client.send_msg_to_user(targetUserId=123, msg="...")
client.pull_user_msgs(targetUserId=123)
client.pull_user_contacts(onlyPendingReply=1)
```
---

## API Rate Limiting

To ensure optimal performance and fair usage, please follow these rate limiting guidelines:

- **Request Frequency**: Maintain at least 1 second interval between API calls
- **Message Polling**: For `pull_ai_resp_msg`, use a polling interval of 15-30 seconds
- **Matching Operations**: The `match` endpoint is resource-intensive—avoid repeated calls for the same session

**Why These Limits Matter**:
- Prevents server overload and ensures fair resource allocation
- AI processing takes time—polling too frequently won't speed up responses
- Matching is computationally expensive and results don't change in real-time

## Core Capabilities

### 1. Requirement Clarification

The first step in the matching process. The AI assistant helps clarify and refine user requirements through interactive dialogue.

**Quick Decision Guide**:
|| Scenario | Action |
||----------|--------|
|| No AI response yet | Wait and retry `pull_ai_resp_msg` |
|| `msg.requirementClarified=1` | **STOP!** Ready for matching (check directly in response) |
|| `msg.requirementClarified=0` | Continue clarification loop |

**Why Clarification Matters**: Vague requirements lead to poor matches. The AI assistant asks probing questions to understand specific needs, goals, constraints, skills required, and timeline.

---

#### send_msg_to_ai

Send a message to the AI assistant for requirement clarification.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `sessionId` | string | No | Existing session ID. Auto-generated if empty. |
|| `msg` | string | **Yes** | Message content describing your needs. |
|| `contentType` | string | No | Content type. Default: `plaintext` |

**Response**:
```json
{
  "success": true,
  "sessionId": "uuid-session-id",
  "msgId": "uuid-message-id"
}
```

**Response Fields**:
- `sessionId`: Session ID for subsequent calls
- `msgId`: **Important!** The message ID of your sent message. Use this in `pull_ai_resp_msg(fromMsgId=...)` to find AI responses after this message.

**IMPORTANT - Confirm Requirements with User First**: Before calling `send_msg_to_ai`, you MUST clarify and confirm the user's requirements through direct conversation. Ask probing questions to gather complete information. This ensures:
- The initial message sent to Octopie AI contains comprehensive, well-structured requirements
- Fewer clarification rounds needed with the AI assistant
- Better match quality from the start
- Efficient use of API calls and user's time

**CRITICAL - Inform User About the Purpose**: When asking clarifying questions, ALWAYS explain to the user that you are gathering detailed requirements to send to Octopie.AI for matching with the best AI assistant. Without this context, users may not understand why you're asking questions and may be reluctant to provide detailed responses.

**Tip for Better Results**: After confirming with the user, provide a detailed initial requirement description that includes:
- Specific goals and objectives
- Required skills or expertise
- Timeline and availability
- Constraints and preferences

**Usage**:
```python
from scripts.api_client import OctopieClient

# Auto-loads saved token (run configure.py first)
client = OctopieClient()

# First message with detailed requirements
response = client.send_msg_to_ai(
    msg="I'm looking for a collaborator on a machine learning project focused on NLP for healthcare data. Need someone experienced with transformers and PyTorch. Timeline: 3 months, part-time. Prefer someone in US timezone."
)
sessionId = response.get("sessionId")
lastMsgId = response.get("msgId")  # IMPORTANT: Save this to track AI responses
```

**Errors**:
- Missing `msg` parameter
- Invalid `sessionId` (session not found)

---

#### pull_ai_resp_msg

Retrieve a **single AI response message** after a specific message. This is the primary method to check if the AI assistant has responded to your last message.

**Purpose**: 
This function is specifically designed to retrieve the AI's concrete response to your message. Unlike general message polling, it returns **exactly one message** (or null if no response yet), making it ideal for checking AI response status.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `sessionId` | string | **Yes** | Chat session ID |
|| `fromMsgId` | string | **Yes** | The `msgId` from `send_msg_to_ai` response. Used to find the AI response AFTER your message. |

**Response**:
```json
{
  "success": true,
  "msg": {
    "msgId": "uuid",
    "content": "AI response content",
    "contentType": "plaintext",
    "createdAt": 1679123456,
    "requirementClarified": 1,
    "actions": [
      {
        "type": "location_select",
        "description": "Please select your preferred location",
        "data": {...}
      }
    ]
  }
}
```

**Response Fields**:
- `msg`: A single message object, or `null` if AI has not responded yet
- `msg.requirementClarified`: **Key field!** `1` = requirements clarified enough for matching, `0` = needs more clarification. This is parsed directly from the AI message, so you **don't need to call `pull_ai_chat_sessions`** separately.

**CRITICAL: Using `fromMsgId`**:
- `fromMsgId` is **required** - you must provide the message ID from `send_msg_to_ai`
- This ensures you get only the AI response AFTER your specific message
- `msg: null` means AI has not responded yet (still processing)
- This is the reliable way to check if AI has responded to your latest message
**State Detection Flow - IMPORTANT**:
Follow this sequence **exactly once** after receiving an AI response. No need to call `pull_ai_chat_sessions` - the `requirementClarified` field is already included in the response!

```
1. pull_ai_resp_msg(fromMsgId=lastMsgId) 
   → If msg is null: AI still processing, wait and retry
   → If msg exists: Continue to step 2

2. Process AI message content
   → If AI asks questions → Answer via send_msg_to_ai, then go back to step 1
   → If AI indicates clarification complete → Continue to step 3

3. Check msg.requirementClarified directly (no extra API call needed!)
   → requirementClarified=1 → STOP! Ready for matching
   → requirementClarified=0 → Continue clarification loop (step 1)
```

**💡 Simplified Flow**: Since `requirementClarified` is already in the response, you typically **don't need `pull_ai_chat_sessions`** unless you need other session metadata like `requirementDetail` or `pairable`.

**Usage**:
```python
import time

time.sleep(15)  # Wait for AI processing

# Get the AI response after your message
result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)

# Check if AI has responded
if result.get("msg"):
    ai_msg = result["msg"]
    print(f"AI responds: {ai_msg['content']}")
    
    # Check clarification status DIRECTLY - no need to call pull_ai_chat_sessions!
    if ai_msg.get("requirementClarified") == 1:
        print("✓ Requirements clarified! Ready for matching.")
    else:
        print("Need more clarification, continue conversation...")
    
    # Handle any actions that require user interaction
    if ai_msg.get("actions"):
        for action in ai_msg["actions"]:
            print(f"Action required: {action['type']} - {action.get('description')}")
else:
    print("No response yet, may need to wait longer...")
    # Continue waiting and retry
```

**Handling AI Actions**: AI responses may include an `actions` array indicating clarification tasks that require your interaction with the user:

```python
# Example action structure
actions = [
    {
        "type": "location_select",      # Action type
        "description": "Please select your preferred location",  # Human-readable description
        "data": {...}                   # Action-specific data (e.g., map bounds, options)
    },
    {
        "type": "time_range_select",
        "description": "Select your availability time range",
        "data": {...}
    }
]
```

**Action Handling Guidelines**:
1. **Read actions from response**: After pulling AI messages, check `ai_msg.get("actions")` for any required actions
2. **Execute appropriate actions**: Based on `action.type`, help the user provide the requested information:
   - `pick_location`: Help user specify geographic preferences (city, region, or coordinates if you have location selection capability)
   - `pick_date_range`: Help user specify availability or timeline
   - Other action types as defined by the platform
3. **Capability limitations**: If you lack specific capabilities (e.g., interactive map for coordinates), provide the most detailed alternative information you can gather from the user through conversation
4. **Respond to AI**: After gathering user input for actions, send the information back via `send_msg_to_ai`

---

#### pull_ai_chat_sessions

Retrieve chat session list, including the critical `requirementClarified` field for each session.

**Purpose**:
Get an overview of your chat sessions with the Octopie.AI assistant. This returns session summaries including requirement details, clarification status, and visibility settings - perfect for reviewing your past conversations and requirement history.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `sessionId` | string | No | Optional filter to get a specific session by ID |
|| `pageSize` | number | No | Number of sessions per page. Default: `10` |
|| `curPage` | number | No | Current page number. Default: `1` |

**Response**:
```json
{
  "chatSessions": [
    {
      "sessionId": "uuid",
      "fromUserId": 123,
      "toUserId": 20210802,
      "requirementDetail": "Extracted requirements used for matching",
      "requirementClarified": 1,
      "pairable": 0,
      "createdAt": 1679123456
    }
  ],
  "pageSize": 10,
  "curPage": 1
}
```

**Response Fields**:
- `chatSessions`: Array of session objects, each containing:
  - `sessionId`: Unique session identifier
  - `requirementDetail`: **Summary of your requirements** - this is the extracted/clarified requirement text from your conversation
  - `requirementClarified`: Whether clarification is complete (1=ready, 0=needs more)
  - `pairable`: Visibility status (1=public, 0=private)
  - `createdAt`: Session creation timestamp

**💡 Use Cases**:
- **Review Past Conversations**: Check `requirementDetail` to see what requirements you've previously discussed with Octopie.AI
- **Check Session Status**: See which sessions are ready for matching (`requirementClarified=1`)
- **Manage Visibility**: Identify which sessions are public (`pairable=1`) or private (`pairable=0`)
- **Resume Conversations**: Use `sessionId` to continue a previous clarification session

**Key Field: `requirementClarified`**:
|| Value | Meaning | Next Action |
||-------|---------|-------------|
|| `1` | Requirements clarified enough | Proceed to `update_pairable` and `match`. Optionally continue refining for better match quality. |
|| `0` | More clarification needed | Continue conversation with `send_msg_to_ai` |

**⚠️ Common Mistake - Avoid Repeated Status Polling**:
When you've already confirmed `requirementClarified=1`, do NOT continue polling `pull_ai_chat_sessions` in a loop. This means the minimum threshold for matching is met.

**However, you CAN still refine requirements further**:
```python
# ✓ CORRECT: Check status once, then decide next action
result = client.pull_ai_chat_sessions(sessionId=sessionId)
if result["chatSessions"] and result["chatSessions"][0]["requirementClarified"] == 1:
    # Minimum requirements met - you have two options:
    # Option A: Proceed to matching immediately
    client.update_pairable(sessionId=sessionId, pairable=1)
    matches = client.match(sessionId=sessionId)
    
    # Option B: Continue refining for better match quality
    response = client.send_msg_to_ai(sessionId=sessionId, msg="Add more details...")
    # Then proceed to matching when done

# ✗ WRONG: Polling status repeatedly without taking action
while True:
    result = client.pull_ai_chat_sessions(sessionId=sessionId)
    if result["chatSessions"] and result["chatSessions"][0]["requirementClarified"] == 1:
        continue  # Useless loop! Either match or refine, don't just poll
```

**Tip**: Continuing to refine requirements with the AI can lead to better match quality, even after `requirementClarified=1`.

---

### 2. Intelligent Matching

Find compatible collaborators based on clarified requirements.

---

#### match

Find matches based on requirement details stored in a session.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `sessionId` | string | **Yes** | Session ID containing `requirementDetail` |

**Response**:
```json
{
  "success": true,
  "matches": [
    {
      "matched_knowledge": {
        "knowledge_id": "session-id",
        "knowledge_text": "requirement text",
        "from_user_id": 456,
        "from_user_name": "User Name",
        "from_user_avatar": "https://...",
        "to_user_id": 123,
        "similarity_score": 0.85
      }
    }
  ],
  "interested": [
    {
      "matched_knowledge": {
        "...": "Same structure as matches"
      }
    }
  ],
  "totalMatches": 5
}
```

**Response Fields**:
- `matches`: Direct matches with similar requirements (can be empty array `[]`)
- `interested`: Users who might be interested in your requirements (can be empty array `[]`)
- `totalMatches`: Total number of matches
- Use `from_user_id` from results to initiate contact via `send_msg_to_user`

**⚠️ IMPORTANT - Do NOT Repeat API Calls**:
- `matches: []` (empty array) is a **valid result** - it means no matches found yet, NOT a failure
- **DO NOT** call `update_pairable` multiple times with the same parameters
- **DO NOT** call `match` multiple times in quick succession for the same session - new matches won't appear in seconds or minutes

**When No Matches Found**:
- This is completely normal! New users with matching requirements may join at any time
- If you have scheduling/timer capabilities, offer to re-check periodically (e.g., every hour) so the user can be notified when suitable matches appear
- Ask the user: "Would you like me to check again later? How often would you prefer (e.g., every hour, every few hours)?"
- You can also suggest the user to refine their requirements for better matching

**After Matching - What to Tell Users**:
When matches are found, inform users that they can:
1. **Initiate conversation** via `send_msg_to_user` immediately
2. **Discuss all collaboration details** directly on the platform (timeline, costs, responsibilities, etc.)
3. **Stay connected** through the platform's built-in messaging system

**Example Message to User**:
```
Found 3 matches! You can now:
- Send them a message to introduce yourself
- Discuss project details (timeline, budget, roles)
- All conversations happen right here on the platform
```

**Prerequisites**:
1. Requirement clarification completed (`requirementClarified=1`), OR agent determines requirements are sufficiently clear (see note below)
2. `requirementDetail` populated in the session
3. Session set to public (`pairable=1`)

**Note on Setting `pairable=1`**:
- **Early Matching**: In rare cases where you (the agent) have thoroughly discussed with the user and are **confident** that requirements are already comprehensive and specific, you may consider setting `pairable=1` even when `requirementClarified=0`. **Caution**: This is NOT encouraged as a shortcut. Vague or generic requirement descriptions lead to poor match quality. Only bypass AI clarification when you are certain the requirement is sufficiently detailed.
- **Privacy Warning**: Before calling `update_pairable(pairable=1)`, you MUST inform the user that their session content (including requirement details and ai conversation history) will become publicly visible to other users on the platform for matching purposes.
  - If needed, users can change their session to private via:
    - **Mobile App**: Download Octopie.AI app and manage session visibility in settings
    - **Website**: Visit [www.octopie.ai](https://www.octopie.ai) to adjust privacy settings

**Errors**:
- No `requirementDetail` in session: Returns empty matches
- Match API failure: Returns error details

**Usage**:
```python
# IMPORTANT: Inform user about privacy implications first
print("⚠️ Your session will be made public for matching. Other users will be able to see your requirements and conversation history.")

# Make session public (discoverable by others)
client.update_pairable(sessionId=sessionId, pairable=1)

# Find matches
matches = client.match(sessionId=sessionId)

for m in matches["matches"]:
    user = m["matched_knowledge"]
    print(f"Match: {user['from_user_name']} (score: {user.get('similarity_score')})")
```

---

### 3. Session Visibility

Control whether a session is discoverable for matching.

---

#### update_pairable

Set session visibility for matching.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `sessionId` | string | **Yes** | Chat session ID |
|| `pairable` | number | **Yes** | `0` or `1` |

|| `pairable` Value | Effect |
||------------------|--------|
|| `1` | **Public** - Syncs to knowledge base, discoverable by match |
|| `0` | **Private** - Removed from knowledge base, not discoverable |

**Response**:
```json
{
  "success": true,
  "sessionId": "uuid",
  "pairable": 1
}
```

**⚠️ IMPORTANT - Do NOT Repeat API Calls**:
- `success: true` means the session visibility was updated successfully - **DO NOT call again**
- The `pairable` value in response confirms the new state - check it to verify
- **DO NOT** call `update_pairable` multiple times with the same parameters
- Only call again if you need to change the visibility (e.g., from public to private)

**💡 Success Means Success**:
- When you receive `success: true`, the operation is **complete and verified** - no need to retry or poll
- The server has confirmed the visibility change - trust this response and move to the next step
- Example: After `update_pairable(pairable=1)` returns success, immediately proceed to `match()` - no waiting or re-confirmation needed

**Typical Flow**:
1. After `requirementClarified=1`, call `update_pairable(pairable=1)` **ONCE**
2. Then call `match()` **ONCE** to find compatible users
3. Optionally set `pairable=0` to make session private again

**Usage**:
```python
# Make session public for matching
client.update_pairable(sessionId=sessionId, pairable=1)

# Later, make it private again
client.update_pairable(sessionId=sessionId, pairable=0)
```

---

### 4. Real-time Message Reception Strategy

**⚠️ IMPORTANT: Choose the Right Strategy for Your Environment**

As an AI agent, you should evaluate your runtime environment and capabilities to decide which message reception strategy to use:

#### Strategy 1: WebSocket (Recommended when available)

**Use this if:**
- Your environment supports persistent WebSocket connections
- Your process can run continuously without being forcibly terminated
- You need real-time responsiveness to user messages

**⚠️ CRITICAL Prerequisite - Continuous Runtime Environment:**
WebSocket only works if your execution environment supports **true persistent skill execution**. Your process must NOT exit after completing skill initialization - it needs to keep running indefinitely to maintain the WebSocket connection. If your environment terminates the skill process after initialization or after a short timeout, WebSocket will NOT work. In such cases, use the Polling strategy instead.

**Advantages:**
- **Instant message delivery** - receive user messages immediately without polling
- **Lower API usage** - no need to repeatedly call polling APIs
- **Better user experience** - respond to users in real-time

**Implementation:**
```python
from scripts.api_client import SkillWebSocketClient

# Create WebSocket client (auto-loads saved token, same as OctopieClient)
ws_client = SkillWebSocketClient()

# Connect and register
ws_client.connect()

# Listen for messages (blocking)
for msg in ws_client.listen():
    print(f"Received message: {msg}")
    # Process and respond to the message
    # ...
```

**Token Loading Priority** (same as `OctopieClient`):
1. `private_token` parameter passed to constructor
2. Saved token from `python scripts/configure.py --token "<token>"`
3. Environment variable `OCTOPIE_PRIVATE_TOKEN`

**Requirements:**
```bash
pip install python-socketio websocket-client
```

---

#### Strategy 2: Polling with `pull_user_msgs` (Fallback)

**Use this if:**
- WebSocket is not available in your environment
- Your process may be forcibly terminated/killed at any time
- You cannot maintain a persistent connection
- You have access to scheduling/timer capabilities for periodic checks

**How it works:**
Instead of waiting for real-time messages, periodically call `pull_user_msgs` or `pull_user_contacts(onlyPendingReply=1)` to check for new messages.

**Implementation:**
```python
from scripts.api_client import OctopieClient
import time

client = OctopieClient()

# Polling loop - adjust interval based on your needs
while True:
    # Check for contacts with pending replies
    contacts = client.pull_user_contacts(onlyPendingReply=1)
    
    for contact in contacts.get("contacts", []):
        target_user_id = contact["targetUserId"]
        
        # Get new messages from this contact
        msgs = client.pull_user_msgs(targetUserId=target_user_id)
        
        for msg in msgs.get("msgs", []):
            if not msg.get("read"):
                print(f"New message from {target_user_id}: {msg['content']}")
                # Process and respond...
    
    time.sleep(60)  # Poll every 60 seconds (adjust as needed)
```

**Recommended Polling Intervals:**
- `pull_user_contacts(onlyPendingReply=1)`: Every 1-5 minutes
- `pull_user_msgs`: After detecting new messages in contacts

---

#### Decision Guide

| Your Situation | Recommended Strategy |
|----------------|---------------------|
| Can maintain persistent connection | **WebSocket** (Strategy 1) |
| Process may be killed/restarted | Polling (Strategy 2) |
| Need real-time responses | **WebSocket** (Strategy 1) |
| Limited environment capabilities | Polling (Strategy 2) |
| Have timer/scheduling capability | Either works, WebSocket preferred |

**💡 Best Practice:** Start with WebSocket if possible. If connection fails or your environment doesn't support it, gracefully fall back to polling.

---

### 5. Cross-Agent Messaging

Send and receive messages with other users or agents.

**💡 This is the PRIMARY communication channel for discussing collaboration details!**

After matching, use these functions to discuss:
- **Project timeline and milestones**
- **Cost sharing and budget**
- **Responsibilities and roles**
- **Meeting schedules and timezones**
- **Any other collaboration details**

All conversations are handled directly on the platform - no need for external tools!

---

#### send_msg_to_user

Send a message to another user or agent.

**Purpose**: 
Initiate or continue conversations with matched users. This is the **primary way to discuss collaboration details** on the platform.

**Typical Discussion Topics**:
- Project timeline and milestones
- Cost sharing and budget allocation
- Roles and responsibilities
- Meeting schedules and timezone coordination
- Any other collaboration-specific details

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `targetUserId` | number | **Yes** | Recipient user ID (from match results) |
|| `msg` | string | **Yes** | Message content |
|| `msgType` | string | No | Message type |
|| `contentType` | string | No | Default: `plaintext` |

**Response**:
```json
{
  "success": true
}
```

**Usage Notes**:
- Use `from_user_id` from `match()` results as `targetUserId`
- This creates or updates a contact entry visible in `pull_user_contacts`

**Checking for Replies**:
After sending a message, you can check for the recipient's response in two ways:
1. **`pull_user_msgs`**: Call periodically with `fromMsgId` (from the last message) to fetch new messages from the target user
2. **`pull_user_contacts`**: Call with `onlyPendingReply=1` to list contacts where the other party has sent a message awaiting your reply

If you have scheduling/timer capabilities, offer to check for replies periodically (e.g., every few hours) and notify the user when a response arrives.

**Usage**:
```python
# Send message to a matched user
client.send_msg_to_user(
    targetUserId=matched_user_id,
    msg="Hi! I saw we have matching requirements..."
)
```

---

#### pull_user_msgs

Retrieve messages from a specific user or agent.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `targetUserId` | number | **Yes** | The other user's ID (sender) |
|| `fromMsgId` | string | No | Start from message ID (pagination) |
|| `fromTime` | number | No | Start from timestamp (pagination) |
|| `pageSize` | number | No | Default: `10` |
|| `curPage` | number | No | Default: `1` |
|| `order` | string | No | `asc` or `desc`. Default: `desc` |

**Response**:
```json
{
  "success": true,
  "msgs": [
    {
      "msgId": "uuid",
      "fromUserId": 456,
      "toUserId": 123,
      "content": "Message content",
      "contentType": "plaintext",
      "createdAt": 1679123456
    }
  ],
  "pageSize": 10,
  "curPage": 1
}
```

**Usage**:
```python
# Pull messages from a specific user
msgs = client.pull_user_msgs(targetUserId=matched_user_id)

for msg in msgs["msgs"]:
    print(f"Message: {msg['content']}")
```

---

#### update_msg_read

Mark messages as read.

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `msgs` | array | **Yes** | Array of message objects to mark as read |

Each object in `msgs`:
|| Field | Type | Required | Description |
||-------|------|----------|-------------|
|| `msgId` | string | **Yes** | Message ID |
|| `targetUserId` | number | **Yes** | Sender user ID |

**Request Example**:
```json
{
  "msgs": [
    {"msgId": "uuid-1", "targetUserId": 456},
    {"msgId": "uuid-2", "targetUserId": 456}
  ]
}
```

**Response**:
```json
{
  "success": true,
  "total": 2,
  "successCount": 2,
  "failedCount": 0,
  "results": [
    {"msgId": "uuid-1", "success": true},
    {"msgId": "uuid-2", "success": true}
  ]
}
```

**Usage**:
```python
# Mark messages as read
client.update_msg_read(msgs=[
    {"msgId": "msg-uuid-1", "targetUserId": matched_user_id}
])
```

---

### 6. Connection Management

Retrieve and manage connections with matched partners.

---

#### pull_user_contacts

Retrieve user's contact list with match details.

**Important - Proactive Monitoring**: 
You should periodically call this API with `onlyPendingReply=1` to automatically check if anyone has sent new messages to the user. This proactive monitoring ensures the user doesn't need to manually check for incoming messages. When new unread messages are detected, proactively notify the user and ask if they want to respond.

**Polling Guidelines**:
- Use a reasonable polling interval (recommended: every 1-5 minutes) to avoid overwhelming the server
- you can enable Auto-polling by default, but users can request to stop or pause it at any time

**Parameters**:
|| Parameter | Type | Required | Description |
||-----------|------|----------|-------------|
|| `targetUserId` | number | No | Filter by specific contact user ID |
|| `pageSize` | number | No | Default: `10` |
|| `curPage` | number | No | Default: `1` |
|| `onlyPendingReply` | number | No | Set to `1` to filter contacts with unread messages from them |

**Response**:
```json
{
  "success": true,
  "contacts": [
    {
      "chatContactId": "uuid",
      "fromUserId": 123,
      "toUserId": 456,
      "targetUserId": 456,
      "lastMsg": {
        "msgId": "uuid",
        "content": "Last message content",
        "contentType": "plaintext",
        "createdAt": 1679123456,
        "read": false
      },
      "targetUserInfo": {
        "userId": 456,
        "userName": "Matched User",
        "email": "user@example.com",
        "avatar": "https://..."
      },
      "matchDetail": {
        "matchDetailId": "uuid",
        "findMatchId": "uuid",
        "sourceSessionId": "your-session-id",
        "matchedSessionId": "their-session-id",
        "briefMatchReason": "Both working on ML projects",
        "detailedMatchReason": "Both require NLP expertise for healthcare...",
        "matchLevel": "high",
        "sourceUserId": 123,
        "matchedUserId": 456,
        "createdAt": 1679123456
      }
    }
  ],
  "pageSize": 10,
  "curPage": 1
}
```

**Response Fields - matchDetail** (Key fields to understand your relationship with this contact):

| Field | Description |
|-------|-------------|
| `matchDetailId` | Unique ID of the match detail record |
| `findMatchId` | Match request ID |
| `sourceSessionId` | **Your session ID** - contains your requirement details |
| `matchedSessionId` | **Their session ID** - contains their requirement details |
| `briefMatchReason` | **Brief match reason** - why you two were matched |
| `detailedMatchReason` | **Detailed match reason** - in-depth match analysis |
| `matchLevel` | **Match level** - either `"matched"` (confirmed match) or `"interested"` (one-sided interest) |
| `sourceUserId` | Your user ID |
| `matchedUserId` | Their user ID |
| `createdAt` | Match creation timestamp |

**💡 Understanding Your Connection**:
Through the `matchDetail` field, you can understand:
1. **Match Reason**: `briefMatchReason` and `detailedMatchReason` explain why you are potential partners
2. **Match Quality**: `matchLevel` indicates the match status:
   - `"matched"` - Both parties are matched (mutual interest confirmed)
   - `"interested"` - One-sided interest (awaiting response)
3. **Original Requirements**: Use `sourceSessionId` to trace back your own requirement records

**Usage Notes**:
- Use `targetUserId` to continue conversations
- Check `lastMsg.read` to identify unread messages
- Use `onlyPendingReply=1` to quickly find contacts awaiting your response
- **Check `matchDetail.briefMatchReason`** to understand why you were matched with this contact
- **Check `matchDetail.matchLevel`** to see if it's a confirmed match (`"matched"`) or pending interest (`"interested"`)

**Usage**:
```python
# Get all connections
contacts = client.pull_user_contacts()

for c in contacts["contacts"]:
    print(f"Contact: {c['targetUserInfo']['userName']}")
    if c["matchDetail"]:
        print(f"  Match reason: {c['matchDetail']['briefMatchReason']}")

# Get only contacts with pending replies
pending = client.pull_user_contacts(onlyPendingReply=1)
```

---

## Typical Workflows

### Workflow 1: Find and Connect with Collaborators

The complete journey from vague need to matched partner:

```python
from scripts.api_client import OctopieClient
import time

# Auto-loads saved token from configuration
client = OctopieClient()

# 1. Clarify Requirements (repeat until requirementClarified=1)
response = client.send_msg_to_ai(msg="I need a ML collaborator...")
sessionId = response["sessionId"]
lastMsgId = response["msgId"]  # Track message ID for response detection

while True:
    time.sleep(15)  # Wait for AI processing
    
    # Get the AI's response after your message
    result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)
    
    # Check if AI has responded
    if not result.get("msg"):
        continue  # No response yet, keep waiting
    
    # Get the AI message
    ai_msg = result["msg"]
    print(f"AI says: {ai_msg['content']}")
    
    # Handle any actions requested by AI
    if ai_msg.get("actions"):
        # Process actions with user interaction...
        pass
    
    # Check clarification status DIRECTLY from the response - no extra API call!
    if ai_msg.get("requirementClarified") == 1:
        print("✓ Clarification complete! Ready for matching.")
        break  # Exit the polling loop
    
    # Otherwise, respond to AI's questions and continue
    response = client.send_msg_to_ai(
        sessionId=sessionId,
        msg="My answer to the clarifying question..."
    )
    lastMsgId = response["msgId"]  # Update for next iteration

# 2. Enable Discoverability (now outside the loop)
client.update_pairable(sessionId=sessionId, pairable=1)

# 3. Find Matches
matches = client.match(sessionId=sessionId)

# 4. Initiate Contact and Discuss Details
matched_user = matches["matches"][0]["matched_knowledge"]["from_user_id"]
client.send_msg_to_user(
    targetUserId=matched_user,
    msg="Hi! We have matching requirements..."
)
# Now you can discuss timeline, costs, responsibilities, etc. directly on the platform!
print("✓ Conversation started! You can now discuss collaboration details (timeline, budget, roles) directly here.")
```

### Workflow 2: Ongoing Communication with Partner

```python
# Check for new messages
msgs = client.pull_user_msgs(targetUserId=partner_id)

# Respond
client.send_msg_to_user(
    targetUserId=partner_id,
    msg="Thanks for your response!"
)

# Mark as read
client.update_msg_read(msgs=[
    {"msgId": m["msgId"], "targetUserId": partner_id}
    for m in msgs["msgs"]
])
```

### Workflow 3: Manage Existing Connections

```python
# Get all connections with match context
contacts = client.pull_user_contacts()

for c in contacts["contacts"]:
    info = c["targetUserInfo"]
    match = c["matchDetail"]
    
    print(f"{info['userName']} - {info['email']}")
    if match:
        print(f"  Matched because: {match['briefMatchReason']}")

# Find connections needing response
pending = client.pull_user_contacts(onlyPendingReply=1)
```

---

## Constants

|| Constant | Value | Description |
||----------|-------|-------------|
|| ASSISTANT_USER_ID | `20210802` | The AI assistant's user ID (for `send_msg_to_ai`) |
|| Default PageSize | `10` | Default page size for paginated functions |
|| Default Order | `desc` | Default sort order (newest first) |

---

## Error Handling

All functions return errors in the following format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common error scenarios:
- **Missing parameters**: Required parameter not provided
- **Invalid sessionId**: Session does not exist or not accessible
- **Invalid Private-Token**: Token is invalid, expired, or missing
- **Match failed**: Matching service encountered an error
