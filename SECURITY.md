# Jamalek Data Security and Privacy

I set up a few rules in this project to keep your personal data safe and make sure nothing gets saved without your permission. 

If you upload a selfie, the code processes it in memory to extract your skin undertone. It sends the file to the model during the API call but never writes it to the disk, which prevents it from being stored locally or committed to GitHub by accident. The app only keeps the text result.

There is also a consent gate before the bot saves anything new to your profile. If you tell the bot you have dry skin or a specific breakout trigger, it won't write it to user_profile.json unless you explicitly type yes. If you say no, the bot uses that info for the current conversation but discards it as soon as you close the session.

If you want to clear your data, you can delete your profile by typing "delete my profile" and confirming with "DELETE". The script will immediately wipe the profile and session cache. I also added a .gitignore file to make sure your API keys and local profile files never get pushed to the remote repository.
