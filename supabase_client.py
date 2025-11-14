from supabase import create_client
import os

# ⚠️ GANTI DENGAN PUNYAMU!
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ykqqnfbyahlvywvqlyex.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlrcXFuZmJ5YWhsdnl3dnFseWV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMTAzMjUsImV4cCI6MjA3ODY4NjMyNX0.pMLOPtUq3VAFJqIp-iXoC65lHEIConf9ucdMgLReiZs")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
