import json
import boto3
from aws_embedded_metrics import metric_scope

from data.dao.ssmdao import SsmDao
from utils.logging import LoggingUtils
from utils.utils import Utils

log = LoggingUtils.configure_logging(__name__)
sns = boto3.client('sns')
ssm = SsmDao(boto3.client('ssm'))

STACKTRACE = 'stacktrace'
OS = 'os'
COMMAND = 'command'
VERSION = 'version'
ERROR_TOPIC_SSM_KEY = '/figgy/resources/sns/error-topic/arn'
REQUIRED_PROPERTIES = [STACKTRACE, OS, COMMAND]

ERROR_TOPIC_ARN = ssm.get_parameter(ERROR_TOPIC_SSM_KEY)


@metric_scope
def publish_error_metric(platform: str, version: str, metrics):
    metrics.set_namespace("figgy")
    metrics.put_dimensions({"Version": version, "Platform": platform})

    metrics.set_namespace("figgy")
    metrics.put_metric('error', 1, "Count")


def handle(event, context):
    body = json.loads(event.get('body'))
    log.info(f'Got request with body: {body}')
    stacktrace = body.get(STACKTRACE)
    os = body.get(OS)
    version = body.get(VERSION)
    command = body.get(COMMAND)

    Utils.validate(stacktrace and os and command, f"These JSON properties are required: {REQUIRED_PROPERTIES}")

    publish_error_metric(platform=os, version=version)

    sns.publish(
        TopicArn=ERROR_TOPIC_ARN,
        Message=f'Version: {version}\nOS: {os}\n\n Stacktrace:\n\n{stacktrace}',
        Subject=f'Error detected for command: {command}'[:100]
    )

    return {"statusCode": 200, "body": "Error logged successfully."}
