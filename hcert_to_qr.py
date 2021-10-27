#!/bin/env python3.9
import base64
import io
import qrcode
import sys


def qr_png_base64(payload_str):
    """
    Generates a QR from the payload
    :param payload_str: QR payload
    :return: QR rendered as a PNG and encoded in an utf-8 base64 string
    """
    qr_code = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=3,
        border=2,
    )
    qr_code.add_data(payload_str)
    qr_image_buffer = io.BytesIO()
    qr_code.make_image().save(qr_image_buffer, format="PNG")
    mybytes = qr_image_buffer.getvalue()

    with open('my.png', 'wb') as my_file:
        my_file.write(mybytes)

    return base64.b64encode(mybytes).decode("utf-8")


for line in sys.stdin:
    data = line.rstrip("\r\n").rstrip("\n")
    qr = qr_png_base64(data)
    print(qr)
