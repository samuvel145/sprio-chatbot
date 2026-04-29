import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SessionData:
    phone_number: str
    ttl_minutes: int
    max_turns: int
    chat_history: List[Dict[str, str]] = field(default_factory=list)
    last_diagnosis: Optional[Dict] = None
    request_timestamps: List[float] = field(default_factory=list)
    last_active: float = field(default_factory=time.time)

    def touch(self) -> None:
        self.last_active = time.time()

    def is_expired(self) -> bool:
        return (time.time() - self.last_active) > (self.ttl_minutes * 60)

    def add_message(self, role: str, content: str) -> None:
        self.chat_history.append({"role": role, "content": content})
        self.touch()
        max_messages = self.max_turns * 2
        if len(self.chat_history) > max_messages:
            self.chat_history = self.chat_history[-max_messages:]

    def check_rate_limit(self, rpm: int) -> bool:
        now = time.time()
        self.request_timestamps = [t for t in self.request_timestamps if (now - t) < 60]
        if len(self.request_timestamps) >= rpm:
            return False
        self.request_timestamps.append(now)
        return True


class SessionManager:
    def __init__(self, ttl_minutes: int, max_turns: int):
        self.ttl_minutes = ttl_minutes
        self.max_turns = max_turns
        self.sessions: Dict[str, SessionData] = {}

    def get_or_create(self, phone_number: str) -> SessionData:
        self.cleanup_expired()
        session = self.sessions.get(phone_number)
        if session and not session.is_expired():
            session.touch()
            return session

        session = SessionData(
            phone_number=phone_number,
            ttl_minutes=self.ttl_minutes,
            max_turns=self.max_turns,
        )
        self.sessions[phone_number] = session
        return session

    def cleanup_expired(self) -> None:
        expired = [k for k, v in self.sessions.items() if v.is_expired()]
        for key in expired:
            del self.sessions[key]
