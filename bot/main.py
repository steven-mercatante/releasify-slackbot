import os

import falcon
from slackclient import SlackClient


class PingResource(object):
    def on_get(self, req, resp):
        resp.media = {"message": "ping"}

    def on_post(self, req, resp):
        resp.media = {"message": "ping"}


class ReleaseResource(object):
    def on_post(self, req, resp):
        resp.media = {"ok": True, "hello": "world"}


def create_api():
    api = falcon.API()
    api.add_route('/release', ReleaseResource())
    return api


api = create_api()



# client = SlackClient(os.getenv('SLACK_TOKEN'))
# print('>>>>', os.getenv('SLACK_TOKEN'))


# if __name__ == '__main__':
#     channels_call = client.api_call('channels.list')
#     print(channels_call)
