import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import from agents subfolder and root folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.apps import App
from google.genai import types

# Load environment variables
load_dotenv()

# Import the specialist agents
from agents.skin_analyst import SkinAnalystAgent
from agents.shade_matcher import ShadeMatcherAgent
from agents.product_researcher import ProductResearcherAgent
from agents.routine_planner import RoutinePlannerAgent

# Import profile memory helpers
from memory import (
    load_profile,
    save_profile,
    get_context_string,
    load_pending_state,
    save_pending_state,
    clear_pending_state,
    delete_profile,
    SkinProfile
)

# Global session context dictionary to maintain state across calls
session_context = {
    "skin_analysis": None,
    "shade_match": None,
    "product_research": None,
    "routine_plan": None
}

async def run_agent_helper(agent: Agent, query: str) -> str:
    """Helper function to programmatically execute a sub-agent with user profile context prepended."""
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
    from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
    
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    # Load profile context and prepend to user query
    profile = load_profile()
    context_str = get_context_string(profile)
    full_query = f"{context_str}\n\nUser request: {query}"
    
    app = App(name=agent.name, root_agent=agent)
    runner = Runner(
        app=app,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service
    )
    
    session = await session_service.create_session(app_name=agent.name, user_id="orchestrator_user")
    content = types.Content(role="user", parts=[types.Part(text=full_query)])
    
    response_text = ""
    async for event in runner.run_async(user_id="orchestrator_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                response_text += text
                
    await runner.close()
    return response_text

def format_skin_analyst(res_json: str) -> str:
    try:
        data = json.loads(res_json)
        formatted = "### Here is your skin analysis, gorgeous! ✨\n\n"
        formatted += f"- **Skin Type**: {data.get('skin_type', 'N/A')} 💖\n"
        
        concerns = data.get('concerns', [])
        if concerns:
            formatted += f"- **Concerns**: {', '.join(concerns)} 🌸\n"
            
        avoid = data.get('ingredients_to_avoid', [])
        if avoid:
            formatted += f"- **Ingredients to Avoid**: {', '.join(avoid)} 🚫\n"
            
        formatted += "\n#### ☀️ Recommended Morning (AM) Routine\n"
        for step in data.get('AM_routine', []):
            formatted += f"- {step}\n"
            
        formatted += "\n#### 🌙 Recommended Evening (PM) Routine\n"
        for step in data.get('PM_routine', []):
            formatted += f"- {step}\n"
            
        if data.get('notes'):
            formatted += f"\n*Tip: {data['notes']}*\n"
        return formatted
    except Exception:
        return res_json

def format_shade_matcher(res_json: str) -> str:
    try:
        data = json.loads(res_json)
        formatted = "### Found your perfect matches! Let's get you glowing! 💄✨\n\n"
        formatted += f"- **Confirmed Undertone**: {data.get('confirmed_undertone', 'N/A')} 🎨\n"
        formatted += f"- **Confirmed Depth**: {data.get('confirmed_depth', 'N/A')} ✨\n\n"
        
        formatted += "#### 💖 Recommended Foundations\n"
        for opt in data.get('top_3_foundations', []):
            formatted += f"- **{opt.get('brand')}** ({opt.get('shade_name')}) — *{opt.get('price_range')}*\n"
            formatted += f"  *{opt.get('why_it_works')}*\n"
            
        formatted += "\n#### 🛍️ Recommended Concealers\n"
        for opt in data.get('top_2_concealers', []):
            formatted += f"- **{opt.get('brand')}** ({opt.get('shade_name')}) — *{opt.get('price_range')}*\n"
            formatted += f"  *{opt.get('why_it_works')}*\n"
            
        if data.get('pro_tip'):
            formatted += f"\n*Pro Tip: {data['pro_tip']}*\n"
        return formatted
    except Exception:
        return res_json

def format_routine_planner(res_json: str) -> str:
    try:
        data = json.loads(res_json)
        formatted = "### Scheduled Routine Sequencing 🧴✨\n\n"
        formatted += "**☀️ Morning (AM) Routine Sequence:**\n"
        for step in data.get('AM_routine', []):
            wait_str = f" (Wait: {step.get('wait_time')})" if step.get('wait_time') else ""
            formatted += f"{step.get('step_number')}. **{step.get('action')}**: {step.get('product')}{wait_str}\n"
            formatted += f"   *Why: {step.get('rationale')}*\n"
            
        formatted += f"\n**🌙 Evening (PM) Routine Sequence:**\n"
        for step in data.get('PM_routine', []):
            wait_str = f" (Wait: {step.get('wait_time')})" if step.get('wait_time') else ""
            formatted += f"{step.get('step_number')}. **{step.get('action')}**: {step.get('product')}{wait_str}\n"
            formatted += f"   *Why: {step.get('rationale')}*\n"
            
        if data.get('three_pro_tips'):
            formatted += f"\n#### 🌸 Pro Tips\n"
            for tip in data['three_pro_tips']:
                formatted += f"- {tip}\n"
                
        if data.get('skip_days_warning'):
            formatted += f"\n> [!WARNING]\n> **Skip Days / Alternating Warning**: {data['skip_days_warning']}\n"
        return formatted
    except Exception:
        return res_json

def format_product_researcher(res_json: str) -> str:
    try:
        data = json.loads(res_json)
        orig_name = data.get('original_product') or "the product"
        orig_price = f" ({data['original_price']})" if data.get('original_price') else ""
        
        formatted = f"### Found some amazing dupes for you! Let's save some cash! 💸✨\n\n"
        formatted += f"Original Product: **{orig_name}**{orig_price}\n\n"
        
        formatted += "#### 🌸 Top Dupes I Found:\n"
        for dupe in data.get('three_dupes', []):
            formatted += f"- **{dupe.get('brand')} {dupe.get('name')}** (${dupe.get('price')}) 🛍️\n"
            formatted += f"  - **Key Ingredients**: {', '.join(dupe.get('key_shared_ingredients', []))} 🧪\n"
            formatted += f"  - **Why it's a match**: {dupe.get('why_it_works')} 💕\n\n"
            
        if data.get('conflict_warning'):
            formatted += f"\n> [!WARNING]\n> **Ingredient Conflict Warning**: {data['conflict_warning']} ⚠️\n"
        return formatted
    except Exception:
        return res_json

async def analyze_skin(query: str) -> str:
    """Assess skin type, identify concerns, flag ingredient conflicts, and recommend skincare routine.
    Call this tool when the user mentions skin type, concerns, breakouts, ingredients, or wants skincare advice.
    """
    res = await run_agent_helper(SkinAnalystAgent, query)
    session_context["skin_analysis"] = res
    return format_skin_analyst(res)

async def match_shade(query: str) -> str:
    """Determine a user's foundation and concealer shade based on undertone and depth.
    Call this tool when the user mentions foundation shade, undertone, concealer, or color matching.
    """
    context_msg = query
    if session_context["skin_analysis"]:
        context_msg += f"\nPrevious skin analysis context:\n{session_context['skin_analysis']}"
    res = await run_agent_helper(ShadeMatcherAgent, context_msg)
    session_context["shade_match"] = res
    return format_shade_matcher(res)

async def research_product(query: str) -> str:
    """Find affordable dupes, check ingredient conflicts between two products, or check suitability for a skin type.
    Call this tool when the user mentions dupes, cheaper alternatives, ingredient conflicts, or product suitability.
    """
    res = await run_agent_helper(ProductResearcherAgent, query)
    session_context["product_research"] = res
    return format_product_researcher(res)

async def full_routine_flow(query: str) -> str:
    """Sequence skin profile, recommended skincare products, and shade-matched makeup into correct AM/PM routine order.
    Call this tool for full routine sequencing, application order, AM/PM routine.
    """
    # 1. Call Skin Analyst
    skin_res = await run_agent_helper(SkinAnalystAgent, query)
    session_context["skin_analysis"] = skin_res
    
    # 2. Call Shade Matcher (pass skin analysis context)
    shade_query = query + f"\nPrevious skin analysis context:\n{skin_res}"
    shade_res = await run_agent_helper(ShadeMatcherAgent, shade_query)
    session_context["shade_match"] = shade_res
    
    # 3. Call Routine Planner
    planner_query = (
        f"Query: {query}\n"
        f"Skin Analysis: {skin_res}\n"
        f"Shade Match & Makeup: {shade_res}"
    )
    routine_res = await run_agent_helper(RoutinePlannerAgent, planner_query)
    session_context["routine_plan"] = routine_res
    
    combined = (
        format_skin_analyst(skin_res) + "\n\n" +
        format_shade_matcher(shade_res) + "\n\n" +
        format_routine_planner(routine_res)
    )
    return combined

# Define the Jamalak Orchestrator Agent
JamalakOrchestrator = Agent(
    name="JamalakOrchestrator",
    description="Jamalak's LLM beauty concierge orchestrator.",
    model="gemini-2.5-flash",
    instruction=(
        "You are Jamalak, a full-face beauty LLM concierge. You help users with skincare and makeup together. "
        "You route requests to the right specialist and combine their outputs into one clear helpful response. "
        "Use the provided tools to call the specialized agents based on routing rules:\n"
        "- For skin type, concerns, breakouts, ingredients, or skincare advice → call analyze_skin\n"
        "- For foundation shade, undertone, concealer, or color matching → call match_shade\n"
        "- For dupes, cheaper alternatives, ingredient conflicts, or product suitability → call research_product\n"
        "- For full routines, application order, AM/PM routine → call full_routine_flow\n"
        "- For anything else → answer directly as Jamalak without calling any sub-agent."
    ),
    tools=[analyze_skin, match_shade, research_product, full_routine_flow]
)

# Export as root_agent so ADK CLI can run/load it
root_agent = JamalakOrchestrator

def merge_profile_updates(current: SkinProfile, updates: dict) -> SkinProfile:
    """Merges new profile updates dict into current SkinProfile object."""
    if "skin_type" in updates and updates["skin_type"]:
        current.skin_type = updates["skin_type"]
    if "undertone" in updates and updates["undertone"]:
        current.undertone = updates["undertone"]
    if "depth" in updates and updates["depth"]:
        current.depth = updates["depth"]
        
    for list_field in ["concerns", "sensitivities", "owned_skincare", "owned_makeup", "breakout_triggers"]:
        if list_field in updates and isinstance(updates[list_field], list):
            for item in updates[list_field]:
                if item and item.strip() and item.strip().lower() not in [x.lower() for x in getattr(current, list_field)]:
                    getattr(current, list_field).append(item.strip())
                    
    if "last_session_summary" in updates and updates["last_session_summary"]:
        current.last_session_summary = updates["last_session_summary"]
        
    current.last_updated = datetime.now().isoformat()
    return current

def format_learned_facts(updates: dict) -> str:
    """Formats new learned facts from updates dict into a readable string."""
    facts = []
    for k, v in updates.items():
        if not v:
            continue
        if isinstance(v, list):
            if v:
                facts.append(f"{k}: {', '.join(v)}")
        else:
            facts.append(f"{k}: {v}")
    return ", ".join(facts)

async def extract_new_facts(user_input: str, assistant_response: str, current_profile: SkinProfile) -> dict:
    """Uses LLM to extract new profile facts from user input and assistant response."""
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    current_profile_str = json.dumps(current_profile.to_dict())
    
    prompt = f"""
You are an expert skin profile extractor. Compare the user's message and the assistant's response against the user's current skin profile.
Identify any new or updated profile facts that are NOT already present or are different in the current profile.

Fields to extract:
- skin_type (string, e.g., "oily", "dry", "combination", "normal", "sensitive")
- undertone (string, e.g., "cool", "warm", "neutral")
- depth (string, e.g., "fair", "light", "medium", "tan", "deep")
- concerns (list of strings, e.g., ["acne", "dryness"])
- sensitivities (list of strings, e.g., ["fragrance"])
- owned_skincare (list of strings, e.g., ["Drunk Elephant B-Hydra"])
- owned_makeup (list of strings, e.g., ["NARS concealer"])
- breakout_triggers (list of strings, e.g., ["coconut oil"])

Current Profile:
{current_profile_str}

User Message:
"{user_input}"

Assistant Response:
"{assistant_response}"

Instructions:
1. Return ONLY a valid JSON object containing the new or updated fields.
2. If a field is already in the current profile (e.g. skin_type is already "combination" and hasn't changed), DO NOT include it.
3. If no new profile information is found, return empty JSON object: {{}}
4. Do not include any explanation or markdown formatting (no ```json). Just the raw JSON.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error in extract_new_facts: {e}")
        import traceback
        traceback.print_exc()
        return {}

def check_routing_intent(user_input_lower: str):
    import re
    cleaned = re.sub(r'[^\w\s]', ' ', user_input_lower)
    words = set(cleaned.split())
    
    is_dupe = any(phrase in user_input_lower for phrase in ["dupe", "alternative", "cheaper", "conflict", "suitability", "suitable", "drunk elephant", "b-hydra", "tatcha", "rhode", "glazing serum"])
    is_routine = any(w in words for w in ["am", "pm"]) or any(phrase in user_input_lower for phrase in ["full routine", "what order", "morning routine", "night routine", "evening routine", "skincare routine", "makeup routine"])
    is_shade = any(phrase in user_input_lower for phrase in ["shade", "undertone", "concealer", "colour matching", "color matching", "foundation", "vein", "jewelry"])
    is_skin = any(phrase in user_input_lower for phrase in ["skin type", "concern", "breakout", "ingredient", "skincare advice", "acne", "dryness", "oily", "redness", "sensitivity", "sensitivities"])
    
    if is_dupe and not any(w in words for w in ["am", "pm"]):
        return False, False, False, True
    return is_routine, is_shade, is_skin, is_dupe

async def process_message(user_input: str) -> str:
    """Routes and executes user input against the appropriate sub-agents or directly via Jamalak."""
    user_input_strip = user_input.strip()
    user_input_lower = user_input_strip.lower()
    
    # 1. Load pending state
    state = load_pending_state()
    
    # 2. Check pending delete confirmation
    if state.get("pending_delete"):
        if user_input_strip == "DELETE":
            delete_profile()
            clear_pending_state()
            return "Got it, your profile has been deleted."
        else:
            clear_pending_state()
            return "Deletion cancelled. How can I help you today?"
            
    # 3. Check pending profile updates consent
    if "pending_profile" in state:
        updates = state["pending_profile"]
        if user_input_lower in ["yes", "y"]:
            profile = load_profile()
            profile = merge_profile_updates(profile, updates)
            save_profile(profile)
            clear_pending_state()
            return "Got it, I have updated your profile! What else can I help you with today?"
        elif user_input_lower in ["no", "n"]:
            clear_pending_state()
            return "Got it, I will use that for this session only. What else can I help you with today?"
        else:
            # Cancel updates and clear pending state if user pivots to another query
            clear_pending_state()
            
    # 4. Check for manual delete command
    if user_input_lower == "delete my profile":
        save_pending_state({"pending_delete": True})
        return "Are you sure you want to delete your profile? Please type DELETE to confirm."
        
    # 5. Process normal query
    is_routine, is_shade, is_skin, is_dupe = check_routing_intent(user_input_lower)
    
    if is_routine:
        res = await full_routine_flow(user_input)
    elif is_shade:
        res = await match_shade(user_input)
    elif is_skin:
        res = await analyze_skin(user_input)
    elif is_dupe:
        res = await research_product(user_input)
    else:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        profile = load_profile()
        context_str = get_context_string(profile)
        prompt = (
            "You are Jamalak, a full-face beauty LLM concierge. You help users with skincare and makeup together. "
            f"\n{context_str}\n\n"
            "Provide a direct response to: " + user_input
        )
        response = model.generate_content(prompt)
        res = response.text

    # 6. Extract any new profile facts and ask for consent
    profile = load_profile()
    new_updates = await extract_new_facts(user_input, res, profile)
    if new_updates:
        save_pending_state({"pending_profile": new_updates})
        learned_facts_str = format_learned_facts(new_updates)
        res += f"\n\n[Jamalek]: I'd like to save {learned_facts_str} to your profile so I remember it next time. Save this? (yes/no)"
        
    return res

async def main_async():
    # Print the disclaimer on startup
    print("Jamalek provides personalised beauty guidance only. It is not a medical tool and does not diagnose skin conditions. Always patch test new products and consult a dermatologist for persistent skin concerns.\n")
    
    # Session startup greeting based on profile
    profile = load_profile()
    if profile.skin_type and profile.undertone:
        print(f"Hey! Welcome back, gorgeous. 💖 Still matching your {profile.skin_type} skin and {profile.undertone} undertone! What are we working on today? ✨")
    else:
        print("Hey love! Welcome to Jamalek, your new skincare and makeup bestie. 💖 Tell me a bit about your skin, or drop a selfie so we can get started! ✨")
        
    # Clear any leftover pending state from previous sessions
    clear_pending_state()
    
    while True:
        try:
            user_input = input("\n[user]: ")
        except (KeyboardInterrupt, EOFError):
            break
        if not user_input or user_input.strip() == "":
            continue
        if user_input.strip().lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
            
        user_input_lower = user_input.lower()
        is_routine, is_shade, is_skin, is_dupe = check_routing_intent(user_input_lower)

        try:
            state = load_pending_state()
            if "pending_profile" in state or state.get("pending_delete"):
                pass
            elif user_input_lower == "delete my profile":
                pass
            elif is_routine:
                print("\n[Jamalek]: Routing to Full Routine flow...")
            elif is_shade:
                print("\n[Jamalek]: Routing to Shade Matcher...")
            elif is_skin:
                print("\n[Jamalek]: Routing to Skin Analyst...")
            elif is_dupe:
                print("\n[Jamalek]: Routing to Product Researcher...")
            else:
                print("\n[Jamalek]: Answering directly as Jamalek...")
            
            res = await process_message(user_input)
            print(res)
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
