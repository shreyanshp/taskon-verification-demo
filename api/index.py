from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import csv
from io import StringIO

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
SPREADSHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vRoMTJt5nv0nkmK02vH1jhndbEWaCz3wdf12oMwJGZ7Z4ysuB5K0_zvclzTfwqx4AqTtgJ3CpXHxLZb/pub?gid=2134979020&single=true&output=csv"
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
    # Check if the input is blank
    if not address.strip():
        return VerificationResponse(result={"isValid": False})

    async with httpx.AsyncClient() as client:
        try:
            # Fetch the spreadsheet data in CSV format
            response = await client.get(SPREADSHEET_CSV_URL)

            # Check if the request was successful
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching spreadsheet data: {response.text}"
                )

            # Parse the CSV content
            csv_content = StringIO(response.text)
            csv_reader = csv.DictReader(csv_content)

            # Check if the email exists in the spreadsheet
            for row in csv_reader:
                if address in row.values():
                    return VerificationResponse(result={"isValid": True})

            return VerificationResponse(result={"isValid": False})

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while connecting to the spreadsheet: {e}"
            )

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
