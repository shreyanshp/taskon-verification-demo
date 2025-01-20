from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import csv
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

# Cache to store the spreadsheet data timestamp
spreadsheet_cache = {"last_fetch_time": 0}
CACHE_DURATION = 300  # Cache duration in seconds (e.g., 5 minutes)

async def stream_and_search_csv(url: str, query: str) -> bool:
    """
    Stream the CSV content and search for the query in rows.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching spreadsheet data: {response.text}"
                )

            # Use the HTTP stream directly with the CSV reader
            response_lines = response.aiter_lines()
            csv_reader = csv.reader(response_lines)

            # Skip the header row
            headers = await response_lines.__anext__()
            csv_reader = csv.reader([headers] + list(response_lines))

            # Search for the query in the CSV rows
            async for row in csv_reader:
                if query in row:
                    return True
    return False

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

    # Check cache timestamp to avoid frequent requests
    if time.time() - spreadsheet_cache["last_fetch_time"] > CACHE_DURATION:
        spreadsheet_cache["last_fetch_time"] = time.time()

    # Stream and search the CSV
    is_valid = await stream_and_search_csv(SPREADSHEET_CSV_URL, address)
    return VerificationResponse(result={"isValid": is_valid})

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
