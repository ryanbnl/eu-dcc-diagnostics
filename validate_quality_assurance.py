#!/bin/env python3.9

import os
import util
import argparse
import sys
import zlib
import re
import zxing
import json

from datetime import datetime
from pyzbar.pyzbar import decode
from PIL import Image
from base45 import b45decode
from cbor2 import loads
from cose.messages import Sign1Message
from classes.SchemaValidator import SchemaValidator
from classes.SignatureValidator import SignatureValidator
from classes.TrustList import TrustList, UnknownKidError

# Initialize components
SCHEMA_VALIDATOR = SchemaValidator.create()
SIGNATURE_VALIDATOR = SignatureValidator(TrustList.load("trustlist.json"))
CLI_PARSER = argparse.ArgumentParser()

# Global state
SCRIPT_NAME = 'validate_quality_assurance.py'
ALLOWED_EXT = ['.PNG']
SCHEMA_FILE_PATH = 'DGC.combined-schema.json'

# Various flags which need to be turned into
VERBOSE = True
VALID_IF_ANY_VALID_CASE_FOUND = True

EXPECTED_FAILURES = 0


def validate(path):
    results = dict()
    for country in countries:
        validate_country(path, country, results)
    return results


def date_time_serializer(obj):
    # It's sad that this is needed, but hey!
    if isinstance(obj, datetime):
        return obj.isoformat()
    return None


def unpack_qr_text(qr_text):
    compressed_bytes = b45decode(qr_text[4:])
    cose_bytes = zlib.decompress(compressed_bytes)
    cose_message = Sign1Message.decode(cose_bytes)
    cbor_message = loads(cose_message.payload)
    print(cbor_message)
    payload_object = cbor_message[-260][1]
    return {
        "COSE": cose_bytes.hex(),
        "CBOR": cbor_message,
        "COSE_MESSAGE": cose_message,
        "PAYLOAD_OBJECT": payload_object,
        "PAYLOAD_JSON": json.dumps(payload_object, default=date_time_serializer)
    }


def validate_country(path, country, results):
    print(f"Validating {country}..")
    results[country] = dict()
    results[country]["passed"] = list()
    results[country]["failed"] = list()
    results[country]["skipped"] = list()
    # try:
    files = [f for f in util.walk_path(path, country)
             if os.path.splitext(f)[1].upper() in ALLOWED_EXT]
    if len(files) == 0:
        results[country]["valid"] = False
        results[country]["exception"] = "No test cases found."
        return
    for file in files:
        validate_png(country, file, results)
    if len(results[country]["failed"]) > 0:
        results[country]["valid"] = False
    else:
        results[country]["valid"] = True


def get_version(file):
    pattern = re.compile("\\d\\.\\d\\.\\d")
    result = pattern.search(file)
    return result.group(0)


def read_qr_zxing(file):
    reader = zxing.BarCodeReader()
    barcode = reader.decode(file)
    return barcode.raw


def read_qr_pyzbar(file):
    barcode = decode(Image.open(file))[0]
    return barcode.data.decode("utf-8")


def validate_png(country, file, results):
    print(f"  File: {file}")
    unpacked = dict()
    try:
        version = get_version(file)
        qr_data = read_qr_pyzbar(file)
        if qr_data is None or qr_data == '':
            results[country]["failed"].append({
                "file": file,
                "exception": "Unable to read QR",
                "json": "",
                "cbor": "",
                "cose_msg": ""
            })
            return
        compressed_bytes = b45decode(qr_data[4:])
        cose_payload = zlib.decompress(compressed_bytes)
        unpacked = unpack_qr_text(qr_data)
        result_schema_val = SCHEMA_VALIDATOR.validate_dcc(unpacked["PAYLOAD_OBJECT"], version)
        result_sig_val = SIGNATURE_VALIDATOR.validate(cose_payload)
        if result_schema_val["valid"] and result_sig_val["valid"]:
            results[country]["passed"].append(file)
        else:
            results[country]["failed"].append({
                "file": file,
                "schema": result_schema_val,
                "signature": result_sig_val,
                "json": unpacked["PAYLOAD_JSON"]
            })
    except UnknownKidError as e:
        result = {
            "file": file,
            "exception": e
        }
        results[country]["failed"].append(result)
    except Exception as e:
        #
        result = {
            "file": file,
            "exception": e
        }
        if "PAYLOAD_JSON" in unpacked:
            result["json"] = unpacked["PAYLOAD_JSON"]
        if "CBOR" in unpacked:
            result["cbor"] = unpacked["CBOR"]
        if "CBOR" in unpacked:
            result["cose_msg"] = unpacked["COSE_MESSAGE"]
        results[country]["failed"].append(result)


def info(message):
    if VERBOSE:
        print(message)


CLI_PARSER.add_argument(
    '--repo',
    type=str,
    help='Path to the repository containing the test cases',
    default="..\\dcc-quality-assurance")
CLI_PARSER.add_argument(
    '--countries',
    type=str,
    nargs="?",
    help='Optional string containing a comma-separated list of countries,' +
    ' e.g. "NL,DE,ES"')

args = CLI_PARSER.parse_args()

if args.repo is None:
    CLI_PARSER.print_help()
    sys.exit()

root_directory = args.repo
if args.countries is None:
    print(root_directory)
    countries = util.list_country_directories(root_directory)
else:
    countries = args.countries.split(",")

print(f"Starting validation of the following countries: {countries}")
validation_results = validate(root_directory)
print("Validation complete.")
print("Validation results:")
for c in sorted(validation_results.keys()):
    total_passed = len(validation_results[c]["passed"])
    total_skipped = len(validation_results[c]["skipped"])
    TOTAL_FAILED = len(validation_results[c]["failed"])
    if validation_results[c]["valid"]:
        print(
            f"  {c} ✅ | passed {total_passed} failed {TOTAL_FAILED} skipped" +
            " {total_skipped}.")
    else:
        print(
            f"  {c} ❌ | passed {total_passed} failed {TOTAL_FAILED} skipped" +
            " {total_skipped}.")

print()

TOTAL_FAILED = 0

for c in sorted(validation_results.keys()):
    TOTAL_FAILED = TOTAL_FAILED + len(validation_results[c]["failed"])
    if not validation_results[c]["valid"]:
        print("Error details")
        print()
        for e in validation_results[c]["failed"]:
            print(f"{ c }")
            print(f"  {e['file']}")
            if "exception" in e:
                print("    General error:")
                print(f"      { e['exception'] }")
            if "schema" in e and not e["schema"]["valid"]:
                print("    Schema error:")
                for se in e["schema"]["errors"]:
                    print(f'      { se["error"] }')
            if "signature" in e and not e["signature"]["valid"]:
                print("    Signature error:")
                print(f"      { e['signature']['error']['message'] }")
            if "json" in e:
                print("    JSON:")
                print(f"      {e['json']}")
            if "cbor" in e:
                print("    CBOR:")
                print(f"      {e['cbor']}")
            if "cose_msg" in e:
                print("    COSE message:")
                print(f"      {e['cose_msg']}")

if TOTAL_FAILED == 0:
    print("Everything succeeded!")
