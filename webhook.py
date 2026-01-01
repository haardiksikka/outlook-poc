from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from worker_runner import process_message

app = FastAPI()

EXPECTED_CLIENT_STATE = "poc-secret-123"

@app.api_route("/webhook", methods=["GET", "POST"])
async def webhook(request: Request):
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return PlainTextResponse(validation_token, status_code=200)

    try:
        payload = await request.json()
    except Exception:
        return PlainTextResponse("OK", status_code=200)

    for notification in payload.get("value", []):
        if notification.get("clientState") != EXPECTED_CLIENT_STATE:
            return PlainTextResponse("Forbidden", status_code=403)
        message_id = notification.get("resourceData", {}).get("id")
        resource = notification.get("resource")
        process_message(message_id, resource)
    return PlainTextResponse("OK", status_code=200)
