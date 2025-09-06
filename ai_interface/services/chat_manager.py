"""Chat Manager Service

Manages chat sessions, storage, and history in JSON format.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    message_id: str = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())


@dataclass
class ChatSession:
    """Represents a complete chat session."""
    session_id: str
    title: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str
    
    def __post_init__(self):
        if not self.messages:
            self.messages = []


class ChatManager:
    """Manages chat sessions and storage."""
    
    def __init__(self, chat_folder: str = None):
        """Initialize the chat manager.
        
        Args:
            chat_folder: Path to the chat storage folder. Defaults to ai_interface/chats
        """
        if chat_folder is None:
            # Default to chats folder in ai_interface directory
            ai_interface_dir = os.path.dirname(os.path.dirname(__file__))
            chat_folder = os.path.join(ai_interface_dir, "chats")
        
        self.chat_folder = Path(chat_folder)
        self.chat_folder.mkdir(exist_ok=True)
        
        self.current_session: Optional[ChatSession] = None
        self._sessions_cache: Dict[str, ChatSession] = {}
    
    def create_new_chat(self, title: str = None) -> ChatSession:
        """Create a new chat session.
        
        Args:
            title: Optional title for the chat. If None, generates from first message.
            
        Returns:
            New ChatSession instance
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        if title is None:
            title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        session = ChatSession(
            session_id=session_id,
            title=title,
            messages=[],
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.current_session = session
        self._sessions_cache[session_id] = session
        self._save_session(session)
        
        return session
    
    def add_message(self, role: str, content: str, session_id: str = None) -> ChatMessage:
        """Add a message to the current or specified chat session.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            session_id: Optional session ID. Uses current session if None.
            
        Returns:
            Created ChatMessage instance
        """
        if session_id:
            session = self.get_session(session_id)
        else:
            session = self.current_session
            
        if not session:
            # Create new session if none exists
            session = self.create_new_chat()
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now().isoformat()
        
        # Update title based on first user message if it's a generic title
        if (len(session.messages) == 1 and role == 'user' and 
            session.title.startswith('Chat ')):
            # Generate title from first 50 characters of first message
            session.title = content[:50] + ('...' if len(content) > 50 else '')
        
        self._save_session(session)
        return message
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            ChatSession instance or None if not found
        """
        if session_id in self._sessions_cache:
            return self._sessions_cache[session_id]
        
        session_file = self.chat_folder / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert message dicts back to ChatMessage objects
                messages = [ChatMessage(**msg) for msg in data.get('messages', [])]
                
                session = ChatSession(
                    session_id=data['session_id'],
                    title=data['title'],
                    messages=messages,
                    created_at=data['created_at'],
                    updated_at=data['updated_at']
                )
                
                self._sessions_cache[session_id] = session
                return session
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading session {session_id}: {e}")
                return None
        
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all chat sessions with basic info.
        
        Returns:
            List of session info dictionaries
        """
        sessions = []
        
        for session_file in self.chat_folder.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sessions.append({
                    'session_id': data['session_id'],
                    'title': data['title'],
                    'created_at': data['created_at'],
                    'updated_at': data['updated_at'],
                    'message_count': len(data.get('messages', []))
                })
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error reading session file {session_file}: {e}")
                continue
        
        # Sort by updated_at descending (most recent first)
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        session_file = self.chat_folder / f"{session_id}.json"
        
        try:
            if session_file.exists():
                session_file.unlink()
            
            # Remove from cache
            if session_id in self._sessions_cache:
                del self._sessions_cache[session_id]
            
            # Clear current session if it was deleted
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            
            return True
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def set_current_session(self, session_id: str) -> bool:
        """Set the current active session.
        
        Args:
            session_id: Session ID to set as current
            
        Returns:
            True if set successfully, False if session not found
        """
        session = self.get_session(session_id)
        if session:
            self.current_session = session
            return True
        return False
    
    def get_conversation_context(self, session_id: str = None, max_messages: int = 20) -> List[Dict[str, str]]:
        """Get conversation context for AI processing.
        
        Args:
            session_id: Optional session ID. Uses current session if None.
            max_messages: Maximum number of recent messages to include
            
        Returns:
            List of message dictionaries for AI context
        """
        if session_id:
            session = self.get_session(session_id)
        else:
            session = self.current_session
        
        if not session or not session.messages:
            return []
        
        # Get recent messages (limit to max_messages)
        recent_messages = session.messages[-max_messages:] if len(session.messages) > max_messages else session.messages
        
        # Convert to format expected by AI
        context = []
        for msg in recent_messages:
            context.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return context
    
    def _save_session(self, session: ChatSession) -> bool:
        """Save a session to disk.
        
        Args:
            session: ChatSession to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        session_file = self.chat_folder / f"{session.session_id}.json"
        
        try:
            # Convert session to dict, handling ChatMessage objects
            session_dict = asdict(session)
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving session {session.session_id}: {e}")
            return False
    
    def export_session(self, session_id: str, export_path: str) -> bool:
        """Export a session to a specified path.
        
        Args:
            session_id: Session ID to export
            export_path: Path to export the session to
            
        Returns:
            True if exported successfully, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            session_dict = asdict(session)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error exporting session {session_id}: {e}")
            return False