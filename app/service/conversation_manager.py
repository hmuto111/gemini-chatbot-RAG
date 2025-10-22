import json

# シングルトンインスタンスの管理
_manager_instance = None

class ConversationManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def generate_sequential_session_id(self, prefix: str = "session") -> str:
        """
        Redisのカウンターを使用してシーケンシャルIDを生成
        """
        counter_key = f"{prefix}:counter"
        session_number = self.redis_client.incr(counter_key)
        session_id = f"{prefix}:{session_number:06d}"  # session:000001
        self.redis_client.expire(session_id, 3600)  # 1時間後に期限切れ
        return session_id

    def save_conversation(self, session_id: str, conversation: dict) -> None:
        """
        ユーザーの会話をRedisに保存
        """
        key = session_id
        self.redis_client.rpush(key, json.dumps(conversation, ensure_ascii=False))

    def get_conversation(self, session_id: str) -> list[dict]:
        """
        ユーザーの会話をRedisから取得
        """
        key = session_id
        # 最新の3つの会話履歴を取得
        return [json.loads(item) for item in self.redis_client.lrange(key, -3, -1)]


def get_manager(redis_client) -> ConversationManager:
    """ChatServiceのシングルトンインスタンスを取得"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ConversationManager(redis_client)
    return _manager_instance