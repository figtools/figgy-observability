import json
from datetime import datetime
from typing import Dict

import boto3
from aws_embedded_metrics import metric_scope

from data.dao.ssmdao import SsmDao
# from utils.logging import LoggingUtils
from utils.logging import LoggingUtils
from utils.utils import Utils

log = LoggingUtils.configure_logging(__name__)
sns = boto3.client('sns')
ssm = SsmDao(boto3.client('ssm'))

METRICS = 'metrics'
USER_ID = 'user_id'
COMMAND = 'command'
VERSION = 'version'
PLATFORM = 'platform'
count = 'count'
FIGGY_METRICS_TABLE_NAME = 'figgy-metrics'
FIGGY_METRICS_METRIC_NAME_KEY = 'metric_name'
FIGGY_METRICS_USER_ID_KEY = 'user_id'
FIGGY_METRICS_VERSION_KEY = 'version'
FIGGY_METRICS_PLATFORM_KEY = 'platform'
REQUIRED_PROPERTIES = [METRICS, USER_ID]

ddb_rsc = boto3.resource('dynamodb')
figgy_metrics = ddb_rsc.Table(FIGGY_METRICS_TABLE_NAME)


@metric_scope
def publish_cw_stats(platform: str, version: str, stats, metrics):
    metrics.set_namespace("figgy")
    metrics.put_dimensions({"Version": version, "Platform": platform})

    for key, val in stats.items():
        metrics.set_namespace("figgy")
        metrics.put_metric(key, val, "Count")


def handle(event, context):
    body = json.loads(event.get('body'))
    log.info(f'Got request with body: {body}')

    stats = body.get(METRICS, {})
    user_id = body.get(USER_ID, "Missing")
    version = body.get(VERSION, "Missing")
    platform = body.get(PLATFORM, "Missing")

    Utils.validate(stats, f"These JSON properties are required: {REQUIRED_PROPERTIES}")

    publish_cw_stats(platform, version, stats)

    log.info(f"Adding {stats} to {FIGGY_METRICS_TABLE_NAME}.")

    figgy_metrics.put_item(Item={
        FIGGY_METRICS_METRIC_NAME_KEY: f'{user_id}-version',
        FIGGY_METRICS_VERSION_KEY: version,
        FIGGY_METRICS_PLATFORM_KEY: platform
    })

    figgy_metrics.update_item(
        Key={
            FIGGY_METRICS_METRIC_NAME_KEY: version
        },
        AttributeUpdates={
            'invocations': {
                'Value': 1,
                'Action': 'ADD'
            }
        }
    )

    for command in stats.keys():
        log.info(f"Adding {stats.get(command, 0)} invocations for command: {command}")
        figgy_metrics.update_item(
            Key={
                FIGGY_METRICS_METRIC_NAME_KEY: command
            },
            AttributeUpdates={
                'invocations': {
                    'Value': stats.get(command, 0),
                    'Action': 'ADD'
                }
            }
        )

        figgy_metrics.update_item(
            Key={
                FIGGY_METRICS_METRIC_NAME_KEY: f'{user_id}-{command}'
            },
            AttributeUpdates={
                'invocations': {
                    'Value': stats.get(command, 0),
                    'Action': 'ADD'
                }
            }
        )

    return {"statusCode": 200, "body": "Metrics logged successfully."}


"""
Exported body:

'{
    "metrics": {
        "get": 10,
        "put": 20,
        "sync": 3
    }
}
"""
