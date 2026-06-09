import os

from dotenv import load_dotenv

load_dotenv()

MYSQL = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DB", "paldaca_db"),
        "USER": os.getenv("MYSQL_USER", "RAG"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "12345"),
        "HOST": os.getenv("MYSQL_HOST", "localhost"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
    }
}
