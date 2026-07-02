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
class SkinAnalysisOutput(BaseModel):
    skin_type: str = Field(description="Skin type: dry, oily, combination, normal, or sensitive")
    concerns: List[str] = Field(description="List of identified concerns (acne, hyperpigmentation, redness, dryness, aging, sensitivity)")
    ingredients_to_avoid: List[str] = Field(description="List of ingredients to avoid based on skin type, concerns, or conflicts")
    AM_routine: List[str] = Field(description="AM skincare routine, exactly 3 steps")
    PM_routine: List[str] = Field(description="PM skincare routine, exactly 3 steps")
    notes: str = Field(description="Additional specialist notes or warnings. Never give medical diagnoses.")

from pathlib import Path

# Load SKILL.md for this agent
skill_path = Path(__file__).resolve().parent.parent / "skills" / "skin_analyst.md"
skill_content = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""

# Define the Skin Specialist Agent
SkinAnalystAgent = Agent(
    name="SkinAnalystAgent",
    description="Jamalak's skin specialist agent.",
    model="gemini-2.5-flash",
    instruction=(
        skill_content + "\n\n" +
        "You are Jamalak's skin specialist. You assess skin type (dry/oily/combination/normal/sensitive), "
        "identify concerns (acne, hyperpigmentation, redness, dryness, aging, sensitivity), flag ingredient conflicts "
        "between any products the user mentions, and recommend a skincare routine. You never give medical diagnoses. "
        "Always ask about current products the user is using before recommending new ones."
    ),
    output_schema=SkinAnalysisOutput
)

# Export the agent as root_agent so that ADK CLI can run/load it
root_agent = SkinAnalystAgent

async def test_agent():
    # Setup standard ADK Runner components for testing
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
    from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
    
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    app = App(name="SkinAnalystTest", root_agent=root_agent)
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service
    )
    
    session = await session_service.create_session(app_name="SkinAnalystTest", user_id="test_user")
    
    test_msg = "I have combination skin, oily T-zone and dry cheeks. I use a vitamin C serum in the morning and retinol at night. I break out around my chin monthly."
    print(f"Testing SkinAnalystAgent with query:\n{test_msg}\n")
    
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
