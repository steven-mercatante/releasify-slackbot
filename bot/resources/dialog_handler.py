import json
from pprint import pprint

from ..config import REPO_OWNER, releasify_client, slack_client


class DialogHandlerResource(object):
    def on_post(self, req, resp):
        payload = json.loads(req.get_param('payload'))
        pprint(payload)

        state = json.loads(payload['state'])
        release_tag = payload['submission']['tag']
        release_body = payload['submission']['body']

        try:
            resp = releasify_client.create_release(
                REPO_OWNER,
                state['repo'],
                state['release_type'],
                next_tag=release_tag,
                body=release_body,
            )
            pprint(resp)
        except Exception as e:
            msg = f'An error occurred: {str(e)}'
            slack_client.api_call(
                'chat.postEphemeral',
                channel=payload['channel']['id'],
                user=payload['user']['id'],
                text=msg,
                as_user=True,
            )

        # TODO: post message in channel upon success
