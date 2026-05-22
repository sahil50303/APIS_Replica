import os
import secrets
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API Replication Server",
    description="FastAPI replication system storing data in Supabase via Python SDK.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Supabase Python Client Initialization
# ---------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = None

if not SUPABASE_URL or not SUPABASE_KEY or "your-project-id" in SUPABASE_URL:
    print("WARNING: SUPABASE_URL and/or SUPABASE_KEY are not configured properly in your .env file.")
else:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase Python SDK Client.")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Supabase Client: {e}")

def get_supabase_client():
    if not supabase:
        raise HTTPException(
            status_code=500,
            detail="Supabase Client is not initialized. Please configure SUPABASE_URL and SUPABASE_KEY in your .env file."
        )
    return supabase

# ---------------------------------------------------------
# Helper Sanitizers (Output ISO Formatted Strings for DB)
# ---------------------------------------------------------
def parse_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str or str(date_str).strip() == "" or str(date_str).lower() == "null":
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return None

def parse_time(time_str: Optional[str]) -> Optional[str]:
    if not time_str or str(time_str).strip() == "" or str(time_str).lower() == "null":
        return None
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(str(time_str).strip(), fmt).time().isoformat()
        except ValueError:
            continue
    return None

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class PurposeItem(BaseModel):
    yojna_id: Optional[str] = None
    qty: Optional[str] = None
    amount: Optional[float] = 0.0
    bhojan_date: Optional[str] = ""

class AnnouncementPayload(BaseModel):
    annoucePurposeList: List[PurposeItem] = []
    ashri: Optional[str] = None
    ashri_oth: Optional[str] = None
    announcer_name: Optional[str] = None
    announce_amount: Optional[float] = 0.0
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    ph_no: Optional[int] = 0
    mob_no: str = Field(..., min_length=1, description="Mobile number is mandatory")
    announce_through: Optional[str] = None
    announce_date: Optional[str] = None
    announce_time: Optional[str] = None
    std_code: Optional[int] = 0
    email_id: Optional[str] = None
    purpose: Optional[int] = 0
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    completed: Optional[int] = 0
    remark1: Optional[str] = None
    first_remark: Optional[str] = None
    second_remark: Optional[str] = None
    third_remark: Optional[str] = None
    city_code: Optional[str] = None
    district_code: Optional[str] = None
    state_code: Optional[str] = None
    remark2: Optional[str] = None
    channel_code: Optional[int] = 0
    pandit_code: Optional[int] = 0
    bhag_city_code: Optional[int] = 0
    user_name: Optional[str] = None
    emp_code: Optional[int] = 0
    live: Optional[str] = None
    ash_event_id: Optional[str] = None
    event_name: Optional[str] = None
    user_id: Optional[str] = None
    cash_pickup: Optional[str] = None
    other_type: Optional[int] = 0
    currency_id: Optional[str] = None
    cause_id: Optional[int] = 0
    ngcode: Optional[str] = None
    data_flag: str = Field(..., min_length=1, description="Data flag is mandatory")
    fy_id: Optional[str] = None
    dmobilewhatsapp1: Optional[str] = None
    aadhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    pincode_code: Optional[str] = None
    country_code: Optional[str] = None
    pincode: Optional[str] = None

class CreateKeyRequest(BaseModel):
    key_name: str

# ---------------------------------------------------------
# Security Dependency
# ---------------------------------------------------------
def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    client: Client = Depends(get_supabase_client)
):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. X-API-Key header is missing."
        )
    
    try:
        res = client.table("api_keys").select("id, key_name").eq("key_value", x_api_key).eq("is_active", True).execute()
        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API Key."
            )
        return {"id": res.data[0]["id"], "name": res.data[0]["key_name"]}
    except Exception as e:
        err_msg = str(e)
        if "relation" in err_msg and "does not exist" in err_msg:
            raise HTTPException(
                status_code=500,
                detail="Database tables are missing. Please execute schema.sql in your Supabase SQL Editor first."
            )
        raise HTTPException(status_code=500, detail=f"Supabase connection error: {err_msg}")

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

