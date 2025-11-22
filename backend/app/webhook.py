import os
import hmac
import hashlib
from fastapi import APIRouter, Request, Header, HTTPException
from .tasks import process_pr_event_task

router = APIRouter()

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "devsecret")


def verify_github_signature(secret, payload_body, signature_header):
    if not signature_header:
        return False

    try:
        sha_name, signature = signature_header.split("=")
    except ValueError:
        return False

    if sha_name != "sha256":
        return False

    mac = hmac.new(secret.encode(), msg=payload_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    # Read raw body
    body = await request.body()

    # Verify signature
    if not verify_github_signature(GITHUB_WEBHOOK_SECRET, body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    payload = await request.json()

    # Handle PR events
    if x_github_event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            process_pr_event_task.delay(payload)

    return {"ok": True}
