import boto3
import json
import time
import requests
from data.dao.ssmdao import SsmDao
from utils.logging import LoggingUtils

log = LoggingUtils.configure_logging(__name__)
ssm = SsmDao(boto3.client('ssm'))

CURRENT_VERSION_SSM_KEY = '/figgy/deployments/current_version'
ROLLOUT_MODIFIER_KEY = '/figgy/deployments/rollout_modifier'
CHANGELOG_ADDRESS = 'https://raw.githubusercontent.com/figtools/figgy-cli/master/CHANGELOG.md'

LAST_FETCH = 0
CACHE_DURATION = 60 * 3  # cache the latest version for 3 minutes
CHANGELOG, CURRENT_VERSION, NOTIFY_CHANCE = None, None, None


def update_version():
    global LAST_FETCH, CURRENT_VERSION, NOTIFY_CHANCE
    if time.time() - CACHE_DURATION > LAST_FETCH:
        CURRENT_VERSION = ssm.get_parameter(CURRENT_VERSION_SSM_KEY)
        NOTIFY_CHANCE = ssm.get_parameter(ROLLOUT_MODIFIER_KEY)
        LAST_FETCH = time.time()

def handle(event, context):
    global CHANGELOG

    if not CHANGELOG:
        result = requests.get('https://raw.githubusercontent.com/figtools/figgy/develop/cli/CHANGELOG.md')
        CHANGELOG = result.text if result.status_code == 200 else "Empty"

    update_version()

    print(f'{CURRENT_VERSION} -> {NOTIFY_CHANCE}')
    return {"statusCode": 200, "body":
        json.dumps({
            "version": CURRENT_VERSION,
            "notify_chance": NOTIFY_CHANCE,
            "changelog": CHANGELOG
        })
    }
