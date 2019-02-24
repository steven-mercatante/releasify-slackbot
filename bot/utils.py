from .config import slack_client


def post_error_msg(channel, user, msg):
    slack_client.api_call(
        'chat.postEphemeral',
        channel=channel,
        user=user,
        text=msg,
        as_user=True,
    )
