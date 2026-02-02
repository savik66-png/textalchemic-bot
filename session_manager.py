from datetime import datetime, timedelta
from typing import Dict, Any

class SessionManager:
    """
    Простой менеджер сессий для хранения состояния пользователей.
    """
    def __init__(self, session_lifetime_hours: int = 2):
        self.sessions: Dict[int, Dict[str, Any]] = {}
        self.session_lifetime = timedelta(hours=session_lifetime_hours)

    def _cleanup_expired_sessions(self):
        """Удаляет сессии, срок которых истёк."""
        now = datetime.now()
        expired_user_ids = [
            user_id for user_id, session_data in self.sessions.items()
            if now - session_data["last_activity"] > self.session_lifetime
        ]
        for user_id in expired_user_ids:
            if user_id in self.sessions:
                del self.sessions[user_id]

    def get_or_create_session(self, user_id: int):
        """Возвращает сессию пользователя, создавая её при необходимости."""
        self._cleanup_expired_sessions() # Очищаем перед обращением
        if user_id not in self.sessions:
            self.create_session(user_id)
        return self.sessions[user_id]

    def create_session(self, user_id: int):
        """Создаёт новую сессию для пользователя."""
        self.sessions[user_id] = {
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "state": "waiting_for_text",  # Возможные состояния: waiting_for_text, waiting_for_style
            "selected_style_id": None,
            "original_text": "",
        }

    def update_session_state(self, user_id: int, state: str, **kwargs):
        """Обновляет состояние сессии."""
        session = self.get_or_create_session(user_id)
        session["last_activity"] = datetime.now()
        session["state"] = state
        for key, value in kwargs.items():
            session[key] = value

# --- Глобальный экземпляр ---
session_manager = SessionManager()