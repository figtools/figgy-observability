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
    stacktrace = body.get(STACKTRACE)
    os = body.get(OS)
    command = body.get(COMMAND)

    Utils.validate(stacktrace and os and command, f"These JSON properties are required: {REQUIRED_PROPERTIES}")

    sns.publish(
        TopicArn=ERROR_TOPIC_ARN,
        Message=f'OS: {os}\n\n Stacktrace:\n\n{stacktrace}',
        Subject=f'Error detected for command: {command}'[:100]
    )

    return {"statusCode": 200, "body": "Error logged successfully."}
