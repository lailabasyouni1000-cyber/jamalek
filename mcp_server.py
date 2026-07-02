import json
import os
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("Jamalak Product Database")

PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "data", "products.json")

def load_products():
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

@mcp.tool()
def search_products(query: str) -> str:
    """Search products in the database by name, brand, category, or ingredients."""
    try:
        products = load_products()
        results = []
        q = query.lower()
        for p in products:
            fullname = f"{p['brand']} {p['name']}".lower()
            if (q in p["name"].lower() or 
                p["name"].lower() in q or
                q in p["brand"].lower() or 
                p["brand"].lower() in q or
                q in fullname or
                fullname in q or
                q in p["category"].lower() or 
                any(q in ing.lower() or ing.lower() in q for ing in p["key_ingredients"])):
                results.append(p)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def find_dupes(product_name: str) -> str:
    """Find affordable dupes in the database for a given product by its name or brand."""
    try:
        products = load_products()
        original = None
        q = product_name.lower()
        
        # Robust exact/soft matching in both directions
        for p in products:
            fullname = f"{p['brand']} {p['name']}".lower()
            name = p["name"].lower()
            if q == name or q == fullname or q in name or name in q or q in fullname or fullname in q:
                original = p
                break
                
        if not original:
            return json.dumps({"error": f"Product '{product_name}' not found in database"}, indent=2)
            
        # Find products that are dupes for this original product's ID
        dupes = []
        for p in products:
            if p["dupe_for"] == str(original["id"]):
                dupes.append(p)
                
        return json.dumps({
            "original_product": original,
            "dupes": dupes
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def check_skin_compatibility(product_name: str, skin_type: str) -> str:
    """Check if a product in the database is suitable for a given skin type (dry, oily, combination, normal, sensitive)."""
    try:
        products = load_products()
        product = None
        q = product_name.lower()
        
        # Robust exact/soft matching in both directions
        for p in products:
            fullname = f"{p['brand']} {p['name']}".lower()
            name = p["name"].lower()
            if q == name or q == fullname or q in name or name in q or q in fullname or fullname in q:
                product = p
                break
                
        if not product:
            return json.dumps({"error": f"Product '{product_name}' not found in database"}, indent=2)
            
        skin_type_lower = skin_type.lower()
        is_suitable = skin_type_lower in [st.lower() for st in product["skin_type_suitability"]]
        
        return json.dumps({
            "product": f"{product['brand']} {product['name']}",
            "skin_type": skin_type,
            "suitable": is_suitable,
            "suitable_types": product["skin_type_suitability"]
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run()
