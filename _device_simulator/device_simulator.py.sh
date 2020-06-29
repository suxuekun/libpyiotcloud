#!/bin/bash

##########################################################
#
# Device credentials
#
##########################################################
#
# For new devices, set the following values:
# Application will now generate USERNAME AND PASSWORD based on DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD
#
# DEVICE_ID        - should match UUID during device registration      
# DEVICE_SERIAL    - should match Serial Number during device registration 
# DEVICE_MACADD    - should match POE MAC Address during device registration 
# DEVICE_SECRETKEY - [CONFIDENTIAL] please ASK ME directly or check the SKYPE GROUP
#
# For existing devices (backward compatibility), set the following values:
#
# DEVICE_ID        - should match UUID during device registration   
# USER             - should match UUID during device registration   
# PASS             - should match Serial Number during device registration
# DEVICE_SECRETKEY - [CONFIDENTIAL] please ASK ME directly or check the SKYPE GROUP
#
##########################################################

DEVICE_ID="PH80XXRR06262017"
DEVICE_SECRETKEY="warol8fmesdl23pse039tfyawetagtoi"

# For new devices
DEVICE_SERIAL="00023"
DEVICE_MACADD="CD:76:27:15:F9:56"

# For existing devices (backward compatibility)
USER=""
PASS=""



##########################################################
#
# Device certificates
#
##########################################################

DEVICE_CA="cert_ecc/rootca.pem"
DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"



##########################################################
#
# Backend message broker
#
##########################################################
#
# DEV  environment             - set HOST to dev.brtchip-iotportal.com
# TEST environment             - set HOST to test.brtchip-iotportal.com
# PROD environment             - set HOST to prod.brtchip-iotportal.com
#
# LOCAL non-docker environment - set HOST to localhost
# LOCAL docker environment     - set HOST to 192.168.99.100 [double check with docker-machine ip]
# LOCAL docker environment Mac - set HOST to localhost
#
# KUBERNETES environment       - set PORT to 30883
#
##########################################################

PORT="8883"
HOST="localhost"


python3 device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID $DEVICE_ID --USE_DEVICE_CA $DEVICE_CA --USE_DEVICE_CERT $DEVICE_CERT --USE_DEVICE_PKEY $DEVICE_PKEY --USE_HOST $HOST --USE_PORT $PORT --USE_DEVICE_SERIAL $DEVICE_SERIAL --USE_DEVICE_MACADD $DEVICE_MACADD --USE_DEVICE_SECRETKEY $DEVICE_SECRETKEY 


# python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID $DEVICE_ID --USE_DEVICE_CA $DEVICE_CA --USE_DEVICE_CERT $DEVICE_CERT --USE_DEVICE_PKEY $DEVICE_PKEY --USE_HOST $HOST --USE_PORT $PORT --USE_DEVICE_SERIAL $DEVICE_SERIAL --USE_DEVICE_MACADD $DEVICE_MACADD --USE_DEVICE_SECRETKEY $DEVICE_SECRETKEY --USE_USERNAME $USER --USE_PASSWORD $PASS


