import pandas
from dotenv import load_dotenv
import os

load_dotenv()
print("EIA key loaded:", os.getenv("EIA_API_KEY"))
