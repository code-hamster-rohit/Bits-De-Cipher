from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

username = urllib.parse.quote_plus("code_hamster_rohit")
password = urllib.parse.quote_plus("Raj@1975")

uri = f"mongodb+srv://{username}:{password}@bitsdecipher2024.fks8l.mongodb.net/?retryWrites=true&w=majority&appName=BITSDECIPHER2024"

client = MongoClient(uri, server_api=ServerApi("1"))

db = client['BITSDECIPHER2024']