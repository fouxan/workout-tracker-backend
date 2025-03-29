class WebSocketError(Exception):
    def __init__(self, code: int, reason: str):
        self.code = code
        self.reason = reason
