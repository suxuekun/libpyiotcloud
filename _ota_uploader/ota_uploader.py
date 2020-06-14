import argparse
import binascii
import json
import os
import sys
from s3_client import s3_client



###################################################################################
# Utilities
###################################################################################

def print_json(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

def bin_compute_checksum(contents):
    return binascii.crc32(contents)

def bin_read_file(filename):
    try:
        f = open(filename, "rb")
        contents = f.read()
        f.close()
        return contents
    except:
        pass
    return None

def json_read_file(filename):
    try:
        f = open(filename, "r")
        contents = f.read()
        f.close()
        return json.loads(contents)
    except:
        pass
    return None


###################################################################################
# Logic
###################################################################################

def get_firmware(filename_desc, filename_bin):

    # Read new firmware description
    desc = json_read_file(filename_desc)
    if desc is None:
        print("Error: Firmware description not found! {}".format(filename_desc))
        return None, None
    #print_json(desc)
    if desc.get("version") is None:
        print("Error: Firmware description not valid!")
        return None, None
    if desc.get("date") is None:
        print("Error: Firmware description not valid!")
        return None, None
    if desc.get("location") is None:
        print("Error: Firmware description not valid!")
        return None, None
    if desc.get("size") is None:
        print("Error: Firmware description not valid!")
        return None, None
    if desc.get("checksum") is None:
        print("Error: Firmware description not valid!")
        return None, None
    if desc.get("description") is None:
        print("Error: Firmware description not valid!")
        return None, None

    # Read new firmware binary
    bin = bin_read_file(filename_bin)
    if bin is None:
        print("Error: Firmware binary not found! {}".format(filename_bin))
        return None, None

    # Verify the checksum
    checksum = bin_compute_checksum(bin)
    if checksum != desc["checksum"]:
        print("Error: Checksum does not match! {} {}".format(checksum, desc["checksum"]))
        return None, None

    print_json(desc)
    return desc, bin


def upload_firmware(client, doc, desc, bin):
    if doc["ft900"]["latest"] != desc["version"]:
        doc["ft900"]["latest"] = desc["version"]
        doc["ft900"]["firmware"].insert(0, desc)
    else:
        doc["ft900"]["firmware"][0] = desc
    #print_json(doc)
    return client.update_device_firmware_updates(json.dumps(doc, indent=2), bin, desc["location"])


def verify_upload(client, doc, desc, bin):
    result, doc_new = client.get_device_firmware_updates()
    if not result:
        print("Error: Could not read device firmware updates file!")
        return

    if doc["ft900"]["latest"] != doc_new["ft900"]["latest"]:
        print("Error: Read latest firmware incorrect! 1")
        return
    if doc["ft900"]["firmware"][0]["version"] != doc_new["ft900"]["firmware"][0]["version"]:
        print("Error: Read latest firmware incorrect! 2")
        return
    if doc["ft900"]["latest"] != doc_new["ft900"]["firmware"][0]["version"]:
        print("Error: Read latest firmware incorrect! 3")
        return
    if doc["ft900"]["firmware"][0]["location"] != doc_new["ft900"]["firmware"][0]["location"]:
        print("Error: Read latest firmware incorrect! 4")
        return

    result, firmware_bin = client.get_firmware(doc_new["ft900"]["firmware"][0]["location"])
    if not result:
        print("Error: Could not read new firmware")
        return
    checksum = bin_compute_checksum(firmware_bin)
    if checksum != doc_new["ft900"]["firmware"][0]["checksum"]:
        print("Error: Checksum does not match! {} {}".format(checksum, desc["checksum"]))
        return None, None

    return True


###################################################################################
# Main entry point
###################################################################################

def main(args):

    # Get firmware list from AWS S3
    client = s3_client(args.USE_PASSCODE)
    result, doc = client.get_device_firmware_updates()
    if not result:
        print("Error: Could not read device firmware updates file!")
        return

    # Verify the new firmware
    desc, bin = get_firmware(args.USE_FIRMWARE_DESC, args.USE_FIRMWARE_BIN)
    if not desc:
        print("Error: New firmware is not valid!")
        return

    # Upload new firmware
    result = upload_firmware(client, doc, desc, bin)
    if not result:
        print("Uploading of new firmware failed!")
        return
    print("Uploading of new firmware was successful!")

    # Verify uploaded firmware
    result = verify_upload(client, doc, desc, bin)
    if not result:
        print("Verifying of uploading new firmware failed!")
        return
    print("Verifying of uploading new firmware was successful!")

    # Open Google Chrome
    try:
        os.system("start chrome https://ft900-iot-portal.s3.amazonaws.com/latest_firmware_updates.json")
    except:
        pass
    print("Downloading file via Google Chrome!")


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--USE_PASSCODE',      required=True, default='', help='')
    parser.add_argument('--USE_FIRMWARE_BIN',  required=True, default='', help='New firmware binary')
    parser.add_argument('--USE_FIRMWARE_DESC', required=True, default='', help='New firmware description')
    return parser.parse_args(argv)


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])
    print("")
    print("-------------------------------------------------------")
    print("Copyright (C) Bridgetek Pte Ltd")
    print("-------------------------------------------------------")
    print("Welcome to IoT Portal OTA Firmware Uploader...")
    print("")
    print("This application uploads OTA firmware to IoT Portal")
    print("-------------------------------------------------------")
    print("")

    print("USE_FIRMWARE_BIN={}".format(args.USE_FIRMWARE_BIN))
    print("USE_FIRMWARE_DESC={}".format(args.USE_FIRMWARE_DESC))
    main(args)


