import base64
import json

from django.http import JsonResponse
from acme.helper import convert_asn1_to_pem, load_config, logger_setup

from csr import make_key, make_csr
from zerossl_ca_handler import CAhandler


HEADER_NAME = "X-API-KEY"
METHOD_NOT_ALLOWED = JsonResponse(
    status=400, data={"status": 405, "message": "Method Not Allowed', 'detail': 'Wrong request type. Expected HEAD."}
)

CONFIG = load_config()
DEBUG = CONFIG.getboolean("DEFAULT", "debug", fallback=False)
# initialize logger
LOGGER = logger_setup(DEBUG)

# for zerossl
KEY_SIZE = 2048


def format_response(code, message):
    return JsonResponse(status=code, data={"status": code, "message": message})


def verify(request):
    if HEADER_NAME not in request.headers:
        raise ValueError(f"{HEADER_NAME} is missing")

    api_key = request.headers[HEADER_NAME]
    api_keys = []

    if CONFIG.has_section("api"):
        api_keys = CONFIG["api"].values()

    if api_key not in api_keys:
        raise PermissionError("permission denied")


def get_csr(domains, email):
    key = make_key(KEY_SIZE)
    return key, make_csr(key, domains, email)


def prefetch(request):
    try:
        # better be a middleware?
        verify(request)
    except (ValueError, PermissionError) as e:
        return format_response(400, str(e))

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            data = {}

        domains = data.get("domains")
        email = data.get("email")
        if not domains:
            return format_response(400, f"argument of 'domains' is missing")

        handler = CAhandler(DEBUG, LOGGER)
        key, csr = get_csr(domains, email)
        encoded_csr = base64.b64encode(csr)
        try:
            bundle, raw = handler.prefetch(domains, encoded_csr)
        except RuntimeError as e:
            return format_response(400, str(e))

        return JsonResponse(
            status=200,
            data={
                "private_key": key.decode(),
                "fullchain": bundle,
                "cert": convert_asn1_to_pem(base64.b64decode(raw)).decode(),
                "csr": encoded_csr.decode(),
            },
        )
    else:
        return METHOD_NOT_ALLOWED
