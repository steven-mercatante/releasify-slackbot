# TODO: verify commands sent by Slack using verification token
import falcon

from .resources.release import ReleaseResource
from .resources.dialog_handler import DialogHandlerResource


def create_api():
    api = falcon.API()
    api.req_options.auto_parse_form_urlencoded = True
    api.add_route('/release', ReleaseResource())
    api.add_route('/handle-button-press', DialogHandlerResource())
    return api


api = create_api()
