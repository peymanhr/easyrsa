#!/bin/bash
set -e

EASYRSA_DIR="/ca/easyrsa"

if [ ! -d "$EASYRSA_DIR" ] ; then
    
    echo "Initializing Easy-RSA in $EASYRSA_DIR"
    make-cadir $EASYRSA_DIR
    cd $EASYRSA_DIR
    ./easyrsa init-pki
    
    echo "Building CA"
    export EASYRSA_REQ_CN="openvpn-ca"
    ./easyrsa build-ca
    unset EASYRSA_REQ_CN
    
    echo "Generate CRL"
    ./easyrsa gen-crl
    
    echo "Generate tls-crypt"
    openvpn --genkey secret $EASYRSA_DIR/tls-crypt.key

    echo "Generate DH"
    ./easyrsa gen-dh
fi

exec "$@"