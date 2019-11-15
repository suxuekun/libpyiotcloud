#!/bin/bash

DEVICE_ID="2edbe5ed81fe2ac0f2f103db9751885264c98f97"
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


python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID $DEVICE_ID --USE_DEVICE_CA $DEVICE_CA --USE_DEVICE_CERT $DEVICE_CERT --USE_DEVICE_PKEY $DEVICE_PKEY --USE_HOST $HOST --USE_PORT $PORT --USE_USERNAME $USER --USE_PASSWORD $PASS

