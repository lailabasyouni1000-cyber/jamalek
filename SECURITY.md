# Security Policy — Jamalek Skincare Concierge

This document details the security and privacy controls implemented in Jamalek to protect user data and ensure user control.

## 1. Ephemeral Media Processing
- **Selfies and Images**: Any uploaded selfie or skin photo is sent directly and ephemerally to the Gemini Vision API for analysis (e.g., matching skin tones or identifying visible concerns). 
- **No Disk Storage**: Raw image files are processed in-memory and are **never** stored on disk or committed to the codebase. Only the resulting text classifications (such as undertone label or identified concerns) are returned to the user session.

## 2. Human-in-the-Loop Consent Gate
- **No Silent Updates**: Before writing or updating any personal skin details (such as skin type, triggers, or owned products) to the local profile, Jamalek prompts the user for explicit confirmation:
  `I'd like to save [updates] to your profile so I remember it next time. Save this? (yes/no)`
- **Opt-Out**: If the user responds with "no" or "n", the facts are kept in-memory for the current chat session only and are discarded when the session ends.

## 3. Data Deletion (Right to Be Forgotten)
- **Immediate Purge**: Users can delete their saved profile at any time by typing `delete my profile`.
- **Double Confirmation**: The system will prompt the user to type `DELETE` to confirm. Once confirmed, `user_profile.json` and any cached session state are completely deleted from the disk.

## 4. Local Credential and Profile Safety
- **Git Protection**: The project's `.gitignore` explicitly excludes all sensitive configurations, environments, and databases:
  - `.env` (contains API keys)
  - `data/user_profile.json` (user profile data)
  - `data/pending_state.json` (state cache)
  - `.venv/` (local virtual environments)
