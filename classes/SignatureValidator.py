"""This file contains the signature validator abstraction"""

import base64
import json

from cose.headers import KID
from cose.keys.keyops import VerifyOp
from cose.messages import Sign1Message
from cose.keys import CoseKey
from cose.algorithms import Es256, Ps256
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.keys.keyparam import KpKty, KpKeyOps
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN
from cose.keys.curves import P256
from cose.exceptions import CoseException
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.utils import int_to_bytes

from classes.TrustList import TrustList


class SignatureValidator:
    """Validate COSE signatures"""
    def __init__(self, trust_list: TrustList):
        self._trust_list = trust_list

    def validate(self, payload: bytes):
        """Validates the signature, or returns the errors"""
        try:
            message = Sign1Message.decode(payload)
            kid = self._get_kid(message)
            print(f"KID = {kid}")
            dsc = self._trust_list.find(kid)
            cert: x509.base = dsc.certificate()
            if cert is None:
                return {
                    "valid": False,
                    "error": {
                        "type": "TRUST-LIST",
                        "message": f"KID {kid} not found in the trust-list"
                    }
                }
            message.key = self._get_key(cert)
            if message.verify_signature():
                return {
                    "valid": True,
                    "error": None
                }
            return {
                "valid": False,
                "error": "Invalid signature! Reason: unknown."
            }
        except UnicodeDecodeError as err:
            return {
                "valid": False,
                "error": {
                    "type": "UNICODE",
                    "message": err
                }
            }
        except json.decoder.JSONDecodeError as err:
            return {
                "valid": False,
                "error": {
                    "type": "JSON",
                    "message": err
                }
            }
        except (CoseException, AttributeError, TypeError) as err:
            return {
                "valid": False,
                "error": {
                    "type": "COSE",
                    "message": err
                }
            }

    @staticmethod
    def _get_kid(message) -> str:
        """Returns the KID from the message"""
        if KID in message.phdr.keys():
            return base64.b64encode(message.phdr[KID]).decode("UTF-8")
        return base64.b64encode(message.uhdr[KID]).decode("UTF-8")

    @staticmethod
    def _get_key(cert: x509.base) -> CoseKey:
        """Returns the CoseKey"""
        if isinstance(cert.public_key(), rsa.RSAPublicKey):
            return CoseKey.from_dict(
                {
                    KpKeyOps: [VerifyOp],
                    KpKty: KtyRSA,
                    KpAlg: Ps256,  # RSSASSA-PSS-with-SHA-256-and-MFG1
                    RSAKpE: int_to_bytes(cert.public_key().public_numbers().e),
                    RSAKpN: int_to_bytes(cert.public_key().public_numbers().n)
                }
            )
        elif isinstance(cert.public_key(), ec.EllipticCurvePublicKey):
            return CoseKey.from_dict(
                {
                    KpKeyOps: [VerifyOp],
                    KpKty: KtyEC2,
                    EC2KpCurve: P256,  # Ought o be pk.curve - but the two libs clash
                    KpAlg: Es256,  # ecdsa-with-SHA256
                    EC2KpX: int_to_bytes(cert.public_key().public_numbers().x),
                    EC2KpY: int_to_bytes(cert.public_key().public_numbers().y)
                }
            )
        else:
            raise Exception(f"Algorithm unsupported: { cert.signature_algorithm_oid }")
