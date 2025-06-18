from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI(
    title="TaskOn Verification API Demo",
    description="A demo API for TaskOn task verification integration with Polygon blockchain",
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

# Free Polygon RPC endpoints
POLYGON_RPC_URLS = [
    "https://polygon-rpc.com",
    "https://rpc-mainnet.matic.network",
    "https://matic-mainnet.chainstacklabs.com"
]

async def query_polygon_blockchain(address: str) -> dict:
    """
    Query Polygon blockchain for wallet information using free RPC endpoints.
    Returns balance and transaction count.
    """
    polygon_data = {
        "balance": "0",
        "transaction_count": 0,
        "is_contract": False,
        "rpc_used": None
    }
    
    # Validate address format
    if not address.startswith('0x') or len(address) != 42:
        return {"error": "Invalid Ethereum address format"}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for rpc_url in POLYGON_RPC_URLS:
            try:
                # Prepare JSON-RPC requests
                requests = [
                    {
                        "jsonrpc": "2.0",
                        "method": "eth_getBalance",
                        "params": [address, "latest"],
                        "id": 1
                    },
                    {
                        "jsonrpc": "2.0",
                        "method": "eth_getTransactionCount",
                        "params": [address, "latest"],
                        "id": 2
                    },
                    {
                        "jsonrpc": "2.0",
                        "method": "eth_getCode",
                        "params": [address, "latest"],
                        "id": 3
                    }
                ]
                
                # Send batch request
                response = await client.post(
                    rpc_url,
                    json=requests,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Process results
                    for result in results:
                        if result["id"] == 1 and "result" in result:
                            # Convert hex balance to decimal (wei to MATIC)
                            balance_wei = int(result["result"], 16)
                            balance_matic = balance_wei / 10**18
                            polygon_data["balance"] = f"{balance_matic:.6f}"
                        
                        elif result["id"] == 2 and "result" in result:
                            # Convert hex transaction count to decimal
                            polygon_data["transaction_count"] = int(result["result"], 16)
                        
                        elif result["id"] == 3 and "result" in result:
                            # Check if address is a contract (has code)
                            code = result["result"]
                            polygon_data["is_contract"] = code != "0x"
                    
                    polygon_data["rpc_used"] = rpc_url
                    break  # Success, exit the loop
                    
            except Exception as e:
                # Try next RPC endpoint
                continue
        
        # If all RPCs failed, return error info
        if polygon_data["rpc_used"] is None:
            polygon_data["error"] = "All Polygon RPC endpoints failed"
    
    return polygon_data

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Task Completion",
    description="Verify if a user has completed the task based on their wallet address and query Polygon blockchain.",
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
                    # Query Polygon blockchain for additional verification
                    polygon_data = await query_polygon_blockchain(address)
                    
                    return VerificationResponse(result={"isValid": True})

            # If all season IDs are exhausted and no data found, return invalid
            return VerificationResponse(result={"isValid": False})

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while connecting to the external API: {e}"
            )

@app.get("/polygon/wallet/{address}")
async def get_polygon_wallet_info(address: str):
    """
    Standalone endpoint to query Polygon blockchain wallet information.
    """
    polygon_data = await query_polygon_blockchain(address)
    return {"address": address, "polygon_data": polygon_data}

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}
