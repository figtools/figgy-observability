import json
from datetime import datetime

import boto3

from data.dao.ssmdao import SsmDao
from utils.logging import LoggingUtils
from utils.utils import Utils

log = LoggingUtils.configure_logging(__name__)
sns = boto3.client('sns')
ssm = SsmDao(boto3.client('ssm'))

METRICS = 'metrics'
USER_ID = 'user_id'
COMMAND = 'command'
VERSION = 'version'
count = 'count'
FIGGY_METRICS_TABLE_NAME = 'figgy-metrics'
FIGGY_METRICS_METRIC_NAME_KEY = 'metric_name'
FIGGY_METRICS_USER_ID_KEY = 'user_id'
FIGGY_METRICS_VERSION_KEY = 'version'
REQUIRED_PROPERTIES = [METRICS, USER_ID]

ddb_rsc = boto3.resource('dynamodb')
figgy_metrics = ddb_rsc.Table(FIGGY_METRICS_TABLE_NAME)


def handle(event, context):
    body = json.loads(event.get('body'))
    log.info(f'Got request with body: {body}')
    metrics = body.get(METRICS, {})
    user_id = body.get(USER_ID, "Missing")
    version = body.get(VERSION, "Missing")

    Utils.validate(metrics, f"These JSON properties are required: {REQUIRED_PROPERTIES}")

    log.info(f"Adding {metrics} to {FIGGY_METRICS_TABLE_NAME}.")

    figgy_metrics.put_item(Item={
        FIGGY_METRICS_METRIC_NAME_KEY: f'{user_id}-version',
        'version': version
    })

    figgy_metrics.update_item(
        Key={
            FIGGY_METRICS_METRIC_NAME_KEY: version
        },
        AttributeUpdates={
            'invocations': {
                'Value': count,
                'Action': 'ADD'
            }
        }
    )

    for command in metrics.keys():
        log.info(f"Adding {metrics.get(command, 0)} invocations for command: {command}")
        figgy_metrics.update_item(
            Key={
                FIGGY_METRICS_METRIC_NAME_KEY: command
            },
            AttributeUpdates={
                'invocations': {
                    'Value': metrics.get(command, 0),
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
                    'Value': metrics.get(command, 0),
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