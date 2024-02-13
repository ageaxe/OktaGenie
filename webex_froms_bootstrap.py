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
                "text": "Application Details",
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
        
        if "yes" in message_obj.text.lower():
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
            result = self.qa_chain({"query": message_obj.text.lower()})
            message = result["result"] + "\n"+ "You can find more details at : https://developer.okta.com/"+result["source_documents"][0].metadata["source"] + "\n" + "Are you happy with answer or will like to know more ...?"
            msg_result = self.api.messages.create(toPersonEmail=message_obj.personEmail, markdown=message)


