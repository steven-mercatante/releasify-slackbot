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
                force=True,
            )

            msg = '🎉 *{user}* created the *{tag}* release for *{owner}*/*{repo}*'.format(
                user=payload['user']['name'],
                tag=resp['tag_name'],
                owner=REPO_OWNER,
                repo=state['repo']
            )

            slack_client.api_call(
                'chat.postMessage',
                channel=payload['channel']['id'],
                text=msg,
                as_user=True,
            )
        except Exception as e:
            msg = f'😬 An error occurred: {str(e)}'
            slack_client.api_call(
                'chat.postEphemeral',
                channel=payload['channel']['id'],
                user=payload['user']['id'],
                text=msg,
                as_user=True,
            )
