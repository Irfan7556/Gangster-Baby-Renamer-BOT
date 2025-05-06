import re, os
from pymongo import MongoClient

id_pattern = re.compile(r'^.\d+$') 

API_ID = os.environ.get("API_ID", "21786970")
API_HASH = os.environ.get("API_HASH", "aa1eaa84080fdf706c5cb37a27d35e81")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7989061588:AAHKqJpCQtYvCTMbrDaaBCO9B7AsB45jW5s") 
FORCE_SUB = os.environ.get("FORCE_SUB", "KMovieHubInHindi") 

DB_NAME = os.environ.get("DB_NAME", "TensaiRenameBot")    
DB_URL = os.environ.get("DB_URL", "mongodb+srv://mohammadirfan01239:T1njoUYWxmsu1itN@cluster0.suyfipt.mongodb.net/TensaiRenameBot?retryWrites=true&w=majority&appName=Cluster0")

# MongoDB Connection Setup
client = MongoClient(DB_URL)
db = client[DB_NAME]
users_collection = db["botUsers"]  # Explicitly define the user collection

FLOOD = int(os.environ.get("FLOOD", "10"))
START_PIC = os.environ.get("START_PIC", "")
ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5944299635').split()]
PORT = os.environ.get("PORT", "8080")
