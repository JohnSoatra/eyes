import requests

# Suppress only the single warning from urllib3 needed.
try:
    requests.packages.urllib3.disable_warnings()
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

except AttributeError:
    # no pyopenssl support used / needed / available
    pass
