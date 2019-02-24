# TODO: verify commands sent by Slack using verification token
import json
import logging
import os
import re
from pprint import pprint
from textwrap import dedent

import falcon
import requests
from releasify.client import Client as ReleasifyClient
from slackclient import SlackClient


GITHUB_USER = os.getenv('GITHUB_USER')
GITHUB_PASSWORD = os.getenv('GITHUB_PASSWORD')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
REPO_OWNER = 'steven-mercatante'


text_parser_pattern = re.compile(r'^\s*(?P<repo>[\w-]+)\s+(?P<release_type>\w+)\s*$')
slack_client = SlackClient(SLACK_TOKEN)
releasify_client = ReleasifyClient(GITHUB_USER, GITHUB_PASSWORD)


def parse_text(text):
    try:
        matches = text_parser_pattern.search(text).groupdict()
        return matches['repo'], matches['release_type']
    except AttributeError:
        # TODO: raise an explicit exception
        pass


class ReleaseResource(object):
    def on_post(self, req, resp):
        logging.critical(req.params)
        text = req.get_param('text')

        repo, release_type = parse_text(text)
        # TODO: check release_type is valid - return error otherwise

        # TODO: force should be passable as an arg. Or maybe show a button asking the user if they want to force it if there haven't been commits since the last release.
        resp = releasify_client.create_release(
            REPO_OWNER, 
            repo, 
            release_type, 
            dry_run=True, 
            force_release=True
        )
        # pprint(resp)

        body = dedent(f"""
        Version: *{resp['tag_name']}*
        Body: *{resp['body']}*
        Should I create this release? 
        """)

        # msg = {
        #     'channel': req.get_param('channel_id'),
        #     'user': req.get_param('user_id'),
        #     'as_user': True,
        #     "blocks": [{
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn",
        #             "text": body,
        #         },
        #     }, {
        #         "type": "actions",
        #         "elements": [{
        #             "type": "button",
        #             "text": {
        #                 "type": "plain_text",
        #                 "text": "Yes",
        #             },
        #             "action_id": "confirm",
        #             "value": json.dumps({
        #                 'repo': repo,
        #                 'release_type': release_type,
        #             }),
        #         }, {
        #             "type": "button",
        #             "text": {
        #                 "type": "plain_text",
        #                 "text": "No",
        #             },
        #             "action_id": "cancel",
        #             "value": json.dumps({
        #                 'message_id': 'foo'
        #             }),
        #         }]
        #     }]
        # }


        dialog = json.dumps({
            "callback_id": "create-release",
            "title": "Create a Release",
            "submit_label": "Create",
            "notify_on_cancel": True,
            "state": "Limo",
            'elements': [{
                'type': 'text',
                'label': 'Tag',
                'name': 'tag',
                'value': resp['tag_name'],
            }, {
                'type': 'textarea',
                'label': 'Release body',
                'name': 'body',
                'value': resp['body'],
            }]
        })

        trigger_id = req.get_param('trigger_id')
        print('>>>> trigger ID', trigger_id)

        resp = slack_client.api_call(
            'dialog.open',
            trigger_id=trigger_id,
            dialog=dialog
        )
        pprint(resp)

        # resp = slack_client.api_call('chat.postEphemeral', **msg)
        # resp = slack_client.api_call('chat.postMessage', **msg)

        # resp = requests.post(
        #     req.get_param('response_url'),
        #     data={
        #         'response_type': 'ephemeral',
        #         'text': 'lol'
        #     }
        # )

        # print('>> orig msg ts:', resp['ts'])
        # pprint(resp.content)
        

class ButtonHandlerResource(object):
    def on_post(self, req, resp):
        payload = json.loads(req.get_param('payload'))
        pprint(payload)

        action_id = payload['actions'][0]['action_id']
        action_value = json.loads(payload['actions'][0]['value'])
        # print('>>>>> action_id:', action_id)
        # print('>>>>> action_value:', action_value)

        # TODO: if action_id is `cancel`, delete the prev message?

        response_text = ''

        if action_id == 'cancel':
            print('DELETE THIS.....', payload['channel']['id'], payload['container']['message_ts'])
            slack_client.api_call(
                'chat.postMessage',
                channel=payload['channel']['id'],
                text="done!!!!",
            )
            # foo = slack_client.api_call(
            #     'chat.delete', 
            #     channel=payload['channel']['id'], 
            #     ts=payload['container']['message_ts'],
            #     as_user=True
            # )
            # pprint(foo)

        # if action_id == 'confirm':
        #     repo = action_value['repo']
        #     release_type = action_value['release_type']
        #     try:
        #         resp = releasify_client.create_release(
        #             REPO_OWNER, 
        #             repo, 
        #             release_type, 
        #         )
        #         pprint(resp)
        #         response_text = 'success!!!'
        #     except Exception as e:
        #         response_text = f'Error: Unable to create {release_type} release. {str(e)}'

        # resp = slack_client.api_call(
        #     'chat.postMessage', 
        #     channel=payload['channel']['id'],
        #     as_user=True,
        #     text=response_text,
        # )
        # print('``````````````````````````````')
        # pprint(resp)
        # resp.media = payload 


def create_api():
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/release', ReleaseResource())
    api.add_route('/handle-button-press', ButtonHandlerResource())
    return api


api = create_api()
