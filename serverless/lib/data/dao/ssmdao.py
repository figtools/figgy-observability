from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Union, Dict
from typing import Tuple
from botocore.exceptions import ClientError
from utils.utils import Utils


class SsmDao:
    """
    Should be used for all queries to SSM, has built in pagination, etc.
    """
    max_results = 50  # This is the max according to api docs.

    def __init__(self, boto_ssm_client):
        self._ssm = boto_ssm_client

    @Utils.retry
    def get_parameter_values(self, parameters: List[str], decrypt: bool = False) -> List[Dict]:
        """
        Queries values for a series of parameters, and decrypts SecureStrings if requested.
        Args:
            parameters: List[str]: Parameter names to query values for.
            decrypt: bool: True/False - Attempt to decrypt values during query.

        Returns: List[Dict] - List of Dictionaries container parameter data
        """
        results = []  # type: List[Dict]
        chunks = Utils.chunk_list(parameters, 10)
        for chunk in chunks:
            result = self._ssm.get_parameters(Names=chunk, WithDecryption=decrypt)
            if 'Parameters' in result:
                results = results + result['Parameters']

        return results

    @Utils.retry
    def get_all_parameters(self, prefixes: List[str], option: str = 'Recursive', page: str = None) -> List[dict]:
        """
        Returns all parameters under prefix. Automatically pages recursively then returns full result set
        Args:
            prefixes: List of prefixes to query. E.G. [ '/shared', '/data', '/app' ]
            existing_params: Used in recursive calls to build a total result set
            page: Used in recursive calls if more pages exist.
            option: Must be 'Recursive' or 'OneLevel' - Indicates # of levels below the prefix to recurse.
        Returns: List[dict] -> Parameter details as returned from AWS API

        """
        filters = {
                      'Key': 'Path',
                      'Option': f'{option}',
                      'Values': prefixes
                  },
        total_params = []
        if page:
            params = self._ssm.describe_parameters(ParameterFilters=filters, NextToken=page,
                                                   MaxResults=self.max_results)
        else:
            params = self._ssm.describe_parameters(ParameterFilters=filters, MaxResults=self.max_results)

            Utils.validate(params and 'Parameters' in params,
                                 f"Failed to lookup parameters with prefix: {prefixes}")
        total_params = total_params + params['Parameters']

        if params and 'NextToken' in params:
            total_params = total_params + self.get_all_parameters(prefixes, option=option, page=params['NextToken'])

        return total_params

    @Utils.retry
    def get_parameter_details(self, name: str) -> Dict:
        """
        Get the parameter details for a single parameter. This is extremely inefficient, due to how the AWS API is
        designed, you should probably avoid this.
        :param name: The name of the parameter
        :return: Dict -> Parameter details as returned from AWS API or an empty Dict {} if nothing is found.
        """
        filters = {
            'Key': 'Name',
            'Values': [name]
        }
        next_token = True
        while next_token:
            if isinstance(next_token, str):
                result = self._ssm.describe_parameters(Filters=[filters], NextToken=next_token,
                                                       MaxResults=self.max_results)
            else:
                result = self._ssm.describe_parameters(Filters=[filters], MaxResults=self.max_results)

            params = result.get('Parameters')
            if params:
                return params.pop()
            else:
                next_token = result.get('NextToken')

        return {}

    @Utils.retry
    def get_parameter_with_description(self, name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns a parameter's value and description from its provided name. Returns `None, None` tuple
        if no parameter exists.

        This method paginates to the last page via the SSM API then grabs the last item, which will
        be the current version.

        :param name: The name of the parameter - e.g. /app/foo/bar
        :return: Tuple[value, description] - Value & Description found. None returned if no parameter exists.
        """
        try:
            next_token, result = True, {}

            while next_token:
                if isinstance(next_token, str):
                    result = self._ssm.get_parameter_history(
                        Name=name,
                        WithDecryption=True,
                        NextToken=next_token
                    )
                else:
                    result = self._ssm.get_parameter_history(
                        Name=name,
                        WithDecryption=True
                    )

                next_token = result.get('NextToken')

            history = result.get('Parameters', [])
            if history:
                current_val = history[-1]
                return current_val.get('Value'), current_val.get('Description')
            else:
                return None, None

        except ClientError as e:
            if "ParameterNotFound" == e.response['Error']['Code']:
                return None, None
            else:
                raise

    @Utils.retry
    def get_description(self, name: str) -> Union[str, None]:
        """
        Returns the description for a parameter in parameter store, or None if no description exists.
        :param name: /path/to/parameter
        :return: str - description of the specified parameter, or None if no description exists
        """

        value, desc = self.get_parameter_with_description(name)
        return desc


    @Utils.retry
    def delete_parameter(self, key) -> None:
        """
        Deletes a parameter from PS
        Args:
            key: The PS Name - E.G. /app/demo-time/parameter/abc123

        Returns:

        """
        response = self._ssm.delete_parameter(Name=key)
        Utils.validate(
            response and response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode']
            and response['ResponseMetadata']['HTTPStatusCode'] == 200,
            f"Error deleting key: [{key}] from PS. Please try again.")

    @Utils.retry
    def get_parameter(self, key) -> Optional[str]:
        """
        Gets a parameter, returns None if parameter doesn't exist.
        Args:
            key: The PS Name - E.G. /app/demo-time/parameter/abc123

        Returns: str -> Parameter's value

        """
        try:
            parameter = self._ssm.get_parameter(Name=key, WithDecryption=True)
            return parameter['Parameter']['Value']
        except ClientError as e:
            if "ParameterNotFound" == e.response['Error']['Code']:
                return None
            else:
                raise

    @Utils.retry
    def get_parameter_encrypted_by_version(self, key: str, ps_version: int) -> Optional[str]:
        try:
            parameter_history = self._ssm.get_parameter_history(
                Name=key,
                WithDecryption=False,
                MaxResults=10,
            )
            if len(parameter_history["Parameters"]) > 0:
                parameter = list(filter(lambda x: x["Version"] == ps_version, parameter_history["Parameters"]))
                if parameter:
                    return parameter[0]["Value"]
            else:
                return None
        except ClientError as e:
            if "ParameterNotFound" == e.response['Error']['Code']:
                return None
            else:
                raise

    @Utils.retry
    def get_parameter_encrypted(self, key):
        """
            Returns the parameter without decrypting the value. If parameter isn't encrypted, it returns the value.
        Args:
            key: The PS Name - E.G. /app/demo-time/parameter/abc123

        Returns: str -> encrypted string value of an encrypted parameter.

        """
        try:
            parameter = self._ssm.get_parameter(Name=key, WithDecryption=False)
            return parameter['Parameter']['Value']
        except ClientError as e:
            if "ParameterNotFound" == e.response['Error']['Code']:
                return None
            else:
                raise

    @Utils.retry
    def set_parameter(self, key, value, desc, type, key_id=None) -> None:
        """
        Sets a parameter in PS.
        Args:
            key: The PS Name - E.G. /app/demo-time/parameter/abc123
            value: Value to set
            desc: Description
            type: SecureString or String
            key_id: KMS Key Id to use for encryption if SecureString
        """
        # print(f"Inputting parameter {key} with value: {value} and DESC {desc} and type {type}")
        if key_id:
            self._ssm.put_parameter(
                Name=key,
                Description=desc,
                Value=value,
                Overwrite=True,
                Type=type,
                KeyId=key_id
            )
        else:
            self._ssm.put_parameter(
                Name=key,
                Description=desc,
                Value=value,
                Overwrite=True,
                Type=type
            )
