import os
import sys
import asyncio
from unittest.mock import AsyncMock, patch

# Add project root to sys.path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from memory import load_profile, save_profile, delete_profile, load_pending_state, clear_pending_state
from agents.orchestrator import process_message

async def run_mocked_test():
    print("1. Clearing any existing profile/pending states...")
    delete_profile()
    clear_pending_state()
    
    # Mock extract_new_facts to return oily skin facts
    mock_updates = {
        "skin_type": "oily",
        "concerns": ["acne"],
        "undertone": "warm"
    }
    
    # Mock analyze_skin and extract_new_facts
    with patch('agents.orchestrator.analyze_skin', new_callable=AsyncMock) as mock_analyze, \
         patch('agents.orchestrator.extract_new_facts', new_callable=AsyncMock) as mock_extract:
         
        mock_analyze.return_value = "Mocked Skin Analysis: User has oily skin with active breakouts."
        mock_extract.return_value = mock_updates
        
        print("\n2. Sending a message that contains new skin profile details...")
        user_input = "I have oily skin and my main concern is acne."
        print(f"User: {user_input}")
        
        response = await process_message(user_input)
        print(f"Jamalak response:\n{response}")
        
        # Verify pending state was saved
        state = load_pending_state()
        print(f"\nPending State in Database: {state}")
        
        # Verify consent prompt was appended
        assert "[Jamalak]: I'd like to save" in response
        assert "skin_type: oily" in response
        assert "concerns: acne" in response
        
    # Test consent approval (No mocks needed here as it only reads state)
    print("\n3. Sending 'yes' to consent save...")
    consent_input = "yes"
    print(f"User: {consent_input}")
    response = await process_message(consent_input)
    print(f"Jamalak response:\n{response}")
    
    # Verify profile was successfully saved
    prof = load_profile()
    print(f"\nSaved Skin Profile: {prof.to_dict()}")
    assert prof.skin_type == "oily"
    assert "acne" in prof.concerns
    assert prof.undertone == "warm"
    
    # Test delete command confirmation flow
    print("\n4. Testing the delete command...")
    del_input = "delete my profile"
    print(f"User: {del_input}")
    response = await process_message(del_input)
    print(f"Jamalak response:\n{response}")
    
    # Verify pending delete is set
    state = load_pending_state()
    print(f"Pending State: {state}")
    assert state.get("pending_delete") is True
    
    confirm_del = "DELETE"
    print(f"User: {confirm_del}")
    response = await process_message(confirm_del)
    print(f"Jamalak response:\n{response}")
    
    # Verify profile and pending state cleared
    prof = load_profile()
    state = load_pending_state()
    print(f"\nSkin Profile after delete: {prof.to_dict()}")
    print(f"Pending State after delete: {state}")
    assert prof.skin_type == ""
    assert state == {}
    
    print("\nAll consent and deletion state machine flows verified successfully!")

if __name__ == "__main__":
    asyncio.run(run_mocked_test())
