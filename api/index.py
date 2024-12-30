from fastapi import FastAPI, HTTPException, Query
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

RSS_FEED_URL = "https://eu.jotform.com/rss/243640065431045/"

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Email in RSS Feed",
    description="Check if the provided email exists in the RSS feed.",
)
async def verify_email(
    email: str = Query(..., description="The email of the user.")
) -> VerificationResponse:
    # Check if the input is blank
    if not address.strip():
        return VerificationResponse(result={"isValid": False})

    async with httpx.AsyncClient() as client:
        try:
            # Call the RSS feed post API with the required payload
            rss_payload = {
                "passKey": "Bitcoin.com",
            }
            response = await client.post(RSS_FEED_URL, data=rss_payload)

            # Check if the RSS feed API request was successful
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching RSS feed data: {response.text}"
                )

            # Check if the email exists in the response content
            rss_content = response.text
            if email in rss_content:
                return VerificationResponse(result={"isValid": True})
            else:
                return VerificationResponse(result={"isValid": False})

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while connecting to the RSS feed API: {e}"
            )

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
