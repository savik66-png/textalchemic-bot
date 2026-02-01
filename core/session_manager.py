"""
Менеджер сессий пользователей
"""
from datetime import datetime, timedelta
from typing import Dict, Any

class SessionManager:
    """Менеджер сессий"""
    def __init__(self, session_lifetime_hours: int = 2):
        self.sessions: Dict[int, Dict[str, Any]] = {}
        self.session_lifetime = timedelta(hours=session_lifetime_hours)

    def create_session(self, user_id: int) -> None:
        """Создать новую сессию"""
        self.sessions[user_id] = {
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "step": "choose_style",
            "usage_count": 0,
            "last_original_text": "",
            "last_result": "",
            "last_style": ""
        }

    def update_activity(self, user_id: int) -> None:
        """Обновить время последней активности"""
        if user_id in self.sessions:
            self.sessions[user_id]["last_activity"] = datetime.now()

    def set_step(self, user_id: int, step: str) -> None:
        """Установить текущий шаг"""
        if user_id in self.sessions:
            self.sessions[user_id]["step"] = step
            self.update_activity(user_id)

    def set_style(self, user_id: int, style: str) -> None:
        """Установить выбранный стиль"""
        if user_id in self.sessions:
            self.sessions[user_id]["style"] = style
            self.update_activity(user_id)

    def save_text(self, user_id: int, original_text: str, result: str, style: str) -> None:
        """Сохранить текст и результат"""
        if user_id in self.sessions:
            self.sessions[user_id]["last_original_text"] = original_text
            self.sessions[user_id]["last_result"] = result
            self.sessions[user_id]["last_style"] = style
            self.sessions[user_id]["usage_count"] += 1
            self.update_activity(user_id)

    def get_session(self, user_id: int) -> Dict[str, Any]:
        """Получить сессию пользователя"""
        return self.sessions.get(user_id, {})

    def cleanup_old_sessions(self) -> int:
        """Очистить старые сессии, вернуть количество удалённых"""
        now = datetime.now()
        to_delete = []
        
        for user_id, session in self.sessions.items():
            last_activity = session.get("last_activity", session.get("created_at"))
            if now - last_activity > self.session_lifetime:
                to_delete.append(user_id)
        
        for user_id in to_delete:
            del self.sessions[user_id]
        
        return len(to_delete)

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        session = self.get_session(user_id)
        return {
            "usage_count": session.get("usage_count", 0),
            "last_activity": session.get("last_activity"),
            "session_age": str(datetime.now() - session.get("created_at", datetime.now()))
        }
