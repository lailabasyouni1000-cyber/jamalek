# Jamalek Data Security and Privacy

I set up the security controls in this project to make sure user data is handled safely and to give users full control over what is saved. The main rules the project follows are:

## How Selfies are Handled
When the agent analyzes a selfie or skin photo, it doesn't store the raw image. It just sends the image to the model to check things like undertone and skin concerns. The file is kept in memory during the call and never written to disk, so it's never stored locally or pushed to GitHub. The only thing the chat session gets back is the text result.

## Consent Gate for Profile Updates
The system uses a consent gate before saving new facts. If you tell the bot you have dry skin or bought a new moisturizer, the orchestrator won't save it to your profile without asking first. If you say no, the bot will use that detail for the current chat session but won't write it to your profile, and the information disappears when the session ends.

## Deleting Your Profile
If you want to clear your data, you can delete your profile by typing "delete my profile". The code will ask you to confirm by typing "DELETE" in all caps. Once you confirm, the script deletes your user profile and clears the session state file.

## Protecting Secrets and Profile Data
To make sure no keys or profiles get committed to Git, the project uses a .gitignore file. This prevents files like the .env configuration, the local virtual environment, and the local profile store from ever being pushed to the remote repository.
