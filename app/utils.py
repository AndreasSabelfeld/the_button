from app import supabase

def get_total_presses() -> int:
    """Returns the sum of all presses."""
    result = supabase.table("users").select("presses").execute()
    total = sum([r["presses"] for r in result.data])
    return total