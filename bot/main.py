# TODO: verify commands sent by Slack using verification token
import logging

import falcon

from releasify.exceptions import (
    InvalidReleaseTypeError,
    NotFoundError,
    UnauthorizedError,
)

from .config import GITHUB_USER, GITHUB_PASSWORD, REPO_OWNER, SLACK_TOKEN
from .exceptions import MissingRequiredConfigException
from .resources.release import ReleaseResource
from .resources.dialog_handler import DialogHandlerResource
from .utils import post_error_msg


class CheckConfigMiddleware(object):
    def process_request(self, req, resp):
        if not GITHUB_USER:
            raise MissingRequiredConfigException('GITHUB_USER')

        if not GITHUB_PASSWORD:
            raise MissingRequiredConfigException('GITHUB_PASSWORD')

        if not REPO_OWNER:
            raise MissingRequiredConfigException('REPO_OWNER')

        if not SLACK_TOKEN:
            raise MissingRequiredConfigException('SLACK_TOKEN')


def handle_error(exception, req, resp, params):
    channel_id = req.params['channel_id']
    user_id = req.params['user_id']

    if isinstance(exception, MissingRequiredConfigException):
        resp.media = str(exception)
        resp.status_code = falcon.HTTP_500
        return 

    if isinstance(exception, UnauthorizedError):
        msg = 'Invalid GitHub credentials'
    elif isinstance(exception, (InvalidReleaseTypeError)):
        msg = 'Invalid `release_type`. Must be one of: `major`, `minor`, `patch`'
    elif isinstance(exception, NotFoundError):
        msg = 'Repo not found'
    else:
        msg = 'An unexpected error occurred.'

    post_error_msg(channel_id, user_id, msg)


def create_api():
    api = falcon.API(middleware=[CheckConfigMiddleware()])
    api.req_options.auto_parse_form_urlencoded = True
    api.add_error_handler(Exception, handle_error)
    api.add_route('/release', ReleaseResource())
    api.add_route('/handle-button-press', DialogHandlerResource())
    return api


api = create_api()
