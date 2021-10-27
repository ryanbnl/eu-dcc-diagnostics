# Validation tools

This repository contains scripts that help you validate QR codes.

It's hacky, and a warning for Apple Silicon users: the dependencies I use are a mess on your platform. I've given up trying to get it working.

## Initializing

First make sure that you have Python 3.9+ installed and working.

Secondly, install all the dependencies:

    pip3 install -r requirements.txt

Thirdly, update `trustlist.json` using the response from the gateway.

No access to the gateway? Then you can use the German trust list:

https://de.dscg.ubirch.com/trustList/DSC/

Just remove the first line (it's a signature of the document).


# validate_quality_assurance.py

This tool validates the encoding, schema and signature of all the Quality Assurance QR codes.

The QA repository can be found here:

    https://github.com/eu-digital-green-certificates/dcc-quality-assurance

It has the following arguments, both of which are optional and have sensible defaults:

    --repo 'path/to/dcc-quality-assurance'
    --countries 'NL,DE,SE'


# validate_hcert.py

This tool validates the encoding, schema and signature of all the hcert string.
It reads the hcerts from `std-in`, one line per hcert, and validates in serial.

Example (unix-likes)

    cat examples/hcert-examples.txt | python3 validate_hcert.py

Example (windows)

    type examples\hcert-examples.txt | python validate_hcert.py


# qr_to_hcert.py

This little tool converts a QR into a hcert string and dumps that to std-out.

Now you can do this to validate a QR code:

    python qr_to_hcert.py examples/VAC.png | python validate_hcert.py

# hcert_to_qr.py

Takes QRs from std:in; for each line, generates a QR. Dumps all QRs to std:out as base64.
The last QR created is saved as "my.png" in the current folder

    cat examples/hcert.txt | python hcert_to_qr.py

# print_payload_hcert.py

Takes QRs from std:in; for each line, unpacks hcert and dumps all of the output to std:out.

    cat examples/hcert.txt | python print_payload_hcert.py

# print_payload_hcert.py

Takes a QR, parses it, unpacks hcert and dumps all of the output to std:out.

    python print_payload_qr.py --file my.png
