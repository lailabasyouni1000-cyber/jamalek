import os
import sys
import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.apps import App
from google.genai import types

# Add project root to sys.path so we can import properly
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load environment variables
load_dotenv()

# Imports for MCP toolset
from google.adk.tools import McpToolset
from mcp import StdioServerParameters

# Define structured output schema
class DupeOption(BaseModel):
    brand: str = Field(description="The brand of the dupe product")
    name: str = Field(description="The name of the dupe product")
    price: str = Field(description="Approximate price of the dupe")
    key_shared_ingredients: List[str] = Field(description="Key active/hydrating ingredients shared with the original")
    why_it_works: str = Field(description="Explanation of what makes this dupe comparable to the original")

class ProductResearcherOutput(BaseModel):
    original_product: Optional[str] = Field(description="Name of the original product researched, if applicable")
    original_price: Optional[str] = Field(description="Price of the original product, if applicable")
    three_dupes: List[DupeOption] = Field(description="Exactly three affordable dupes")
    conflict_warning: Optional[str] = Field(description="Details of any ingredient conflicts (e.g., Vitamin C + Retinol), or null if none")

# Setup MCP Toolset to connect to our local mcp_server.py dynamically
project_root = Path(__file__).resolve().parent.parent
python_executable = sys.executable

mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command=python_executable,
        args=[str(project_root / "mcp_server.py")]
    )
)

# Load SKILL.md for this agent
skill_path = Path(__file__).resolve().parent.parent / "skills" / "product_researcher.md"
skill_content = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""

# Define Product Researcher Agent with MCP tools
ProductResearcherAgent = Agent(
    name="ProductResearcherAgent",
    description="Jamalak's product researcher agent.",
    model="gemini-2.5-flash",
    instruction=(
        skill_content + "\n\n" +
        "You are Jamalak's product researcher. You find affordable dupes for expensive beauty products across "
        "both skincare and makeup. You check whether ingredients in two products conflict with each other such "
        "as niacinamide and vitamin C, retinol and AHAs, or benzoyl peroxide and retinol. You check whether a product "
        "is suitable for a given skin type. You always include approximate prices and explain what makes the dupe "
        "comparable to the original. You handle 3 request types: (a) find dupes for a named product, (b) check "
        "ingredient conflict between two products, and (c) check product suitability for a skin type.\n"
        "CRITICAL: You MUST always query the product database using the provided tools (like search_products, find_dupes, "
        "and check_skin_compatibility) first to retrieve real product recommendations before using your own static knowledge."
    ),
    tools=[mcp_toolset],
    output_schema=ProductResearcherOutput
)

# Export as root_agent so ADK CLI can run/load it
root_agent = ProductResearcherAgent

async def test_agent():
    # Setup standard ADK Runner components for testing
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
    from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
    
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    app = App(name="ProductResearcherTest", root_agent=root_agent)
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service
    )
    
    session = await session_service.create_session(app_name="ProductResearcherTest", user_id="test_user")
    
    # This test queries a product in our database (B-Hydra which has Ordinary HA 2% + B5 as dupe in products.json)
    test_msg = "Find me a dupe for the Drunk Elephant B-Hydra Intensive Hydration Serum, $48"
    print(f"Testing ProductResearcherAgent with query:\n{test_msg}\n")
    
    content = types.Content(role="user", parts=[types.Part(text=test_msg)])
    
    # Run the agent invocation
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                print(f"[{event.author}]: {text}")
                
    await runner.close()

if __name__ == "__main__":
    asyncio.run(test_agent())
