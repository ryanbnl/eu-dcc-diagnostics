"""This file contains the schema validator abstraction"""

import json
from datetime import datetime

from jschon import JSONSchema, Evaluator, Catalogue, OutputFormat, JSON

# initializing the json schema catalogue
Catalogue.create_default_catalogue('2020-12')

SCHEMAS = ["1.0.0", "1.0.1", "1.1.0", "1.2.0", "1.2.1", "1.3.0"]


class SchemaValidator:
    """Schema validator"""
    def __init__(self):
        self._schemas = dict()

    @classmethod
    def create(cls):
        """factory"""
        instance = cls()
        for schema_key in SCHEMAS:
            instance.load_schema(schema_key, f"schemas/{schema_key}.json")
        return instance

    @staticmethod
    def _fix_python_dates(obj):
        """converts strings python parses as dates back to strings"""
        # Convert the data in SC into a string
        if "t" in obj and obj["t"] is not None:
            for item in obj["t"]:
                if "sc" in item:
                    if isinstance(item["sc"], datetime):
                        item["sc"] = item["sc"].isoformat()
                if "dr" in item:
                    if isinstance(item["dr"], datetime):
                        item["dr"] = item["dr"].isoformat()
        return obj

    def load_schema(self, version: str, path: str) -> None:
        """Loads the given schema from the given path"""
        with open(path, 'r') as file:
            schema = JSONSchema(json.load(file)).validate()
            self._schemas[version] = Evaluator(schema)

    # Validates <json> against the schema with version <version>
    # returns:
    # {
    #   valid: bool,
    #   errors: [{
    #     'instanceLocation': 'rel-path',
    #     'keywordLocation': 'rel-path',
    #     'absoluteKeywordLocation': 'uri',
    #     'error': 'message'
    #   }]
    # }
    def validate(self, dgc_json: json):
        """Validates the dcc against the given schema version in the json"""
        # version is in json["ver"], but will be passed in as you
        # might wanna validate against multiple versions
        schema: Evaluator = self._schemas[dgc_json["ver"]]
        return schema.evaluate_instance(JSON(dgc_json), OutputFormat.BASIC)

    # Validates <json> against the schema with version <version>
    # returns:
    # {
    #   valid: bool,
    #   errors: [{
    #     'instanceLocation': 'rel-path',
    #     'keywordLocation': 'rel-path',
    #     'absoluteKeywordLocation': 'uri',
    #     'error': 'message'
    #   }]
    # }
    def validate_dcc(self, dcc: object, version):
        """Validates the dcc against the given schema version"""
        # version is in json["ver"], but will be passed in as you
        # might wanna validate against multiple versions
        schema: Evaluator = self._schemas[version]
        # NOTE: JSON Schema doesn't support datetime objects,
        # so convert 't' -> 'sc' into a date/time string
        dcc = self._fix_python_dates(dcc)
        try:
            return schema.evaluate_instance(JSON(dcc), OutputFormat.BASIC)
        except TypeError as error:
            raise error

    # Validates <json> against the schema against all supported versions
    # returns:
    # [{
    #   valid: bool,
    #   errors: [{
    #     'instanceLocation': 'rel-path',
    #     'keywordLocation': 'rel-path',
    #     'absoluteKeywordLocation': 'uri',
    #     'error': 'message'
    #   }]
    # }, ..]
    def validate_all(self, dgc_json: json):
        """Validates the dcc against all schema versions"""
        result = dict()
        for schema_key in SCHEMAS:
            schema: Evaluator = self._schemas[schema_key]
            result[schema_key] = schema.evaluate_instance(JSON(dgc_json), OutputFormat.BASIC)
        return result
