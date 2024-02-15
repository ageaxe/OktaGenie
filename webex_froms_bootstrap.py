import os
import sys
from webexteamssdk import WebexTeamsAPI
from webex_ws_bootstrap import WebexMessage

from webexteamssdk.models.cards.card import AdaptiveCard
from webexteamssdk.models.cards.inputs import Text, Number
from webexteamssdk.models.cards.components import TextBlock
from webexteamssdk.models.cards.actions import Submit



adaptive_card_content = {
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
        "type": "AdaptiveCard",
        "version": "1.0",
        "body": [
            {
                "type": "TextBlock",
                "text": "Please provide following details to create OIDC Application",
                "size": "Medium",
                "weight": "Bolder",
            },
            {
                "type": "Input.Text",
                "id": "applicationName",
                "placeholder": "Application Name",
            },
            {
                "type": "Input.Text",
                "id": "espBusinessApplication",
                "placeholder": "ESP Business Application",
            },
            {
                "type": "Input.Text",
                "id": "applicationOwnerGroup",
                "placeholder": "Application Owner Group",
            },
            {"type": "Input.Text", "id": "teamMailer", "placeholder": "Team Mailer"},
            {"type": "Input.Text", "id": "clientId", "placeholder": "Client ID"},
            {
                "type": "Input.Text",
                "id": "clientSecret",
                "placeholder": "Client Secret",
                "style": "password",
            },
        ],
        "actions": [{"type": "Action.Submit", "title": "Submit"}],
    },
}

class WebExForms(object):
    def __init__(self, api : WebexTeamsAPI,qa_chain):
        self.api = api
        self.qa_chain = qa_chain

    def process_message(self,message_obj):  
        
        if "hi" in message_obj.text.lower() or "hello" in message_obj.text.lower():
            msg_result = self.api.messages.create(
                toPersonEmail=message_obj.personEmail,
                markdown="""Greetings!
                I am OktaGenie, your dedicated Okta assistant. 
                I have been trained on the comprehensive Okta knowledge base and am at your service to support you with all your Okta-related inquiries.
                Whether you require assistance with accessing applications, managing your user profile, or simply seeking information about available features, I am here to guide you efficiently.
                Please feel free to inquire about any concerns you may have, and I will do my utmost to provide accurate and helpful responses.""",
            )
        elif "yes" in message_obj.text.lower():
            msg_result = self.api.messages.create(
                toPersonEmail=message_obj.personEmail,
                attachments=[adaptive_card_content],
                text="fallback",
            )
        elif message_obj.attachments:
            msg_result = self.api.messages.create(           
                roomId=message_obj.roomId,
                markdown="OIDC Application is created successfully! \n Can be accessed at: https://myid-sso-dev.cisco.com/application/internalsaml/a645256e-0198-4b3d-b416-2b0b5b519a12",
            )
        else:
            self.api.messages.create(toPersonEmail=message_obj.personEmail, markdown="I am looking into your query, please wait for a moment ....")
            result = self.qa_chain({"query": message_obj.text.lower()})
            message = None
            if "client credentials" in result["result"].lower():
                message = result["result"] + "\n\n\n"+ "You can find more details at : https://developer.okta.com/"+result["source_documents"][0].metadata["source"].replace(" ", "") + "\n\n\n" + "Will you like to proceed with OIDC Application creation ?"
                
            else:
                message = result["result"] + "\n\n\n"+ "You can find more details at : https://developer.okta.com/"+result["source_documents"][0].metadata["source"].replace(" ", "")
            msg_result = self.api.messages.create(toPersonEmail=message_obj.personEmail, markdown=message)


