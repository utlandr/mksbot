import json

import requests
import yaml


def upload_streamable(video_url: str, user: str, pw: str) -> str | None:
    """Uploads a video from a url to streamable, returns the streamable url if successful"""
    api_url = "https://api.streamable.com/import"
    headers = {"User-Agent": "Streamable Discord Upload Bot"}
    params = {"url": video_url}
    r = requests.get(api_url, auth=(user, pw), headers=headers, params=params)

    out = json.loads(r.content)

    if out["status"]:
        short_code: str = out["shortcode"]
        return short_code
    return None


def streamable_instance() -> tuple[str, str]:
    """Provides details for streamable account instance

    :return: streamable username
    :return: streamable user password
    """
    config = yaml.safe_load(open("config.yml"))
    return config["streamable"]["user"], config["streamable"]["pw"]
