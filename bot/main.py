import os

import falcon
from slackclient import SlackClient


class PingResource(object):
    def on_get(self, req, resp):
        resp.media = {"message": "pong"}

    def on_post(self, req, resp):
        resp.media = {"message": "pong"}


class ReleaseResource(object):
    def on_post(self, req, resp):
        resp.media = {"ok": True, "hello": "world"}


def create_api():
    api = falcon.API()
    api.add_route('/ping', PingResource())
    api.add_route('/release', ReleaseResource())
    return api


api = create_api()
