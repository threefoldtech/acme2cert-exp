# taken from certbot and certbot/acme
# see https://github.com/certbot/certbot/blob/master/certbot/certbot/crypto_util.py
# and https://github.com/certbot/certbot/blob/master/acme/acme/crypto_util.py


from OpenSSL import crypto


class Error(Exception):
    pass


def make_key(bits=1024, key_type="rsa", elliptic_curve=None):
    """Generate PEM encoded RSA|EC key.
    :param int bits: Number of bits if key_type=rsa. At least 1024 for RSA.
    :param str ec_curve: The elliptic curve to use.
    :returns: new RSA or ECDSA key in PEM form with specified number of bits
              or of type ec_curve when key_type ecdsa is used.
    :rtype: str
    """
    if key_type == 'rsa':
        if bits < 1024:
            raise Error("Unsupported RSA key length: {}".format(bits))

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, bits)
    elif key_type == 'ecdsa':
        try:
            name = elliptic_curve.upper()
            if name in ('SECP256R1', 'SECP384R1', 'SECP521R1'):
                _key = ec.generate_private_key(
                    curve=getattr(ec, elliptic_curve.upper(), None)(),
                    backend=default_backend()
                )
            else:
                raise Error("Unsupported elliptic curve: {}".format(elliptic_curve))
        except TypeError:
            raise Error("Unsupported elliptic curve: {}".format(elliptic_curve))
        except UnsupportedAlgorithm as e:
            raise e from Error(str(e))
        _key_pem = _key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption()
        )
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, _key_pem)
    else:
        raise Error("Invalid key_type specified: {}.  Use [rsa|ecdsa]".format(key_type))
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, key)


def make_csr(private_key_pem, domains, email=None, must_staple=False, filetype=crypto.FILETYPE_ASN1):
    """Generate a CSR containing a list of domains as subjectAltNames.
    :param buffer private_key_pem: Private key, in PEM PKCS#8 format.
    :param list domains: List of DNS names to include in subjectAltNames of CSR.
    :param bool must_staple: Whether to include the TLS Feature extension (aka
        OCSP Must Staple: https://tools.ietf.org/html/rfc7633).
    :returns: buffer PEM-encoded Certificate Signing Request.
    """
    private_key = crypto.load_privatekey(
        crypto.FILETYPE_PEM, private_key_pem)
    csr = crypto.X509Req()
    extensions = [
        crypto.X509Extension(
            b'subjectAltName',
            critical=False,
            value=', '.join('DNS:' + d for d in domains).encode('ascii')
        ),
    ]
    if must_staple:
        extensions.append(crypto.X509Extension(
            b"1.3.6.1.5.5.7.1.24",
            critical=False,
            value=b"DER:30:03:02:01:05"))
    csr.add_extensions(extensions)
    csr.set_pubkey(private_key)
    csr.set_version(2)
    csr.sign(private_key, 'sha256')
    if email:
        csr.get_subject().emailAddress = email
    return crypto.dump_certificate_request(
        filetype, csr)
