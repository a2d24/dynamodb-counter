from typing import Set

import boto3

from reserved import RESERVED_KEYWORDS
from .serializers import serialize, deserialize


class RetriesExceeded(Exception): pass

class Counter:

    def __init__(self, table,
                 variable_name='current_count',
                 endpoint_url=None,
                 region_name=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 **kwargs):

        self.table = table
        self.variable_name = variable_name

        self._named_variables: Set[str] = set()

        self._key = {}

        if len(kwargs) > 2 or len(kwargs) == 0:
            raise ValueError("The key of the counter can only consist of a Hash Key and an optional Sort Key")

        for key_name, key_value in kwargs.items():
            self._key[key_name] = serialize(key_value)

        self._internal_variable_name = self._name_variable(variable_name)

        self._client = boto3.client(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )

    def next(self, increment: int=1, retries=3):

        expression_attribute_names = {}

        if self._named_variables:
            expression_attribute_names.update({f"#{var}": var for var in self._named_variables})

        update_request = dict(
            TableName=self.table,
            Key=self._key,
            UpdateExpression=f"ADD {self._internal_variable_name} :increment",
            ExpressionAttributeValues={
                ':increment': {'N': str(increment)}
            },
            ReturnValues='UPDATED_NEW'
        )

        if expression_attribute_names:
            update_request['ExpressionAttributeNames'] = expression_attribute_names


        response = self._update_item(update_request, retries=retries)
        result = deserialize(response['Attributes'])
        return int(result[self.variable_name])

    def reset(self):
        return self.set(count=0)

    def set(self, count: int, retries=3):
        expression_attribute_names = {}

        if self._named_variables:
            expression_attribute_names.update({f"#{var}": var for var in self._named_variables})

        update_request = dict(
            TableName=self.table,
            Key=self._key,
            UpdateExpression=f"SET {self._internal_variable_name} = :value",
            ExpressionAttributeValues={
                ':value': {'N': str(count)}
            },
            ReturnValues='UPDATED_NEW'
        )

        if expression_attribute_names:
            update_request['ExpressionAttributeNames'] = expression_attribute_names


        response = self._update_item(update_request, retries=retries)
        result = deserialize(response['Attributes'])
        return int(result[self.variable_name])

    def _update_item(self, update_request, retries=0):
        try:
            return self._client.update_item(**update_request)
        except Exception as e:
            print("Retrying", retries)
            if retries == 0:
                print(e)
                raise RetriesExceeded("Could not atomically increment {}. Retries exceeded")
            return self._update_item(update_request=update_request, retries=retries-1)

    def _name_variable(self, variable):
        if variable.upper() not in RESERVED_KEYWORDS:
            return variable

        self._named_variables.add(variable)

        return f"#{variable}"
