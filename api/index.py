from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import csv
from io import StringIO
import time

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

# Public Google Spreadsheet URL (Export in CSV format)
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1dw5zAOu6jJ9p3oBMT61THVsW8oRpjhxjJEVmlGJEr34/export?format=csv&gid=2134979020"

# Cache to store the spreadsheet data
spreadsheet_cache = {"data": None, "last_fetch_time": 0}
CACHE_DURATION = 300  # Cache duration in seconds (e.g., 5 minutes)

async def fetch_spreadsheet_data():
    """
    Fetch the spreadsheet data from Google Sheets and update the cache.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(SPREADSHEET_CSV_URL)
        if response.status_code == 200:
            spreadsheet_cache["data"] = response.text
            spreadsheet_cache["last_fetch_time"] = time.time()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error fetching spreadsheet data: {response.text}"
            )

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Email in Google Spreadsheet",
    description="Check if the provided email exists in the Google Spreadsheet.",
)
async def verify_email(
    address: str = Query(..., description="The email of the user.")
) -> VerificationResponse:
    # Validate input
    if not address.strip():
        return VerificationResponse(result={"isValid": False})

    # Fetch spreadsheet data if the cache is invalid or expired
    if (
        not spreadsheet_cache["data"]
        or time.time() - spreadsheet_cache["last_fetch_time"] > CACHE_DURATION
    ):
        await fetch_spreadsheet_data()

    # Parse the cached CSV content
    csv_content = StringIO(spreadsheet_cache["data"])
    csv_reader = csv.DictReader(csv_content)

    # Check if the email exists in the spreadsheet
    for row in csv_reader:
        if address in row.values():
            return VerificationResponse(result={"isValid": True})

    # Email not found
    return VerificationResponse(result={"isValid": False})

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
