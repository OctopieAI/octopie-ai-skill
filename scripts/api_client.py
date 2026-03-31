#!/usr/bin/env python3
"""
Octopie.AI API Client

A Python client for interacting with the Octopie.AI backend API endpoints.
This script provides functions to call all skill-related API endpoints.

Authentication:
    All requests require a private-token obtained from www.octopie.ai.
    The token is passed in the 'private-token' header and the backend
    automatically resolves the user ID from it.

Usage:
    from api_client import OctopieClient

    client = OctopieClient(private_token="your-token-here")

    # Send message to AI
    response = client.send_msg_to_ai(
        msg="I need help with finding a project partner"
    )

WebSocket Usage:
    from api_client import SkillWebSocketClient

    ws_client = SkillWebSocketClient(private_token="your-token-here")

    # Connect and register
    ws_client.connect()

    # Wait for messages (blocking)
    for msg in ws_client.listen():
        print(f"Received: {msg}")

    # Or use callback
    ws_client.on_message = lambda msg: print(f"Got: {msg}")
    ws_client.listen_blocking()
"""

import requests
import json
import os
import time
import threading
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
from queue import Queue, Empty

# Try to import socketio, provide helpful error if not installed
try:
    import socketio
except ImportError:
    socketio = None


# Default production API URL (built into the skill)
DEFAULT_API_URL = "https://www.octopie.ai"
DEFAULT_CHAT_API_URL = "https://chat.octopie.ai"

# Configuration file location
CONFIG_DIR = Path(__file__).parent.parent / ".config"
CONFIG_FILE = CONFIG_DIR / "credentials.json"


def _load_saved_token() -> Optional[str]:
    """
    Load Private Token from saved configuration.
    
    Returns:
        Saved token if exists, None otherwise
    """
    if not CONFIG_FILE.exists():
        return None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get("private_token")
    except Exception:
        return None


