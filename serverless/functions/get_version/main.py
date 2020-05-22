import boto3

from data.dao.ssmdao import SsmDao
from utils.logging import LoggingUtils

log = LoggingUtils.configure_logging(__name__)
ssm = SsmDao(boto3.client('ssm'))

CURRENT_VERSION_SSM_KEY = '/figgy/deployments/current_version'
CURRENT_VERSION = ssm.get_parameter(CURRENT_VERSION_SSM_KEY)


def handle(event, context):
    return {"statusCode": 200, "body": CURRENT_VERSION}
