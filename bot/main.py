# TODO: verify commands sent by Slack using verification token
import json
import logging
import os
import re
from pprint import pprint
from textwrap import dedent

import falcon
from releasify.client import ReleasifyClient
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
        dry_run_resp = releasify_client.create_release(
            REPO_OWNER, 
            repo, 
            release_type, 
            dry_run=True, 
            force=True
        )

        state = json.dumps({
            'repo': repo,
            'release_type': release_type,
        })

        dialog = json.dumps({
            'callback_id': 'create-release',
            'title': 'Create a Release',
            'submit_label': 'Create',
            'state': state,
            'elements': [{
                'type': 'text',
                'label': 'Tag',
                'name': 'tag',
                'value': dry_run_resp['tag_name'],
            }, {
                'type': 'textarea',
                'label': 'Release body',
                'name': 'body',
                'value': dry_run_resp['body'],
            }]
        })

        resp = slack_client.api_call(
            'dialog.open',
            trigger_id=req.get_param('trigger_id'),
            dialog=dialog
        )
        pprint(resp)


# TODO: rename ButtonHandlerResource
class ButtonHandlerResource(object):
    def on_post(self, req, resp):
        payload = json.loads(req.get_param('payload'))
        pprint(payload)

        state = json.loads(payload['state'])
        release_tag = payload['submission']['tag']
        release_body = payload['submission']['body']
        resp = releasify_client.create_release(
            REPO_OWNER,
            state['repo'],
            state['release_type'],
            next_tag=release_tag,
            body=release_body,
        )
        pprint(resp)

        # TODO: post message in channel upon success


def create_api():
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/release', ReleaseResource())
    api.add_route('/handle-button-press', ButtonHandlerResource())
    return api


api = create_api()
