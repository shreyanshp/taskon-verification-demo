from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="TaskOn Verification API Demo",
    description="A demo API for TaskOn task verification integration",
    version="1.0.0",
)

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class VerificationResponse(BaseModel):
    result: dict

RSS_FEED_URL = "https://zapier.com/engine/rss/12535328/fr"

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Email in RSS Feed",
    description="Check if the provided email exists in the RSS feed.",
)
async def verify_email(
    email: str = Query(..., description="The email of the user.")
) -> VerificationResponse:
    # Check if the input is blank or contains only whitespace
    if not email.strip():
        return VerificationResponse(
            result={
                "isValid": False,
                "redirectURL": "https://www.freerogernow.org/bitcoincom",
            }
        )

    async with httpx.AsyncClient() as client:
        try:
            # Call the RSS feed API using HTTP GET
            response = await client.get(RSS_FEED_URL)

            # Check if the RSS feed API request was successful
            if response.status_code != 200:
                return VerificationResponse(
                    result={
                        "isValid": False,
                        "redirectURL": "https://www.freerogernow.org/bitcoincom",
                    }
                )

            # Check if the email exists in the response content
            rss_content = response.text
            if email in rss_content:
                return VerificationResponse(result={"isValid": True})
            else:
                return VerificationResponse(
                    result={
                        "isValid": False,
                        "redirectURL": "https://www.freerogernow.org/bitcoincom",
                    }
                )

        except httpx.RequestError:
            return VerificationResponse(
                result={
                    "isValid": False,
                    "redirectURL": "https://www.freerogernow.org/bitcoincom",
                }
            )


@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
