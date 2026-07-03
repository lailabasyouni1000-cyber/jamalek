# Jamalek Security and Data Privacy

I set up the security controls in this project to make sure user data is handled safely and that users have full control over what is saved. The main rules the project follows are:

## 1. How Selfies are Handled
When you upload a selfie or skin photo, the image is passed directly to the Gemini API for analysis (like finding your undertone). The raw image file is processed in memory and never written to disk, which means it is never saved locally or committed to GitHub. The agent only returns the resulting text classification to the chat session.

## 2. Consent Gate for Profile Updates
Before any new facts (like your skin type, triggers, or products you own) are saved to your local profile, the orchestrator stops and asks you for permission. If you type "no", the update is used for the current session only and is discarded when the session ends.

## 3. Deleting Your Profile
You can completely delete your saved profile at any time. Typing "delete my profile" will trigger a confirmation prompt asking you to type "DELETE". Once you do, the code removes `user_profile.json` and clears any pending session state from the disk.

## 4. Protecting Secrets and Profile Data
I added a `.gitignore` file to prevent sensitive configurations and personal data from being committed to Git. The ignored paths include:
- The `.env` file (which holds your API keys)
- The `.venv/` folder (local python environments)
- The `data/user_profile.json` and `data/pending_state.json` files (your saved skin profiles and temporary session state)
