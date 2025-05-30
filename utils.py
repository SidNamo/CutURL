from fastapi import Request

BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def base62_encode(num: int) -> str:
    if num == 0:
        return BASE62_CHARS[0]
    base = len(BASE62_CHARS)
    encoded = ""
    while num > 0:
        encoded = BASE62_CHARS[num % base] + encoded
        num //= base
    return encoded


def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # 여러 IP가 있는 경우 첫 번째가 원래 클라이언트
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host
