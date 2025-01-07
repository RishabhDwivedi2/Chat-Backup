1. Go to https://console.cloud.google.com/ and create a new project, for example "EmailBot".

2. Select the project you created.

3. Now, in left sidebar (or Hamburger menu), click on "APIs & Services" -> Library. now do as follows:
    - Search for "gmail api" and enable it.
    - Search for "cloud pub/sub" and enable it.

4. Then, in left sidebar (or Hamburger menu), click on "APIs & Services" -> Credentials -> Create Credentials, But when you click on "Create Credentials", select "OAuth 2.0 Client IDs".

5. Now, you will see a popup, click on "Configure consent screen", select "External" and select "Testing", and then click on "Confirm" or "Save".

6. Now, go back to the previous page, and click on "Create Credentials" again, but this time select "OAuth client ID".

7. Then, you'll entered in Create OAuth client ID, fill in details as follows:
    - Application type: Web application
    - Name: EmailBot
    - Authorised JavaScript origins: http://localhost:3001, http://localhost:8000, https://7a35-103-203-227-178.ngrok-free.app
    - Authorised redirect URIs: http://localhost:8000/auth/google/callback, http://localhost:8000/gmail-webhook

8. Now, click on "Create" and you'll see a popup that says "OAuth client created", and give some information about the client ID and secret and says download the JSON file.

9. Download the JSON file and save it in your project directory.

10. Now, go to "APIs & Services" -> OAuth consent screen -> Edit app, and fill in details as follows:
    - User type: External
    - Application name: EmailBot
    - User support email: Add your email address
    - Authorised domain: Add your domain name, for example: deltabots.ai
    - Developer contact information: Add your email address
    - Click on "Save and Continue"
    - Next, you'll came to scopes tab, click on "Add or remove scopes", and add the following scopes:
        - https://www.googleapis.com/auth/gmail.modify
        - https://www.googleapis.com/auth/gmail.send
        - https://www.googleapis.com/auth/gmail.readonly
    - Click on "Save and Continue"
    - Next, you'll came to test users tab, click on "Add users", and add your email address.
    - Click on "Save and Continue"
    - Now, click on "Publish app"

11. Now, in search bar, search for "pub/sub" and click on "Pub/Sub".

12. Then, click on "Create Topic" and fill in details as follows:
    - Topic ID: gmail-notifications
    - Click on "Create"

13. Now, click on the topic you created. You'll see at the bottom right side in Permissions tab, the Role/Principal showing. There for owner, there is already the email address which the google cloud project was created with.

14. Now, There we need another role/principal. So, click on "Add Principal" and do as follows:
    - Type in this for email/id whatever asking for, gmail-api-push@system.gserviceaccount.com
    - Then, in Assign role, select "Pub/Sub Publisher" 
    - Click on "Save"

15. Now, since we have created the topic, we need to create a subscription to it. Mind you we need to create 2 subscriptions, one for the gmail notifications subscription and one for the gmail webhook push subscription. Click on "Create Subscription".

16. Now, fill in details as follows for the gmail notifications subscription:
    - Subscription Name: gmail-notifications-subscription
    - Topic Name: gmail-notifications or it will auto suggest it.
    - Delivery type: Pull
    - Click on "Create"

17. Now, fill in details as follows for the gmail webhook push subscription:
    - Subscription Name: gmail-webhook-push-subscription
    - Topic Name: gmail-webhook-push or it will auto suggest it.
    - Delivery type: Push
    - Endpoint URL: https://7a35-103-203-227-178.ngrok-free.app/gmail-webhook
    - Click on "Create"

18. Everything is done, now you can go back to your local machine and start the server and test the webhook.


