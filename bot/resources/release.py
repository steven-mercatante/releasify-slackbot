import json
import logging
import re

from ..config import REPO_OWNER, releasify_client, slack_client
from ..utils import post_error_msg


text_parser_pattern = re.compile(r'^\s*(?P<repo>[\w-]+)\s+(?P<release_type>\w+)\s*$')

class ReleaseResource(object):
    def on_post(self, req, resp):
        logging.critical(req.params)
        text = req.get_param('text')

        try:
            repo, release_type = parse_text(text)
        except TypeError:
            msg = 'Invalid paramters. Format should be `/releasify repo_name release_type`'
            post_error_msg(req.get_param('channel_id'), req.get_param('user_id'), msg)

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
            'title': 'Create a Release for',
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

        slack_client.api_call(
            'dialog.open',
            trigger_id=req.get_param('trigger_id'),
            dialog=dialog
        )


def parse_text(text):
    try:
        matches = text_parser_pattern.search(text).groupdict()
        return matches['repo'], matches['release_type']
    except AttributeError:
        # TODO: raise an explicit exception
        pass
