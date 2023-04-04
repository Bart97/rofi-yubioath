from ykman.device import list_all_devices, scan_devices
from yubikit.core.smartcard import SmartCardConnection
import yubikit.oath
import subprocess
import pyperclip

def creds_to_string_dict(creds):
    converted = {}
    for cred, code in creds.items():
        if code is not None:
            converted[cred.id.decode("utf-8")] = code.value
        else:
            converted[cred.id.decode("utf-8")] = ""
    return converted

def get_longest_cred_name(credDict):
    return len(max(credDict.keys(), key=len))

def build_creds_string(credDict):
    longestCred = get_longest_cred_name(credDict)
    credsString = ''
    for cred, code in credDict.items():
        credsString += cred.ljust(longestCred, ' ') + ','
        credsString += code
        credsString += '|'
    credsString = credsString[:-1]
    return credsString

device, info = list_all_devices()[0]
connection = device.open_connection(SmartCardConnection)

session = yubikit.oath.OathSession(connection)
creds = session.calculate_all()

credDict = creds_to_string_dict(creds)

credsString = build_creds_string(credDict)

result = subprocess.run(
        [
            'rofi',
            '-dmenu',
            '-sep', "|",
            '-display-column-separator', ',',
            '-display-columns', '1,2',
            '-no-custom',
            '-format', 'i'
        ], input=credsString,
        capture_output=True, text=True)

if result.returncode == 0:
    try:
        selectedCred = int(result.stdout)
        code = session.calculate_code(list(creds.keys())[selectedCred])
        pyperclip.copy(code.value)
    except ValueError:
        pass

