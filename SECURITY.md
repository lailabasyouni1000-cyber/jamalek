# Jamalek Data Security and Privacy

I set up the data and privacy rules in this project to make sure your information is handled safely. 

If you upload a selfie, the bot doesn't save the image file anywhere. It just sends the image to the model to check things like your skin undertone. The file is kept in memory during the API call and never written to the disk, which prevents it from being stored locally or pushed to GitHub. The chat session only receives the text results.

The app also uses a consent gate before saving any new facts to your profile. If you tell the bot you have dry skin or that you bought a new product, the code won't write it to your profile unless you type yes. If you say no, the bot will use the details for the current chat session but won't save them, and the information is cleared when you close the session.

If you want to clear your data completely, you can type "delete my profile". The bot will ask you to confirm by typing "DELETE" in all caps. Once you do, the script removes the profile file and clears the session state. I also added a .gitignore file to prevent your local configurations, keys, and profile files from ever getting pushed to GitHub.
