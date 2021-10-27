import sys
import pyzbar.pyzbar

from PIL import Image


def read_qr_code(qr_file):
    # https://www.codershubb.com/generate-or-read-qr-code-using-python/
    # https://stackoverflow.com/questions/32908639/open-pil-image-from-byte-file
    image = Image.open(qr_file)
    decoded_image = pyzbar.pyzbar.decode(image)
    return decoded_image[0].data.decode()


if len(sys.argv) != 2:
    raise ValueError('File missing!')

file = sys.argv[1]
h_cert = read_qr_code(file)
print(h_cert)
