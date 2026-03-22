import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://psbhardwaj181_db_user:MMnsjhQRFXAa3cFu@cluster0.sjrvasq.mongodb.net/emrs_dornala?retryWrites=true&w=majority"
)

DB_NAME = os.getenv("MONGODB_DB", "emrs_dornala")

client = AsyncIOMotorClient(
    MONGODB_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client[DB_NAME]
