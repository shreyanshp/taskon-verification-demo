from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
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

API_URL = "https://neko-web.api.wallet.bitcoin.com/api/v2/quests/progresses"
SEASON_IDS = [
    "6e04d818-0c26-491a-b876-45ff15ae05f4",
    "9707ddf8-00d8-4c5a-8a0f-1cee452142b2"
]

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Task Completion",
    description="Verify if a user has completed the task based on their wallet address.",
)
async def verify_task(
    address: str,
    authorization: Optional[str] = Header(None)
) -> VerificationResponse:
    async with httpx.AsyncClient() as client:
        try:
            for season_id in SEASON_IDS:
                # Build the request URL
                url = f"{API_URL}?address={address}&seasonId={season_id}"
                response = await client.get(url)

                # Check if the request was successful
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error fetching data from external API: {response.text}"
                    )

                # Parse the response JSON
                data = response.json()

                # Check if the response data is not a blank array
                if isinstance(data, list) and len(data) > 0:
                    return VerificationResponse(result={"isValid": True})

            # If all season IDs are exhausted and no data found, return invalid
            return VerificationResponse(result={"isValid": False})

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while connecting to the external API: {e}"
            )

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
