import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import AdmissionReviewRequest, AdmissionReviewResponse,Response, JsonPatch, JsonPatchOp
import os
import random
from app_logger import logger
app = FastAPI()

try:
    flaky = int(os.environ.get("FLAKY",0))
    if flaky < 0 or flaky > 100:
        flaky = 0
except ValueError:
    flaky = 0

@app.exception_handler(RequestValidationError)
async def _(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    content = {'status_code': 422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/health")
async def health(request: Request):
    logger.info(f"Health endpoint pinged from {request.client.host if request.client else None}")
    return {"status": "healthy"}

@app.post("/webhook", response_model_exclude_none=True)
async def webhook(request: AdmissionReviewRequest) -> AdmissionReviewResponse:

    logger.info(f"AdmissionReview request received: {request.model_dump_json()}")
    if random.randint(1,100) <= flaky:
        response = AdmissionReviewResponse(apiVersion=request.apiVersion,
                                       kind=request.kind,
                                       response=Response(uid=request.request.uid,
                                                         allowed=False))
    else:
        response = AdmissionReviewResponse(apiVersion=request.apiVersion,
                                       kind=request.kind,
                                       response=Response(uid=request.request.uid,
                                                         allowed=True,
                                                         patchType="JSONPatch",
                                                         patch=[JsonPatch(op=JsonPatchOp.Add,
                                                                         path="/metadata/labels/myMutatingWebhookLabel",
                                                                         value="mutating-webhook-was-here"),
                                                                JsonPatch(op=JsonPatchOp.Add,
                                                                         path="/metadata/labels/anotherMutatingWebhookLabel",
                                                                         value="and-also-here")]))
    logger.info(f"AdmissionReview response sent: {response.model_dump_json()}")
    return response

if __name__ == "__main__":

    env = os.environ.get("ENVIRONMENT","PROD")

    if env == "DEV":
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8080,
            reload=True
        )
    else:
        ssl_cert_file = os.environ.get("SSL_CERTFILE",None)
        ssl_key_file = os.environ.get("SSL_KEYFILE",None)

        if not ssl_cert_file or not ssl_key_file:
            logger.critical("Both SSL_CERTFILE and SSL_KEYFILE environment variables must be defined")
            exit(1)

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8443,
            ssl_certfile=ssl_cert_file,
            ssl_keyfile=ssl_key_file
        )
