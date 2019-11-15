#!/bin/bash

DEVICE_ID="efa4c8663739c4b380e25164e58ff89bfbd27976"
DEVICE_CA="cert_ecc/rootca.pem"
DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"


HOST="richmondu.com"     #For production testing
#HOST="localhost"        #For development testing with local non-Docker setup
#HOST="192.168.99.100"   #For development testing with local Docker setup 

PORT="8883"
#PORT="30883"            #For development testing with Minikube Kubernetes

USER=""
PASS=""


node device_simulator.js --USE_DEVICE_ID $DEVICE_ID --USE_DEVICE_CA $DEVICE_CA --USE_DEVICE_CERT $DEVICE_CERT --USE_DEVICE_PKEY $DEVICE_PKEY --USE_HOST $HOST --USE_PORT $PORT --USE_USERNAME $USER --USE_PASSWORD $PASS
