# -*- coding: utf-8 -*-
import json
import asyncio
import string
import random
import logging
import uuid
import websockets
from base64 import b64encode
from webexteamssdk import WebexTeamsAPI


class WebexMessage(object):
    def __init__(self, access_token, on_message=None):
        self.access_token = access_token
        self.webex = WebexTeamsAPI(access_token=access_token)
        self.device_info = None
        self.on_message = on_message

    def _process_message(self, msg):
        if msg['data']['eventType'] == 'conversation.activity':
            activity = msg['data']['activity']
            if activity['verb'] == 'post':
                #___Convert 'id' and get message text
                uuid = activity['id']
                if "-" in uuid:
                    space_id = (b64encode(f"ciscospark://us/MESSAGE/{uuid}".encode("ascii")).decode("ascii"))
                else:
                    space_id = uuid
                webex_msg_object = self.webex.messages.get(space_id)
                #___Skip messages from the bot itself
                if webex_msg_object.personEmail in self.my_emails:
                    logging.debug('>>> message is from myself, ignoring')
                    return
                #___Process message
                if self.on_message:
                    self.on_message(webex_msg_object)

 
    def run(self):
        if self.device_info == None:
            if self._get_device_info() is None:
                logging.error('>>> could not get/create device info')
                return

        self.my_emails = self.webex.people.me().emails

        async def _run():

            async with websockets.connect(self.device_info['webSocketUrl']) as ws:
                msg = {'id': str(uuid.uuid4()),
                       'type': 'authorization',
                       'data': {
                          'token': 'Bearer ' + self.access_token
                        }
                      }
                await ws.send(json.dumps(msg))

                while True:
                    message = await ws.recv()

                    try:
                        msg = json.loads(message)
                        loop = asyncio.get_event_loop()
                        loop.run_in_executor(None, self._process_message, msg)
                    except:
                        print('>>> **ERROR** An exception occurred while processing message. Ignoring. ')

        asyncio.get_event_loop().run_until_complete(_run())