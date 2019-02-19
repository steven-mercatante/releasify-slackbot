# TODO: verify commands sent by Slack using verification token
import json
import logging
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
        logging.critical(req.params)
        release_type = req.get_param('text', '').strip()
        # TODO: check release_type is valid - return error otherwise

        resp.media = {"text": release_type}


def create_api():
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/ping', PingResource())
    api.add_route('/release', ReleaseResource())
    return api


api = create_api()
