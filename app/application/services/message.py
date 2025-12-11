"""Message service placeholder. Business logic that orchestrates messages to users."""


class MessageService:
    def send_message(self, to_user_id: str, payload: dict):
        """Send a message to a user (TODO: adapt to actual delivery impl)."""
        raise NotImplementedError()
