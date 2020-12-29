import requests

from src.helper.json_helper import convert_jsonify


def send_callback_request(output, callback_url):
    if callback_url is None:
        return

    body = convert_jsonify(output)
    header = {"content-type": "application/json"}
    try:
        requests.post(callback_url, data=body, headers=header, verify=False)
    except:
        print("Callback URL have a problem!")
