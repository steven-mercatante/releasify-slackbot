import os

from releasify.client import ReleasifyClient
from slackclient import SlackClient


GITHUB_USER = os.getenv('GITHUB_USER')
GITHUB_PASSWORD = os.getenv('GITHUB_PASSWORD')
REPO_OWNER = os.getenv('REPO_OWNER')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')

slack_client = SlackClient(SLACK_TOKEN)
releasify_client = ReleasifyClient(GITHUB_USER, GITHUB_PASSWORD)
