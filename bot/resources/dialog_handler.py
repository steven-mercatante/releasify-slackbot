import json
from pprint import pprint

from ..config import REPO_OWNER, releasify_client, slack_client


class DialogHandlerResource(object):
    def on_post(self, req, resp):
        payload = json.loads(req.get_param('payload'))

        state = json.loads(payload['state'])
        release_tag = payload['submission']['tag']
        release_body = payload['submission']['body']
        resp = releasify_client.create_release(
            REPO_OWNER,
            state['repo'],
            state['release_type'],
            next_tag=release_tag,
            body=release_body,
            force=True,
        )
        pprint(resp)

        # TODO: post message in channel upon success
        # TODO: post message in channel upon error
