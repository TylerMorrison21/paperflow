import os
from dotenv import load_dotenv

load_dotenv()

DATALAB_API_KEY = os.environ.get("DATALAB_API_KEY", "")
MARKER_API_URL  = os.environ.get("MARKER_API_URL", "https://www.datalab.to/api/v1/marker")
CORS_ORIGINS    = os.environ.get("CORS_ORIGINS", "*")
DATA_DIR        = os.environ.get("DATA_DIR", "./data/papers")
