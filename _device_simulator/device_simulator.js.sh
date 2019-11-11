#!/bin/bash

DEVICE_ID="efa4c8663739c4b380e25164e58ff89bfbd27976"
DEVICE_CA="cert_ecc/rootca.pem"
DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"

# HOST="richmondu.com"
PORT="8883"
# HOST="localhost"
HOST="192.168.99.102"
# PORT="30883"

node device_simulator.js --USE_DEVICE_ID $DEVICE_ID --USE_DEVICE_CA $DEVICE_CA --USE_DEVICE_CERT $DEVICE_CERT --USE_DEVICE_PKEY $DEVICE_PKEY --USE_HOST $HOST --USE_PORT $PORT
