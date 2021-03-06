# coding: utf-8

from typing import List, Optional
from decimal import Decimal, Inexact

import boto3
from .store import Store
from hikidashi.models.item import Item


class DynamoStore(Store):
    def __init__(self, table_name: str, endpoint_url: str=None):
        self.dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
        if not check_table_exists(self.dynamodb, table_name):
            init_table(self.dynamodb, table_name)
        self.table = self.dynamodb.Table(table_name)

    def get_items(self, **kwargs) -> List[Item]:
        items = self.table.scan()
        if 'Items' not in items:
            return []
        return [Item(**load_from_dynamo(i)) for i in items['Items']]

    def get_item(self, key: str) -> Optional[Item]:
        item = self.table.get_item(
            Key={'key': key}
        )
        if "Item" not in item:
            return None
        return Item(**load_from_dynamo(item['Item']))

    def put_item(self, item: Item = None):
        self.table.put_item(
            Item=dump_to_dynamo(item.to_dict())
        )

    def truncate(self):
        self.table.delete()


def check_table_exists(dynamodb, table_name):
    tables = [t.name for t in dynamodb.tables.all()]
    return table_name in tables


def init_table(dynamodb, table_name, read_capacity=10, write_capacity=5):
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "key", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "key", "AttributeType": "S"}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': read_capacity,
            'WriteCapacityUnits': write_capacity
        },
    )


def dump_to_dynamo(values: dict) -> dict:
    """DynamoDBに適した形に変換する"""
    values = values.copy()
    for k in values.keys():
        v = values[k]
        # int, floatはDecimalに変換
        if isinstance(v, (int, float)):
            values[k] = Decimal(f'{v:.5f}')  # boto3 内で精度が保証できないとエラーになるので適度にまるめる
            continue
        # 空文字列の場合はNoneに
        if v == "":
            values[k] = None
            continue
    return values


def load_from_dynamo(values: dict) -> dict:
    """DynamoDBの形式から復元する"""
    values = values.copy()
    for k in values.keys():
        v = values[k]
        if isinstance(v, Decimal):
            if v == int(v):
                values[k] = int(v)
            else:
                values[k] = float(v)
    return values
