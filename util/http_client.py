import requests
from util.logger import logger
import json
from requests.auth import HTTPBasicAuth


def http_get_request(http_path, host, params, basic_auth_user, basic_auth_pass):
    logger.info("http_get_request ----- http_path: " + http_path + ", params: " + str(params))
    url = host + http_path
    logger.info(url)
    headers = {
        'accept': "*/*",
        'cache-control': "no-cache",
    }
    if params is None:
        params = {}
    response = requests.request("GET", url, headers=headers, params=params, timeout=20,
                                auth=HTTPBasicAuth(basic_auth_user, basic_auth_pass))
    res = json.loads(response.content.decode('UTF-8'))
    logger.info(res)
    logger.info("Time taken: " + str(response.elapsed.total_seconds()/60))
    if response.status_code == 200:
        return res
    return None

