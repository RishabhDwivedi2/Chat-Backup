# app/utils/chat_utils.py

from typing import Optional
import re
from datetime import datetime

def generate_conversation_title(first_message: str) -> str:
    """Generate a title from the first message"""
    words = first_message.split()
    title = ' '.join(words[:6])  # Take first 6 words
    return f"{title}..." if len(words) > 6 else title

def format_chat_timestamp(timestamp: datetime) -> str:
    """Format timestamp for chat display."""
    now = datetime.utcnow()
    diff = now - timestamp

    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
    elif diff.days == 1:
        return "Yesterday"
    else:
        return timestamp.strftime("%b %d, %Y")
