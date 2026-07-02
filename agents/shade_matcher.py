import os
import asyncio
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.apps import App
from google.genai import types

# Load environment variables
load_dotenv()

# Define the structured output schema
class FoundationOption(BaseModel):
    brand: str = Field(description="The brand of the foundation")
    shade_name: str = Field(description="The exact shade name or number")
    price_range: str = Field(description="Price category: High-end, Mid-range, or Drugstore")
    why_it_works: str = Field(description="Brief explanation of why this formula or shade suits the user")

class ConcealerOption(BaseModel):
    brand: str = Field(description="The brand of the concealer")
    shade_name: str = Field(description="The exact shade name or number")
    price_range: str = Field(description="Price category: High-end, Mid-range, or Drugstore")
    why_it_works: str = Field(description="Brief explanation of why this concealer works")

class ShadeMatcherOutput(BaseModel):
    confirmed_undertone: str = Field(description="Determined/confirmed undertone (warm, cool, or neutral)")
    confirmed_depth: str = Field(description="Determined/confirmed skin depth (fair, light, medium, tan, or deep)")
    top_3_foundations: List[FoundationOption] = Field(description="Exactly 3 foundation options: one high-end, one mid-range, one drugstore")
    top_2_concealers: List[ConcealerOption] = Field(description="Exactly 2 concealer options")
    pro_tip: str = Field(description="Pro makeup application tip related to undertone or application")

from pathlib import Path

# Load SKILL.md for this agent
skill_path = Path(__file__).resolve().parent.parent / "skills" / "shade_matcher.md"
skill_content = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""

# Define the Shade Matcher Agent
ShadeMatcherAgent = Agent(
    name="ShadeMatcherAgent",
    description="Jamalak's shade specialist agent.",
    model="gemini-2.5-flash",
    instruction=(
        skill_content + "\n\n" +
        "You are Jamalak's shade specialist. You determine a user's foundation and concealer shade based on their "
        "undertone (warm/cool/neutral) and depth (fair/light/medium/tan/deep). You always give 3 foundation options "
        "at different price points: one high-end, one mid-range, one drugstore. You name the exact brand and shade. "
        "You always confirm undertone by asking about vein color, jewelry preference, or sun reaction if not provided."
    ),
    output_schema=ShadeMatcherOutput
)

# Export as root_agent so ADK CLI can run/load it
root_agent = ShadeMatcherAgent

async def test_agent():
    # Setup standard ADK Runner components for testing
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
    from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
    
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    app = App(name="ShadeMatcherTest", root_agent=root_agent)
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service
    )
    
    session = await session_service.create_session(app_name="ShadeMatcherTest", user_id="test_user")
    
    test_msg = "Skin type: combination, concerns: acne. Undertone: warm, gold jewelry suits me and my veins look greenish. Depth: medium."
    print(f"Testing ShadeMatcherAgent with query:\n{test_msg}\n")
    
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
