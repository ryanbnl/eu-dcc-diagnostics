"""This file contains the DCC abstraction"""

import json

from SchemaValidator import SchemaValidator
from SignatureValidator import SignatureValidator


class DigitalCovidCertificate:
    """Digital Covid Certificate"""

    # Shared SchemaValidator instance
    _schema_validator: SchemaValidator = None

    # Shared SignatureValidator instance
    _signature_validator: SignatureValidator = None

    # Static initializer: CALL BEFORE FIRST USE
    @staticmethod
    def initialize(schema_validator: SchemaValidator, signature_validator):
        """Initializes this type for usage (for all instances)"""
        _schema_validator = schema_validator
        _signature_validator = signature_validator

    # self = this, schema_provider = dictionary[version]=>json-schema-instance
    def __init__(self, dgc_json: str, dgc_cose: bytes):
        self._dgc_json: str = dgc_json
        self._dgc_cose: str = dgc_cose

    @classmethod
    def parse_from_test_json(cls, path: str):
        """Parses the DCC content from the T-systems test case JSON format"""
        with open(path, 'r') as file:
            test_file_json = json.load(file)
            dgc_json = test_file_json["JSON"]
            dgc_cose = bytes.fromhex(test_file_json["COSE"])
            return cls(None, dgc_json, dgc_cose)

    def validate_signature(self) -> bool:
        """Validates the signature"""
        return self._signature_validator.validate(self._dgc_cose)

    def validate_schema(self):
        """Validates the schema"""
        version = self._dgc_json["ver"]
        result = self._schema_validator.validate(self._dgc_json, version)
        return {
            'valid': result["valid"],
            'schema': version,
            'errors': result["errors"]
        }
