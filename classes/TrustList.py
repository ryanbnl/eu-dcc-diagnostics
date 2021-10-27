"""This file contains the TrustList abstraction"""

import json

from classes.DigitalSigningCertificate import DigitalSigningCertificate


class TrustList:
    """DCC TrustList"""
    def __init__(self, dsc_dict: dict):
        self._store = dsc_dict

    @classmethod
    def load(cls, path):
        """Loads the trustlist from path"""
        with open(path, mode='r', encoding='utf-8') as file:
            file_text = file.read()
            trust_list_json = json.loads(file_text)
            dsc_dict = dict()
            for item in trust_list_json:
                dsc = DigitalSigningCertificate.parse(item)
                dsc_dict[dsc.kid()] = dsc
            return cls(dsc_dict)

    def find(self, kid: str) -> DigitalSigningCertificate:
        """Finds the DSC in the TL"""
        if kid in self._store:
            return self._store[kid]
        raise UnknownKidError(f"KID `{ kid }` is not in the TrustList")


class UnknownKidError(Exception):
    """KID not found in TrustList error"""
    def __init__(self, message):
        self.message = message
        super().__init__()
