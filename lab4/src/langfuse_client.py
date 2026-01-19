import os
from langfuse import Langfuse

LF_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LF_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LF_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

lf = None

if LF_PUBLIC_KEY and LF_SECRET_KEY and LF_BASE_URL:
    lf = Langfuse(
        public_key=LF_PUBLIC_KEY,
        secret_key=LF_SECRET_KEY,
        base_url=LF_BASE_URL,
    )
