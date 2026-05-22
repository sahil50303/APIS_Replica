# main.py

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client
from dotenv import load_dotenv
import os
import random

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_KEY = os.getenv("API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ==========================================
# REQUIRED FIELDS
# ==========================================

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

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def health():
    return {"status": "running"}

# ==========================================
# MAIN API
# ==========================================

@app.post("/api/nssapi/ashram/InsertAnnounceCreation")
def create_announcement(
    payload: dict,
    APIKey: str = Header(None)
):

    # ==========================================
    # API KEY CHECK
    # ==========================================

    if APIKey != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    # ==========================================
    # CHECK ALL REQUIRED FIELDS
    # ==========================================

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

    # ==========================================
    # MANDATORY VALUE CHECK
    # ==========================================

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

    # ==========================================
    # DUPLICATE MOBILE CHECK
    # ==========================================

    duplicate = (
        supabase.table("announcement_purposes")
        .select("id")
        .eq("mob_no", payload["mob_no"])
        .execute()
    )

    if duplicate.data:
        raise HTTPException(
            status_code=409,
            detail="Announcement already exists with this mobile number"
        )

    try:

        # ==========================================
        # EXTRACT FIRST PURPOSE ITEM
        # ==========================================

        purpose_list = payload.get("annoucePurposeList", [])

        first_purpose = {}

        if len(purpose_list) > 0:
            first_purpose = purpose_list[0]

        # ==========================================
        # GENERATE ANNOUNCE CODE
        # ==========================================

        announce_code = random.randint(100000, 999999)

        # ==========================================
        # INSERT INTO EXISTING TABLE
        # ==========================================

        insert_data = {
            "announcement_id": announce_code,
            "yojna_id": first_purpose.get("yojna_id"),
            "qty": first_purpose.get("qty"),
            "amount": first_purpose.get("amount"),
            "bhojan_date": first_purpose.get("bhojan_date"),
            "raw_aannounce_json": payload,
            "mob_no": payload.get("mob_no")
        }

        (
            supabase.table("announcement_purposes")
            .insert(insert_data)
            .execute()
        )

        # ==========================================
        # SUCCESS RESPONSE
        # ==========================================

        return JSONResponse(
            status_code=201,
            content={
                "masterDetails": [
                    {
                        "code": announce_code,
                        "msg": f"Announce Id:{announce_code} created Successfully",
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
    

# ==========================================
# INSERT CIT API
# ==========================================

CIT_REQUIRED_FIELDS = [
    "iCall_Information_Traits_ID",
    "iCall_Category_ID",
    "Call_Id",
    "Call_Date",
    "sInformation_Trait",
    "Dept_Id",
    "iCallReply",
    "Complete",
    "USER_ID",
    "Rec",
    "Rec_Comp",
    "Rec_User_ID",
    "Disp",
    "Disp_Comp",
    "Disp_User_ID",
    "Call",
    "Call_Comp",
    "Call_User_Id",
    "Mno1",
    "Mno2",
    "Remark1",
    "Remark2",
    "Remark3",
    "Remark4",
    "Call_Back_Date",
    "DOEF1",
    "DOEF2",
    "DOEF3",
    "DOEF4",
    "Comp_Date",
    "NgCode",
    "Comp_User_Id",
    "Scan_Files",
    "File_Name",
    "Rec_Date",
    "Disp_Date",
    "Dispatch_Id",
    "Data_Flag",
    "FY_ID",
    "crtObjectId",
    "Call_Date_Time",
    "Call_Back_Date_Time",
    "Target_Date",
    "Emp_Id",
    "EMail_Id",
    "NAME",
    "FROM_WEB",
    "Request_by",
    "Isd1",
    "Isd2",
    "Country_code1",
    "Country_Code2"
]


@app.post("/api/nssapi/ashram/InsertCIT")
def insert_cit(
    payload: dict,
    APIKey: str = Header(None)
):

    # ==========================================
    # API KEY CHECK
    # ==========================================

    if APIKey != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    # ==========================================
    # REQUIRED FIELD CHECK
    # ==========================================

    missing_fields = []

    for field in CIT_REQUIRED_FIELDS:
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

    # ==========================================
    # MANDATORY VALUE CHECK
    # ==========================================

    if not payload.get("Data_Flag"):
        raise HTTPException(
            status_code=400,
            detail="Data_Flag is mandatory"
        )

    if not payload.get("Mno1"):
        raise HTTPException(
            status_code=400,
            detail="Mno1 is mandatory"
        )

    # ==========================================
    # DUPLICATE MOBILE CHECK
    # ==========================================

    duplicate = (
        supabase.table("cit_records")
        .select("id")
        .eq("mno1", payload["Mno1"])
        .execute()
    )

    if duplicate.data:
        raise HTTPException(
            status_code=409,
            detail="CIT already exists with this mobile number"
        )

    try:

        # ==========================================
        # GENERATE CIT CODE
        # ==========================================

        cit_code = random.randint(100000, 999999)

        # ==========================================
        # INSERT DATA
        # ==========================================

        insert_data = {
            "cit_code": cit_code,
            "mno1": payload.get("Mno1"),
            "raw_cit_json": payload
        }

        (
            supabase.table("cit_records")
            .insert(insert_data)
            .execute()
        )

        # ==========================================
        # SUCCESS RESPONSE
        # ==========================================

        return JSONResponse(
            status_code=201,
            content={
                "masterDetails": [
                    {
                        "code": cit_code,
                        "msg": f"CIT Id:{cit_code} created Successfully",
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
    

from fastapi import Form
import json

# ==========================================
# RECEIPT REQUIRED FIELDS
# ==========================================

RECEIPT_REQUIRED_FIELDS = [
    "Receive_Id",
    "Receive_Head",
    "Receive_Name",
    "First_Name",
    "Mid_Name",
    "Last_Name",
    "Pan_No",
    "Ag_Form",
    "Receive_City",
    "Receive_State",
    "Receive_Address",
    "Receive_Mob",
    "Receive_PayMode",
    "Receive_Cheque",
    "Receive_Bank",
    "Receive_Currency",
    "Receive_Amount",
    "Receive_Material",
    "Receive_Prov_Tp",
    "Receive_Prov_No",
    "Receive_User_Id",
    "Receive_Remark",
    "Email_ID",
    "Bank_Charges",
    "Receive_User_Name",
    "Pending_Remark_Date",
    "Pending_Remark_Time",
    "Call_Remark",
    "Bank_Code",
    "Deposit_Bank",
    "Deposit_Date",
    "Letter_id",
    "OrderNo",
    "Announce_Id",
    "Review_Date",
    "Remark",
    "Doc_No",
    "Other_Kumbh",
    "Prov_Date",
    "Prov_Copy",
    "EID",
    "Pay_Type",
    "Proof_Type",
    "MailCode",
    "Daan_Patra_Code",
    "OTHER_TYPE",
    "Work_By",
    "PDC_CHEQUE",
    "DOB",
    "DOA",
    "Response_FromId",
    "Response_FromName",
    "Cheque_Return_Date",
    "InRMemory",
    "Receive_SDWName",
    "Receive_CareOf",
    "Receive_Add1",
    "Receive_Add2",
    "Receive_Add3",
    "Receive_District",
    "Receive_Country",
    "Receive_Pincode",
    "Receive_STD",
    "Receive_ISD",
    "Receive_Mob2",
    "Receive_Whatsapp",
    "Receive_Sandipan",
    "Receive_SMS",
    "Receive_DShri",
    "Receive_DID",
    "Person_Id",
    "Cause_Id",
    "Marit_Status",
    "Don_Id",
    "Don_Pass",
    "Data_Flag",
    "FY_ID",
    "Receive_ISD2",
    "Receive_ISD3",
    "Receive_Prnt_PayMode",
    "Cont_whatsApp",
    "Cont_Email",
    "Cont_Letter",
    "Cont_Phone",
    "Receive_Aadhar",
    "PerAdd1",
    "PerAdd2",
    "PerAdd3",
    "PerCountry_Code",
    "PerState_Code",
    "PerDistrict_Code",
    "AGFORM_REQUIRE",
    "donationPurposeList",
    "donorInstructions"
]

# ==========================================
# INSERT RECEIPT API
# ==========================================

@app.post("/erpapi/ashram/insertdata")
async def insert_receipt(
    APIKey: str = Header(None),

    Receive_Id: str = Form(...),
    Receive_Head: str = Form(...),
    Receive_Name: str = Form(...),
    First_Name: str = Form(...),
    Mid_Name: str = Form(...),
    Last_Name: str = Form(...),
    Pan_No: str = Form(...),
    Ag_Form: str = Form(...),
    Receive_City: str = Form(...),
    Receive_State: str = Form(...),
    Receive_Address: str = Form(...),
    Receive_Mob: str = Form(...),
    Receive_PayMode: str = Form(...),
    Receive_Cheque: str = Form(...),
    Receive_Bank: str = Form(...),
    Receive_Currency: str = Form(...),
    Receive_Amount: str = Form(...),
    Receive_Material: str = Form(...),
    Receive_Prov_Tp: str = Form(...),
    Receive_Prov_No: str = Form(...),
    Receive_User_Id: str = Form(...),
    Receive_Remark: str = Form(...),
    Email_ID: str = Form(...),
    Bank_Charges: str = Form(...),
    Receive_User_Name: str = Form(...),
    Pending_Remark_Date: str = Form(...),
    Pending_Remark_Time: str = Form(...),
    Call_Remark: str = Form(...),
    Bank_Code: str = Form(...),
    Deposit_Bank: str = Form(...),
    Deposit_Date: str = Form(...),
    Letter_id: str = Form(...),
    OrderNo: str = Form(...),
    Announce_Id: str = Form(...),
    Review_Date: str = Form(...),
    Remark: str = Form(...),
    Doc_No: str = Form(...),
    Other_Kumbh: str = Form(...),
    Prov_Date: str = Form(...),
    Prov_Copy: str = Form(...),
    EID: str = Form(...),
    Pay_Type: str = Form(...),
    Proof_Type: str = Form(...),
    MailCode: str = Form(...),
    Daan_Patra_Code: str = Form(...),
    OTHER_TYPE: str = Form(...),
    Work_By: str = Form(...),
    PDC_CHEQUE: str = Form(...),
    DOB: str = Form(...),
    DOA: str = Form(...),
    Response_FromId: str = Form(...),
    Response_FromName: str = Form(...),
    Cheque_Return_Date: str = Form(...),
    InRMemory: str = Form(...),
    Receive_SDWName: str = Form(...),
    Receive_CareOf: str = Form(...),
    Receive_Add1: str = Form(...),
    Receive_Add2: str = Form(...),
    Receive_Add3: str = Form(...),
    Receive_District: str = Form(...),
    Receive_Country: str = Form(...),
    Receive_Pincode: str = Form(...),
    Receive_STD: str = Form(...),
    Receive_ISD: str = Form(...),
    Receive_Mob2: str = Form(...),
    Receive_Whatsapp: str = Form(...),
    Receive_Sandipan: str = Form(...),
    Receive_SMS: str = Form(...),
    Receive_DShri: str = Form(...),
    Receive_DID: str = Form(...),
    Person_Id: str = Form(...),
    Cause_Id: str = Form(...),
    Marit_Status: str = Form(...),
    Don_Id: str = Form(...),
    Don_Pass: str = Form(...),
    Data_Flag: str = Form(...),
    FY_ID: str = Form(...),
    Receive_ISD2: str = Form(...),
    Receive_ISD3: str = Form(...),
    Receive_Prnt_PayMode: str = Form(...),
    Cont_whatsApp: str = Form(...),
    Cont_Email: str = Form(...),
    Cont_Letter: str = Form(...),
    Cont_Phone: str = Form(...),
    Receive_Aadhar: str = Form(...),
    PerAdd1: str = Form(...),
    PerAdd2: str = Form(...),
    PerAdd3: str = Form(...),
    PerCountry_Code: str = Form(...),
    PerState_Code: str = Form(...),
    PerDistrict_Code: str = Form(...),
    AGFORM_REQUIRE: str = Form(...),
    donationPurposeList: str = Form(...),
    donorInstructions: str = Form(...)
):

    # ==========================================
    # API KEY CHECK
    # ==========================================

    if APIKey != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    # ==========================================
    # MANDATORY CHECK
    # ==========================================

    if not Data_Flag:
        raise HTTPException(
            status_code=400,
            detail="Data_Flag is mandatory"
        )

    if not Receive_Mob:
        raise HTTPException(
            status_code=400,
            detail="Receive_Mob is mandatory"
        )

    # ==========================================
    # DUPLICATE MOBILE CHECK
    # ==========================================

    duplicate = (
        supabase.table("receipts_records")
        .select("id")
        .eq("receive_mob", Receive_Mob)
        .execute()
    )

    if duplicate.data:
        raise HTTPException(
            status_code=409,
            detail="Receipt already exists with this mobile number"
        )

    try:

        receipt_code = random.randint(100000, 999999)

        payload = {
            key: value
            for key, value in locals().items()
            if key not in ["APIKey", "receipt_code"]
        }

        insert_data = {
            "receipt_code": receipt_code,
            "receive_mob": Receive_Mob,
            "raw_receipt_json": payload
        }

        (
            supabase.table("receipts_records")
            .insert(insert_data)
            .execute()
        )

        return JSONResponse(
            status_code=201,
            content={
                "masterDetails": [
                    {
                        "code": receipt_code,
                        "msg": f"Receipt Id:{receipt_code} created Successfully",
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
