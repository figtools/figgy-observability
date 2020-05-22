import json
import boto3

from data.dao.ssmdao import SsmDao
from utils.logging import LoggingUtils
from utils.utils import Utils

log = LoggingUtils.configure_logging(__name__)
sns = boto3.client('sns')
ssm = SsmDao(boto3.client('ssm'))

STACKTRACE = 'stacktrace'
OS = 'os'
COMMAND = 'command'
ERROR_TOPIC_SSM_KEY = '/figgy/resources/sns/error-topic/arn'
REQUIRED_PROPERTIES = [STACKTRACE, OS, COMMAND]

ERROR_TOPIC_ARN = ssm.get_parameter(ERROR_TOPIC_SSM_KEY)


def handle(event, context):
    body = json.loads(event.get('body'))
    log.info(f'Got request with body: {body}')
    stacktrace = body.get('stacktrace')
    os = body.get('os')
    command = body.get('command')

    Utils.validate(stacktrace and os and command, f"These JSON properties are required: {REQUIRED_PROPERTIES}")

    response = sns.publish(
        TopicArn=ERROR_TOPIC_ARN,
        Message=body,
        Subject=f'Error detected for command: {command}',
        MessageStructure='json'
    )

    return {"statusCode": 200, "body": "Error logged successfully."}
