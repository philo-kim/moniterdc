"""
Supabase client wrapper for the worldview engine
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Singleton Supabase client"""

    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            cls._instance = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_SERVICE_KEY')
            )
        return cls._instance

def get_supabase() -> Client:
    """Helper function to get Supabase client"""
    return SupabaseClient.get_client()