class OctopieClient:
    """Client for Octopie.AI backend API."""
    
    def __init__(
        self, 
        private_token: Optional[str] = None, 
        base_url: str = DEFAULT_API_URL,
        timeout: int = 30
    ):
        """
        Initialize the Octopie.AI API client.
        
        Args:
            private_token: Your private token from www.octopie.ai
                           If not provided, will try to load from saved config
                           (Generate at: Account Settings -> Generate Private Token)
            base_url: API base URL (default: production URL)
            timeout: Request timeout in seconds (default: 30)
        """
        # Try to load token from multiple sources
        if not private_token:
            private_token = _load_saved_token()
        
        if not private_token:
            private_token = os.environ.get("OCTOPIE_PRIVATE_TOKEN")
        
        if not private_token:
            raise ValueError(
                "Private token is required. Options:\n"
                "1. Run: python scripts/configure.py  (recommended)\n"
                "2. Set environment variable: OCTOPIE_PRIVATE_TOKEN\n"
                "3. Pass token directly: OctopieClient(private_token='...')\n"
                "Get your token at: www.octopie.ai → Account Settings → Generate Private Token"
            )
        
        self.base_url = base_url.rstrip('/')
        self.api_prefix = "/api"
        self.private_token = private_token
        self.timeout = timeout
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers with authentication token.
        
        Returns:
            Headers dict with private-token
        """
        return {
            "Content-Type": "application/json",
            "Private-Token": self.private_token
        }
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            Response JSON data (unwrapped from response wrapper)

        Raises:
            requests.RequestException: If the request fails
            ValueError: If response format is invalid or code != 0
        """
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        headers = self._get_headers()
        response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()

        # Validate response structure
        if not isinstance(result, dict):
            raise ValueError(f"Invalid response format: expected dict, got {type(result)}")

        # Check response code
        code = result.get("code")
        if code is None:
            raise ValueError("Missing 'code' field in response")
        
        if code != 0:
            error_msg = result.get("data", "Unknown error")
            raise ValueError(f"API Error (code={code}): {error_msg}")

        # Return data field directly
        return result.get("data", {})
    
    # ==================== Requirement Clarification ====================
    
    def send_msg_to_ai(
        self,
        msg: str,
        sessionId: Optional[str] = None,
        contentType: str = "plaintext"
    ) -> Dict[str, Any]:
        """
        Send a message to the AI assistant for requirement clarification.
        
        Args:
            msg: Message content describing your needs
            sessionId: Optional existing session ID (auto-generated if None)
            contentType: Content type (default: "plaintext")
            
        Returns:
            Response with:
            - sessionId: Session ID for subsequent calls
            - msgId: IMPORTANT! Message ID of your sent message.
                     Use this in pull_ai_resp_msg(fromMsgId=...) to find AI responses
                     AFTER your message.
        
        Example:
            response = client.send_msg_to_ai(msg="I need a ML collaborator")
            sessionId = response["sessionId"]
            lastMsgId = response["msgId"]
            
            # Later: pull AI response AFTER your message
            result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)
            if result.get("msg"):
                print(f"AI responds: {result['msg']['content']}")
        """
        data = {
            "msg": msg,
            "contentType": contentType
        }
        if sessionId:
            data["sessionId"] = sessionId
        return self._post("/skill/send_msg_to_ai", data)
    
    def pull_ai_chat_sessions(
        self,
        sessionId: Optional[str] = None,
        pageSize: int = 10,
        curPage: int = 1
    ) -> Dict[str, Any]:
        """
        Retrieve chat session list, including clarified requirementDetail for each.
        
        Args:
            sessionId: Optional filter to get a specific session by ID
            pageSize: Number of sessions per page (default: 10)
            curPage: Current page number (default: 1)
            
        Returns:
            Dict with:
            - chatSessions: List of session objects, each with:
              - requirementDetail: The structured requirement (used for matching)
              - requirementClarified: 1=ready for matching, 0=needs more clarification
              - pairable: Current visibility status
            - pageSize: Number of sessions per page
            - curPage: Current page number
            
        Note:
            After each send_msg_to_ai, wait 10-30 seconds then call this method
            to check if requirementClarified=1 before proceeding to matching.
        """
        data = {
            "pageSize": pageSize,
            "curPage": curPage
        }
        if sessionId:
            data["sessionId"] = sessionId
        return self._post("/skill/pull_ai_chat_sessions", data)
    
    def pull_ai_resp_msg(
        self,
        sessionId: str,
        fromMsgId: str
    ) -> Dict[str, Any]:
        """
        Retrieve a single AI response message after a specific message.
        
        This is the primary method to check if the AI assistant has responded
        to your last message. Returns exactly one message or null.
        
        Args:
            sessionId: Chat session ID
            fromMsgId: REQUIRED! The msgId from send_msg_to_ai response.
                       Used to find the AI response AFTER your specific message.
            
        Returns:
            Dict with:
            - success: True if request succeeded
            - msg: Single message object or None if no response yet
            
            Message object contains:
            - msgId: Message ID
            - content: AI response content (think tags removed)
            - contentType: Content type
            - createdAt: Timestamp
            - requirementClarified: 1=ready for matching, 0=needs more clarification
            - actions: List of actions requiring user interaction (optional)
        
        Example:
            response = client.send_msg_to_ai(sessionId=sessionId, msg="...")
            lastMsgId = response["msgId"]
            
            time.sleep(15)
            result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)
            
            if result.get("msg"):
                ai_msg = result["msg"]
                print(f"AI responds: {ai_msg['content']}")
                
                # Check clarification status directly from response
                if ai_msg.get("requirementClarified") == 1:
                    print("Ready for matching!")
            else:
                # No response yet, wait and retry
        """
        data = {
            "sessionId": sessionId,
            "fromMsgId": fromMsgId
        }
        return self._post("/skill/pull_ai_resp_msg", data)
    
    # ==================== Intelligent Matching ====================
    
    def match(self, sessionId: str) -> Dict[str, Any]:
        """
        Find compatible collaborators based on clarified requirements.
        
        Prerequisites:
            1. Requirement clarification completed with AI
            2. requirementDetail populated in the session
            3. Session set to public (pairable=1)
        
        Args:
            sessionId: Session ID containing clarified requirementDetail
            
        Returns:
            Dict with:
            - success: bool - True if API call succeeded, False if error
            - matches: list - Direct matches (may be empty [])
            - interested: list - Interested users (may be empty [])
            - totalMatches: int - Total number of matches
            - error: str - Error message if success=False
            
        IMPORTANT:
            - Check result["success"] first to determine if call succeeded
            - Empty matches [] is a valid result (no matches found yet)
            - DO NOT repeat this call - matching is not real-time
        """
        return self._post("/skill/match", {"sessionId": sessionId})
    
    # ==================== Session Visibility ====================
    
    def update_pairable(self, sessionId: str, pairable: int) -> Dict[str, Any]:
        """
        Set session visibility for matching.
        
        Args:
            sessionId: Chat session ID
            pairable: 1 for public (discoverable), 0 for private
            
        Returns:
            Dict with:
            - success: bool - True if update succeeded
            - sessionId: str - The session ID
            - pairable: int - The new pairable value (confirms the change)
            
        IMPORTANT:
            - Check result["success"] to confirm the update
            - DO NOT repeat this call with the same parameters
            - The response confirms the new state in result["pairable"]
        """
        return self._post("/skill/update_pairable", {
            "sessionId": sessionId,
            "pairable": pairable
        })
    
    # ==================== Cross-Agent Messaging ====================
    
    def send_msg_to_user(
        self,
        targetUserId: int,
        msg: str,
        msgType: Optional[str] = None,
        contentType: str = "plaintext"
    ) -> Dict[str, Any]:
        """
        Send a message to another user or agent.
        
        Args:
            targetUserId: Recipient user ID (from match results)
            msg: Message content
            msgType: Optional message type
            contentType: Content type (default: "plaintext")
            
        Returns:
            Send result
        """
        data = {
            "targetUserId": targetUserId,
            "msg": msg,
            "contentType": contentType
        }
        if msgType:
            data["msgType"] = msgType
        return self._post("/skill/send_msg_to_user", data)
    

    def pull_user_msgs(
        self,
        targetUserId: int,
        fromMsgId: Optional[str] = None,
        fromTime: Optional[int] = None,
        pageSize: int = 10,
        curPage: int = 1,
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Retrieve messages from a specific user or agent.
        
        Args:
            targetUserId: Target user ID (sender, from match results)
            fromMsgId: Start from this message ID
            fromTime: Start from this timestamp
            pageSize: Number of messages per page
            curPage: Current page number
            order: Sort order ("asc" or "desc")
            
        Returns:
            List of messages
        """
        data = {
            "targetUserId": targetUserId,
            "pageSize": pageSize,
            "curPage": curPage,
            "order": order
        }
        if fromMsgId:
            data["fromMsgId"] = fromMsgId
        if fromTime:
            data["fromTime"] = fromTime
        return self._post("/skill/pull_user_msgs", data)
    
    def update_msg_read(
        self,
        msgs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Mark messages as read.
        
        Args:
            msgs: List of {msgId, targetUserId} objects
            
        Returns:
            Update results
        """
        return self._post("/skill/update_msg_read", {"msgs": msgs})
    
    # ==================== Connection Management ====================
    
    def pull_user_contacts(
        self,
        targetUserId: Optional[int] = None,
        pageSize: int = 10,
        curPage: int = 1,
        onlyPendingReply: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve connections with matched partners.

        Args:
            targetUserId: Filter by specific contact
            pageSize: Number of contacts per page
            curPage: Current page number
            onlyPendingReply: 1 to filter contacts with pending replies

        Returns:
            List of contacts with match details and last messages
        """
        data = {
            "pageSize": pageSize,
            "curPage": curPage,
            "onlyPendingReply": onlyPendingReply
        }
        if targetUserId:
            data["targetUserId"] = targetUserId
        return self._post("/skill/pull_user_contacts", data)


class SkillWebSocketClient:
    """
    WebSocket client for receiving real-time messages via skill channel.

    Uses Socket.IO to connect to the skill websocket server.
    The server path is /skill (nginx routes to skill.js port).

    Requirements:
        pip install python-socketio websocket-client
    """

    def __init__(
        self,
        private_token: Optional[str] = None,
        chat_url: str = DEFAULT_CHAT_API_URL,
        auto_reconnect: bool = True
    ):
        """
        Initialize the WebSocket client.

        Args:
            private_token: Your private token (same as OctopieClient)
            chat_url: WebSocket server URL (default: DEFAULT_CHAT_API_URL)
            auto_reconnect: Enable automatic reconnection (default: True)

        Raises:
            ValueError: If private_token is not provided
            ImportError: If python-socketio is not installed
        """
        if socketio is None:
            raise ImportError(
                "python-socketio is required for WebSocket support.\n"
                "Install with: pip install python-socketio websocket-client"
            )

        # Load token from multiple sources
        if not private_token:
            private_token = _load_saved_token()
        if not private_token:
            private_token = os.environ.get("OCTOPIE_PRIVATE_TOKEN")
        if not private_token:
            raise ValueError(
                "Private token is required for WebSocket connection.\n"
                "Set OCTOPIE_PRIVATE_TOKEN or pass private_token parameter."
            )

        self.private_token = private_token
        self.chat_url = chat_url.rstrip('/')
        self.auto_reconnect = auto_reconnect

        # Connection state
        self._sio: Optional[socketio.Client] = None
        self._is_connected = False
        self._is_registered = False
        self._user_id: Optional[str] = None
        self._register_error: Optional[str] = None

        # Message queue for listen() pattern
        self._message_queue: Queue = Queue()

        # Optional callback for message handling
        self.on_message: Optional[Callable[[Dict[str, Any]], None]] = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def is_registered(self) -> bool:
        return self._is_registered

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    def connect(self, timeout: float = 10.0) -> bool:
        """
        Connect to the WebSocket server and register.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected and registered successfully

        Raises:
            ConnectionError: If connection fails
            ValueError: If authentication fails (invalid token)
        """
        if self._is_connected and self._is_registered:
            return True

        # Reset error state
        self._register_error = None

        # Create Socket.IO client with /skill path
        # nginx will route this to skill.js port
        self._sio = socketio.Client(
            reconnection=self.auto_reconnect,
            logger=False,
            engineio_logger=False
        )

        # Set up event handlers
        @self._sio.event
        def connect():
            print('[SkillWS] Connected to server')
            self._is_connected = True
            # Send register event
            self._sio.emit('register', {'private_token': self.private_token})

        @self._sio.event
        def disconnect():
            print('[SkillWS] Disconnected from server')
            self._is_connected = False
            self._is_registered = False
            self._user_id = None

        @self._sio.on('register')
        def on_register(data):
            print(f'[SkillWS] Register response: {data}')
            if data and data.get('code') == 0:
                self._is_registered = True
                self._user_id = data.get('userId')
                print(f'[SkillWS] Registered successfully, userId: {self._user_id}')
            else:
                error_msg = data.get('msg', 'unknown error') if data else 'unknown error'
                print(f'[SkillWS] Registration failed: {data}')
                self._is_registered = False
                self._register_error = error_msg  # Store error for connect() to raise

        @self._sio.on('msg')
        def on_msg(data):
            print(f'[SkillWS] Message received: {data}')
            # Add to queue for listen() pattern
            self._message_queue.put(data)
            # Call callback if set
            if self.on_message:
                try:
                    self.on_message(data)
                except Exception as e:
                    print(f'[SkillWS] Error in on_message callback: {e}')

        @self._sio.on('message')
        def on_message(data):
            """Handle generic 'message' events."""
            print(f'[SkillWS] Generic message received: {data}')
            self._message_queue.put(data)
            if self.on_message:
                try:
                    self.on_message(data)
                except Exception as e:
                    print(f'[SkillWS] Error in on_message callback: {e}')

        # Connect with /skill path
        try:
            socket_path = '/skill'
            print(f'[SkillWS] Connecting to {self.chat_url} with path {socket_path}')
            self._sio.connect(
                self.chat_url,
                socketio_path=socket_path,
                transports=['websocket', 'polling'],
                wait_timeout=timeout
            )

            # Wait for registration to complete
            start_time = time.time()
            while not self._is_registered and self._register_error is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            # Check for registration error
            if self._register_error:
                raise ValueError(f"Authentication failed: {self._register_error}")

            if not self._is_registered:
                raise ConnectionError("Registration timed out")

            return True

        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self._sio:
            try:
                self._sio.disconnect()
            except Exception:
                pass
            self._sio = None
        self._is_connected = False
        self._is_registered = False
        self._user_id = None
        self._register_error = None

    def listen(self, timeout: Optional[float] = None) -> Any:
        """
        Generator that yields messages as they arrive.

        Args:
            timeout: Max time to wait for each message (None = block forever)

        Yields:
            Message dict

        Example:
            for msg in ws_client.listen(timeout=60):
                print(f"Got: {msg}")
                if msg.get('type') == 'done':
                    break
        """
        while self._is_connected:
            try:
                msg = self._message_queue.get(timeout=timeout or 1.0)
                yield msg
            except Empty:
                if timeout is not None:
                    return
                continue

    def listen_blocking(self):
        """
        Start blocking message loop.

        Requires on_message callback to be set for handling messages.
        """
        if not self.on_message:
            raise ValueError("on_message callback must be set before listen_blocking()")

        while self._is_connected:
            try:
                self._sio.wait(1.0)
            except Exception:
                if not self._is_connected:
                    break

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False


# Example usage
if __name__ == "__main__":
    import os
    import sys
    import time

    # Get token from environment or use placeholder
    token = os.environ.get("OCTOPIE_PRIVATE_TOKEN", "your-token-here")

    if token == "your-token-here":
        print("Please set OCTOPIE_PRIVATE_TOKEN environment variable")
        print("Get your token at: https://www.octopie.ai -> Account Settings -> Generate Private Token")
        exit(1)

    # Parse command line args
    use_websocket = "--ws" in sys.argv or "--websocket" in sys.argv

    if use_websocket:
        # ========== WebSocket Example ==========
        print("=== WebSocket Mode ===")
        print("Connecting to skill WebSocket server...")

        try:
            # Using context manager for automatic cleanup
            with SkillWebSocketClient(private_token=token) as ws_client:
                print(f"Connected! User ID: {ws_client.user_id}")
                print("Listening for messages (press Ctrl+C to exit)...\n")

                # Method 1: Using generator pattern
                for msg in ws_client.listen():
                    print(f"Received message: {json.dumps(msg, indent=2)}")

        except KeyboardInterrupt:
            print("\nDisconnected by user")
        except Exception as e:
            print(f"Error: {e}")

    else:
        # ========== REST API Example ==========
        print("=== REST API Mode ===")
        print("(Use --ws or --websocket flag for WebSocket mode)\n")

        client = OctopieClient(private_token=token)

        # Example: Send message to AI for requirement clarification
        print("Sending message to AI...")
        response = client.send_msg_to_ai(
            msg="I'm looking for a partner for a machine learning project"
        )
        sessionId = response.get("sessionId")
        lastMsgId = response.get("msgId")
        print(f"Session ID: {sessionId}")
        print(f"Message ID: {lastMsgId}")

        # Example: Pull AI messages AFTER your sent message
        if sessionId and lastMsgId:
            print("\nWaiting for AI response...")
            time.sleep(15)

            result = client.pull_ai_resp_msg(sessionId=sessionId, fromMsgId=lastMsgId)

            if result.get("msg"):
                ai_msg = result["msg"]
                print(f"AI responds: {ai_msg['content']}")
                if ai_msg.get("requirementClarified") == 1:
                    print("Requirements clarified! Ready for matching.")
            else:
                print("No AI response yet (still processing)")
