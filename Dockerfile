FROM ubuntu:24.04
LABEL org.opencontainers.image.authors="phooshmand@gmail.com"
LABEL version="1.0"

RUN <<EOF
apt-get update
apt-get install -y easy-rsa openvpn python3 python3-pip
rm -rf /var/lib/apt/lists/*
EOF

COPY makeovpn /makeovpn
RUN pip install --break-system-packages -r /makeovpn/requirements.txt
RUN chmod +x /makeovpn/generate.py

WORKDIR /ca
COPY entrypoint.sh /

ENV EASYRSA_ALGO=rsa
ENV EASYRSA_KEY_SIZE=2048
ENV EASYRSA_CURVE=secp384r1
ENV EASYRSA_NO_PASS=1
ENV EASYRSA_CA_EXPIRE=10000
ENV EASYRSA_CERT_EXPIRE=10000
ENV EASYRSA_CRL_DAYS=10000
ENV EASYRSA_REQ_COUNTRY="US"
ENV EASYRSA_REQ_PROVINCE="California"
ENV EASYRSA_REQ_CITY="Los Angles"
ENV EASYRSA_REQ_EMAIL="foo@bar.net"
ENV EASYRSA_REQ_OU="foobar"
ENV EASYRSA_OPENSSL="openssl"
ENV EASYRSA_BATCH=1

ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]
