from pathlib import Path
from dotenv import load_dotenv
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE, override=True)

from Controllers.auth_controller import router as auth_router
from Controllers.transaction_controller import router as transaction_router
from Controllers.otp_controller import router as otp_router
from Controllers.tuition_controller import router as tuition_router
from Controllers.payment_controller import router as payment_router
from Controllers.notification_controller import router as notification_router
from Controllers.user_controller import router as user_router
from Controllers.account_controller import router as account_router

app = FastAPI(title="iBanking Tuition Payment API")


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "success": False,
            "data": {},
            "msg": exc.detail,
            "time": int(time.time())
        },
        headers=exc.headers
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(otp_router)
app.include_router(tuition_router)
app.include_router(payment_router)
app.include_router(notification_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "message": "Backend is running."
    }