MAX_FLOOD_RETRIES: int = 3
# Extra buffer on top of Telegram's retry_after hint to avoid tripping the limit again.
FLOOD_RETRY_BUFFER: float = 1.0
