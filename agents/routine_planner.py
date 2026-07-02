import os
import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.apps import App
from google.genai import types

# Load environment variables
load_dotenv()

# Define structured output schema
class RoutineStep(BaseModel):
    step_number: int = Field(description="Step number in the sequence")
    product: str = Field(description="The product name/description")
    action: str = Field(description="Action to perform (e.g., Cleanse, Apply Serum, Moisten, Makeup base)")
    wait_time: Optional[str] = Field(description="Recommended wait time before next step (e.g. 5 minutes), or null")
    rationale: str = Field(description="Rationale for why this product is applied in this sequence")

class RoutinePlannerOutput(BaseModel):
    AM_routine: List[RoutineStep] = Field(description="Sequence of steps for the morning routine")
    PM_routine: List[RoutineStep] = Field(description="Sequence of steps for the evening routine")
    three_pro_tips: List[str] = Field(description="Exactly three professional application tips")
    skip_days_warning: Optional[str] = Field(description="Warning details about specific days/products to skip or alternate (e.g., Retinol alternating), or null")

from pathlib import Path

# Load SKILL.md for this agent
skill_path = Path(__file__).resolve().parent.parent / "skills" / "routine_planner.md"
skill_content = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""

# Define Routine Planner Agent
RoutinePlannerAgent = Agent(
    name="RoutinePlannerAgent",
    description="Jamalak's routine architect agent.",
    model="gemini-2.5-flash",
    instruction=(
        skill_content + "\n\n" +
        "You are Jamalak's routine architect. You take a user's skin profile, recommended skincare products, "
        "and shade-matched makeup products and sequence them into a correct AM and PM routine. Skincare always "
        "goes thinnest to thickest. SPF is always last in AM before makeup. Retinol and AHAs are PM only. "
        "Makeup starts after skincare is fully absorbed. You explain why each product sits in its position and "
        "flag anything that should be skipped on certain days."
    ),
    output_schema=RoutinePlannerOutput
)

# Export as root_agent so ADK CLI can run/load it
root_agent = RoutinePlannerAgent

async def test_agent():
    # Setup standard ADK Runner components for testing
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
    from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
    
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    app = App(name="RoutinePlannerTest", root_agent=root_agent)
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service
    )
    
    session = await session_service.create_session(app_name="RoutinePlannerTest", user_id="test_user")
    
    test_msg = (
        "Combination oily skin, acne, hyperpigmentation. "
        "Skincare: CeraVe foaming cleanser, The Ordinary niacinamide 10%, "
        "La Roche-Posay Effaclar moisturiser, EltaMD UV Clear SPF 46, "
        "The Ordinary retinol 0.5% PM only. "
        "Makeup: Fenty Beauty Pro Filt'r 330W, NARS concealer Caramel, "
        "Charlotte Tilbury setting powder."
    )
    print(f"Testing RoutinePlannerAgent with query:\n{test_msg}\n")
    
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
