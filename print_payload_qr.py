#!/bin/env python3.9

import sys
from base45 import b45decode
import zlib
from cbor2 import loads
from cose.messages import Sign1Message
from pyzbar.pyzbar import decode
from PIL import Image
import argparse

# Initialize components
CLI_PARSER = argparse.ArgumentParser()


def unpack_qr(qr_text):
    compressed_bytes = b45decode(qr_text[4:])
    cose_bytes = zlib.decompress(compressed_bytes)
    cose_message = Sign1Message.decode(cose_bytes)
    cbor_message = loads(cose_message.payload)
    return {
        "COSE": cose_message,
        "JSON": cbor_message[-260][1]
    }


def read_qr_pyzbar(file):
    barcode = decode(Image.open(file))[0]
    return barcode.data.decode("utf-8")


CLI_PARSER.add_argument(
    '--file',
    type=str,
    help='QR file')

args = CLI_PARSER.parse_args()


if args.file is None:
    CLI_PARSER.print_help()
    sys.exit()

print()
print()
data = read_qr_pyzbar(args.file)
print("Raw QR data")
print(data)
json = unpack_qr(data)
print()
print("Hcert")
print(data)
print()
print("JSON")
print(json["JSON"])
print()
print("COSE")
print(json["COSE"])
print()
