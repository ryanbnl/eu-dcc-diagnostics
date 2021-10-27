#!/bin/env python3.9

import sys
from base45 import b45decode
import zlib
from cbor2 import loads
from cose.messages import Sign1Message

# Initialize components
sys.stdin.reconfigure(encoding='utf-8')


def unpack_qr(qr_text):
    compressed_bytes = b45decode(qr_text[4:])
    cose_bytes = zlib.decompress(compressed_bytes)
    cose_message = Sign1Message.decode(cose_bytes)
    cbor_message = loads(cose_message.payload)
    return {
        "COSE": cose_message,
        "JSON": cbor_message[-260][1],
        "CBOR": cbor_message
    }


for line in sys.stdin:
    data = line.rstrip("\r\n").rstrip("\n")
    json = unpack_qr(data)
    print()
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
    print("CBOR")
    print(json["COSE"])
    print()
