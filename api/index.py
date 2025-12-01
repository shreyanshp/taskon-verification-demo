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
    "9707ddf8-00d8-4c5a-8a0f-1cee452142b2",
    "01872437-7726-45b9-a37a-9fbb10317c25",
    "020d4811-d605-4be6-928a-718af065aa8e",
    "08d413c4-684d-4fe1-8677-a0b1227c64c2",
    "0ba927fa-67e7-4e80-9db8-14a31718ab24",
    "11923043-9615-4cb1-8e0e-3df70c18a367",
    "1de8cfa1-59e2-4ed5-adcb-5e954c22617e",
    "21d6c5d5-6d33-4d44-b8a4-8c88a2e0b587",
    "241efc1b-9dc8-4e4b-bd81-5ee0b94968d3",
    "25f37bd5-8d8a-48b1-af70-9cd031b4e0e7",
    "260195d2-0597-4dbe-921b-437ba4c81602",
    "2a9806c2-d881-4c59-abbd-e03e4609a84c",
    "2d5eee4f-25b5-4861-9ec5-bd2b1bead3c6",
    "31859b40-2f9a-44a6-82da-d26dbad2a29a",
    "40edf094-9023-454e-afea-f2541615dfd1",
    "41f6b465-df04-4de7-8519-26070e67df30",
    "4522fa03-85d7-49f2-b033-5a1f8edda95b",
    "4cc09f03-9f19-49b8-ac33-91ece08c2195",
    "540d0dab-b1c0-4bb8-b376-b72994607bf1",
    "556d4c21-b85b-4f75-93d8-3ba2fa7d3e95",
    "5e940848-5843-4ec5-b4bd-a61c72f81616",
    "6953e06a-e205-4650-80a5-1f3aca2c3854",
    "6d4759e2-b8cb-475a-afc6-4527a3d032f9",
    "729be3a8-5c2c-411c-93f2-3051ff99a519",
    "786a16ed-98a2-41ac-be76-9e1383ff5e2e",
    "8de53844-810e-4898-b94e-cf2a2eaf6716",
    "8e3b98aa-5242-4c12-ae86-f245d7294375",
    "93293e54-3079-4aa7-a4c9-48bde2759e0c",
    "9398fade-a3a9-4501-b169-f6d1a5a9d147",
    "a2a719f3-d7e4-4e5d-b97a-9430beac7a63",
    "a36ddc7d-16e6-4ed8-a47d-0ca87c57eacd",
    "a5e2f772-4363-4a5f-99f0-8d423a224ce9",
    "aa2d45a8-b886-4e36-9a40-0ab52f8507f8",
    "acdf8883-ad60-41fc-8d50-39e5b3b32ee1",
    "b00f039c-218c-4fc5-8209-fe38000597af",
    "b7aa8d2a-397a-4a16-ba23-d5f11b69b526",
    "baa08abe-d5c3-4a53-befe-1962d88e0a8a",
    "bb99b899-a577-4668-9f86-5a3c386e2e2e",
    "c2cda908-f5a2-4452-9ddd-9ae566bad84f",
    "c8ba2e72-12ff-40dc-84e0-27b78495cea7",
    "d1c44090-d1d6-478e-8ee8-20d456515a8f",
    "d58814db-6f6c-438b-a8f5-381b13a524f5",
    "e441050c-6fcd-4d9b-ac0f-b06df2f34b24",
    "ed3fb550-7d55-461c-b1be-eadff63b0611"
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
