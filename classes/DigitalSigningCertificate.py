"""This file contains the DSC abstraction"""

import base64

from cryptography import x509


class DigitalSigningCertificate:
    @classmethod
    def parse(cls, dsc_json):
        """Factory method, parses DSC json and returns instance of this class"""
        instance = cls()
        instance._country = dsc_json["country"]
        instance._kid = dsc_json["kid"]
        raw_data = dsc_json["rawData"]
        cert_bytes = base64.b64decode(raw_data)
        instance._cert = x509.load_der_x509_certificate(cert_bytes)
        return instance

    def certificate(self):
        """Returns the x509 Certificate"""
        return self._cert

    def country(self):
        """Returns the Country"""
        return self._country

    def kid(self):
        """Returns the KID"""
        return self._kid
