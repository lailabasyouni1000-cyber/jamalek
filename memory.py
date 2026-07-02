import os
import json

class SkinProfile:
    def __init__(self, 
                 skin_type="", 
                 undertone="", 
                 depth="", 
                 concerns=None, 
                 sensitivities=None, 
                 owned_skincare=None, 
                 owned_makeup=None, 
                 breakout_triggers=None, 
                 last_session_summary="", 
                 last_updated=""):
        self.skin_type = skin_type
        self.undertone = undertone
        self.depth = depth
        self.concerns = concerns if concerns is not None else []
        self.sensitivities = sensitivities if sensitivities is not None else []
        self.owned_skincare = owned_skincare if owned_skincare is not None else []
        self.owned_makeup = owned_makeup if owned_makeup is not None else []
        self.breakout_triggers = breakout_triggers if breakout_triggers is not None else []
        self.last_session_summary = last_session_summary
        self.last_updated = last_updated

    def to_dict(self):
        return {
            "skin_type": self.skin_type,
            "undertone": self.undertone,
            "depth": self.depth,
            "concerns": self.concerns,
            "sensitivities": self.sensitivities,
            "owned_skincare": self.owned_skincare,
            "owned_makeup": self.owned_makeup,
            "breakout_triggers": self.breakout_triggers,
            "last_session_summary": self.last_session_summary,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            skin_type=data.get("skin_type", ""),
            undertone=data.get("undertone", ""),
            depth=data.get("depth", ""),
            concerns=data.get("concerns", []),
            sensitivities=data.get("sensitivities", []),
            owned_skincare=data.get("owned_skincare", []),
            owned_makeup=data.get("owned_makeup", []),
            breakout_triggers=data.get("breakout_triggers", []),
            last_session_summary=data.get("last_session_summary", ""),
            last_updated=data.get("last_updated", "")
        )

PROFILE_FILE = os.path.join(os.path.dirname(__file__), "data", "user_profile.json")

def load_profile() -> SkinProfile:
    if not os.path.exists(PROFILE_FILE):
        return SkinProfile()
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return SkinProfile.from_dict(data)
    except Exception:
        return SkinProfile()

def save_profile(profile: SkinProfile):
    os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile.to_dict(), f, indent=4, ensure_ascii=False)

def get_context_string(profile: SkinProfile) -> str:
    parts = []
    if profile.skin_type:
        parts.append(f"Skin Type: {profile.skin_type}")
    if profile.undertone:
        parts.append(f"Undertone: {profile.undertone}")
    if profile.depth:
        parts.append(f"Skin Depth: {profile.depth}")
    if profile.concerns:
        parts.append(f"Skin Concerns: {', '.join(profile.concerns)}")
    if profile.sensitivities:
        parts.append(f"Sensitivities/Allergies: {', '.join(profile.sensitivities)}")
    if profile.owned_skincare:
        parts.append(f"Owned Skincare Products: {', '.join(profile.owned_skincare)}")
    if profile.owned_makeup:
        parts.append(f"Owned Makeup Products: {', '.join(profile.owned_makeup)}")
    if profile.breakout_triggers:
        parts.append(f"Breakout Triggers: {', '.join(profile.breakout_triggers)}")
    if profile.last_session_summary:
        parts.append(f"Summary of Last Session: {profile.last_session_summary}")
    
    if not parts:
        return "No user profile information stored yet."
    return "User Profile Information:\n- " + "\n- ".join(parts)

def delete_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            os.remove(PROFILE_FILE)
        except Exception:
            pass

PENDING_FILE = os.path.join(os.path.dirname(__file__), "data", "pending_state.json")

def load_pending_state() -> dict:
    if not os.path.exists(PENDING_FILE):
        return {}
    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_pending_state(state: dict):
    os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

def clear_pending_state():
    if os.path.exists(PENDING_FILE):
        try:
            os.remove(PENDING_FILE)
        except Exception:
            pass
