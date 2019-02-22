# TODO: verify commands sent by Slack using verification token
import json
import logging
import os
from pprint import pprint

import falcon
from slackclient import SlackClient


GITHUB_USER = os.getenv('GITHUB_USER')
GITHUB_PASSWORD = os.getenv('GITHUB_PASSWORD')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')

# print('GITHUB_USER:', GITHUB_USER)
# print('GITHUB_PASSWORD:', GITHUB_PASSWORD)
# print('SLACK_TOKEN:', SLACK_TOKEN)


client = SlackClient(SLACK_TOKEN)


class PingResource(object):
    def on_get(self, req, resp):
        resp.media = {"message": "pong"}

    def on_post(self, req, resp):
        resp.media = {"message": "pong"}


class ReleaseResource(object):
    def on_post(self, req, resp):
        logging.critical(req.params)
        text = req.get_param('text')
        print('text....', text)
        # TODO: check release_type is valid - return error otherwise

        msg = {
            'channel': req.get_param('channel_id'),
            'as_user': True,
            "blocks": [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_hello_ *world*",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Button",
                    },
                    "value": "click_me_123"
                }
            }]
        }

        resp = client.api_call('chat.postMessage', **msg)
        pprint(resp)
        

def create_api():
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/ping', PingResource())
    api.add_route('/release', ReleaseResource())
    return api


api = create_api()
