#!/bin/env python3.9

import sys
from base45 import b45decode
import zlib
from cbor2 import loads
from cose.messages import Sign1Message

from classes.SchemaValidator import SchemaValidator
from classes.SignatureValidator import SignatureValidator
from classes.TrustList import TrustList, UnknownKidError

# Initialize components
SCHEMA_VALIDATOR = SchemaValidator.create()
SIGNATURE_VALIDATOR = SignatureValidator(TrustList.load("trustlist.json"))
sys.stdin.reconfigure(encoding='utf-8')


def unpack_qr(qr_text):
    compressed_bytes = b45decode(qr_text[4:])
    print("..b45-decode OK")
    cose_bytes = zlib.decompress(compressed_bytes)
    print("..zlib.decompress OK")
    cose_message = Sign1Message.decode(cose_bytes)
    print("..cose.decode OK")
    cbor_message = loads(cose_message.payload)
    print("..cbor.load OK")
    print(cbor_message)
    return {
        "COSE": cose_bytes.hex(),
        "JSON": cbor_message[-260][1]
    }


for line in sys.stdin:
    data = line.rstrip("\r\n").rstrip("\n")
    print()
    print(f"Validating: [{data}]")
    try:
        json = unpack_qr(data)
        # Signature
        result = SIGNATURE_VALIDATOR.validate(bytes.fromhex(json["COSE"]))
        if result["valid"]:
            print("Successfully validated signature!")
        else:
            print("Signature validation failed!")
        # Schema
        json_payload = json["JSON"]
        schema_ver = json_payload['ver']
        result = SCHEMA_VALIDATOR.validate(json_payload)
        if result["valid"]:
            print(f"Successfully validated schema! The file conforms to schema { schema_ver }")
        else:
            print(f"Schema validation failed! The file does not conform to schema { schema_ver }")
    except UnknownKidError as error:
        print("Error! KID not found")
        print(error)
    except Exception as error:
        print("Error! Something went very wrong!")
        print(error)
