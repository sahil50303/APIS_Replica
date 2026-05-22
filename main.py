# main.py
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import os
import random

load_dotenv()

app = FastAPI()

# ======================================
# SUPABASE CONFIG
# ======================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======================================
# API KEY
# ======================================

API_KEY = "MY_SECRET_API_KEY"

# ======================================
# ALL REQUIRED FIELDS
# ======================================

REQUIRED_FIELDS = [
    "annoucePurposeList",
    "ashri",
    "ashri_oth",
    "announcer_name",
    "announce_amount",
    "address1",
    "address2",
    "address3",
    "ph_no",
    "mob_no",
    "announce_through",
    "announce_date",
    "announce_time",
    "std_code",
    "email_id",
    "purpose",
    "due_date",
    "due_time",
    "completed",
    "remark1",
    "first_remark",
    "second_remark",
    "third_remark",
    "city_code",
    "district_code",
    "state_code",
    "remark2",
    "channel_code",
    "pandit_code",
    "bhag_city_code",
    "user_name",
    "emp_code",
    "live",
    "ash_event_id",
    "event_name",
    "user_id",
    "cash_pickup",
    "other_type",
    "currency_id",
    "cause_id",
    "ngcode",
    "data_flag",
    "fy_id",
    "dmobilewhatsapp1",
    "aadhar_number",
    "pan_number",
    "pincode_code",
    "country_code",
    "pincode"
]

# ======================================
# API
# ======================================

@app.post("/api/nssapi/ashram/InsertAnnounceCreation")
async def create_announce(
    payload: dict,
    APIKey: str = Header(None)
):

    # ======================================
    # API KEY VALIDATION
    # ======================================

    if APIKey != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    # ======================================
    # CHECK ALL FIELDS EXIST
    # ======================================

    missing_fields = []

    for field in REQUIRED_FIELDS:
        if field not in payload:
            missing_fields.append(field)

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Missing required fields",
                "missing_fields": missing_fields
            }
        )

    # ======================================
    # MANDATORY FIELD VALUE CHECK
    # ======================================

    if not payload.get("data_flag"):
        raise HTTPException(
            status_code=400,
            detail="data_flag is mandatory"
        )

    if not payload.get("mob_no"):
        raise HTTPException(
            status_code=400,
            detail="mob_no is mandatory"
        )

    # ======================================
    # DUPLICATE MOBILE CHECK
    # ======================================

    existing = (
        supabase.table("announce_creation")
        .select("id")
        .eq("mob_no", payload["mob_no"])
        .execute()
    )

    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=409,
            detail="Announce already exists with this mobile number"
        )

    # ======================================
    # GENERATE ANNOUNCE ID
    # ======================================

    announce_id = random.randint(100000, 999999)

    payload["announce_id"] = announce_id
    payload["created_at"] = datetime.now().isoformat()

    # ======================================
    # INSERT INTO SUPABASE
    # ======================================

    try:

        insert_response = (
            supabase.table("announce_creation")
            .insert(payload)
            .execute()
        )

        return JSONResponse(
            status_code=201,
            content={
                "masterDetails": [
                    {
                        "code": announce_id,
                        "msg": f"Announce Id:{announce_id} created Successfully",
                        "status": "success"
                    }
                ]
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ======================================
# HEALTH CHECK
# ======================================

@app.get("/")
async def health():
    return {
        "status": "running"
    }