# Replicated API POST endpoint matching client URL path
@app.post("/api/nssapi/ashram/InsertAnnounceCreation")
async def insert_announce_creation(
    payload: AnnouncementPayload,
    api_key: dict = Depends(verify_api_key),
    client: Client = Depends(get_supabase_client)
):
    try:
        # 1. Prepare parent Announcement record dictionary
        ann_data = {
            "ashri": payload.ashri,
            "ashri_oth": payload.ashri_oth,
            "announcer_name": payload.announcer_name,
            "announce_amount": payload.announce_amount,
            "address1": payload.address1,
            "address2": payload.address2,
            "address3": payload.address3,
            "ph_no": payload.ph_no if payload.ph_no != 0 else None,
            "mob_no": payload.mob_no,
            "announce_through": payload.announce_through,
            "announce_date": parse_date(payload.announce_date),
            "announce_time": parse_time(payload.announce_time),
            "std_code": payload.std_code,
            "email_id": payload.email_id,
            "purpose": payload.purpose,
            "due_date": parse_date(payload.due_date),
            "due_time": payload.due_time,
            "completed": payload.completed,
            "remark1": payload.remark1,
            "first_remark": payload.first_remark,
            "second_remark": payload.second_remark,
            "third_remark": payload.third_remark,
            "city_code": payload.city_code,
            "district_code": payload.district_code,
            "state_code": payload.state_code,
            "remark2": payload.remark2,
            "channel_code": payload.channel_code,
            "pandit_code": payload.pandit_code,
            "bhag_city_code": payload.bhag_city_code,
            "user_name": payload.user_name,
            "emp_code": payload.emp_code,
            "live": payload.live,
            "ash_event_id": payload.ash_event_id,
            "event_name": payload.event_name,
            "user_id": payload.user_id,
            "cash_pickup": payload.cash_pickup,
            "other_type": payload.other_type,
            "currency_id": payload.currency_id,
            "cause_id": payload.cause_id,
            "ngcode": payload.ngcode,
            "data_flag": payload.data_flag,
            "fy_id": payload.fy_id,
            "dmobilewhatsapp1": payload.dmobilewhatsapp1,
            "aadhar_number": payload.aadhar_number,
            "pan_number": payload.pan_number,
            "pincode_code": payload.pincode_code,
            "country_code": payload.country_code,
            "pincode": payload.pincode
        }
        
        # Insert announcement
        res_ann = client.table("announcements").insert(ann_data).execute()
        if not res_ann.data:
            raise Exception("Failed to save announcement details in Supabase.")
            
        announcement_id = res_ann.data[0]["id"]
        
        # 2. Map purposes to list of dictionaries
        purposes_to_insert = []
        for item in payload.annoucePurposeList:
            purposes_to_insert.append({
                "announcement_id": announcement_id,
                "yojna_id": item.yojna_id,
                "qty": item.qty,
                "amount": item.amount,
                "bhojan_date": item.bhojan_date
            })
            
        if purposes_to_insert:
            client.table("announcement_purposes").insert(purposes_to_insert).execute()
            
        # 3. Format response to exactly match client's output
        return {
            "masterDetails": [
                {
                    "code": float(announcement_id),
                    "msg": f"Announce Id:{announcement_id} created Successfully",
                    "status": "success"
                }
            ]
        }
                
    except Exception as e:
        err_msg = str(e)
        if "relation" in err_msg and "does not exist" in err_msg:
            raise HTTPException(
                status_code=500,
                detail="Database schema is missing. Please run schema.sql in Supabase SQL editor."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Replication failed: {err_msg}"
        )

# ---------------------------------------------------------
# Dashboard & Key Management API
# ---------------------------------------------------------

# Create a new API Key
@app.post("/api/keys")
async def create_api_key(
    req: CreateKeyRequest,
    client: Client = Depends(get_supabase_client)
):
    # Generates a premium key prefixed with "NSS-" and a secure token
    new_key = f"NSS-{secrets.token_hex(16).upper()}"
    try:
        res = client.table("api_keys").insert({
            "key_name": req.key_name,
            "key_value": new_key
        }).execute()
        row = res.data[0]
        return {
            "id": str(row["id"]),
            "key_name": row["key_name"],
            "key_value": new_key,
            "created_at": row["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")

# List all active keys
@app.get("/api/keys")
async def list_api_keys(client: Client = Depends(get_supabase_client)):
    try:
        res = client.table("api_keys").select("id, key_name, key_value, created_at").eq("is_active", True).order("created_at", desc=True).execute()
        keys = []
        for row in res.data:
            keys.append({
                "id": str(row["id"]),
                "key_name": row["key_name"],
                "key_value": f"{row['key_value'][:6]}...{row['key_value'][-4:]}", # Mask for safety
                "created_at": row["created_at"]
            })
        return keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list keys: {str(e)}")

# Delete (deactivate) an API key
@app.delete("/api/keys/{key_id}")
async def delete_api_key(
    key_id: str,
    client: Client = Depends(get_supabase_client)
):
    try:
        client.table("api_keys").update({"is_active": False}).eq("id", key_id).execute()
        return {"status": "success", "message": "API key revoked successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete key: {str(e)}")

# Get all replicated records
@app.get("/api/announcements")
async def get_replicated_announcements(client: Client = Depends(get_supabase_client)):
    try:
        # Fetch announcements and their related purposes in a single nested resource select query
        res = client.table("announcements").select(
            "id, announcer_name, announce_amount, mob_no, created_at, purposes:announcement_purposes(yojna_id, qty, amount, bhojan_date)"
        ).order("created_at", desc=True).limit(50).execute()
        
        results = []
        for ann in res.data:
            purposes = []
            for p in ann.get("purposes", []):
                purposes.append({
                    "yojna_id": p["yojna_id"],
                    "qty": p["qty"],
                    "amount": float(p["amount"]) if p["amount"] is not None else 0.0,
                    "bhojan_date": p["bhojan_date"]
                })
            
            results.append({
                "id": ann["id"],
                "announcer_name": ann["announcer_name"],
                "announce_amount": float(ann["announce_amount"]) if ann["announce_amount"] is not None else 0.0,
                "mob_no": ann["mob_no"],
                "created_at": ann["created_at"],
                "purposes": purposes
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load records: {str(e)}")

# Redirect root path to serve index.html directly
@app.get("/")
async def read_index():
    return FileResponse("public/index.html")

# Serves other public files
app.mount("/", StaticFiles(directory="public"), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=True)
