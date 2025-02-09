# easyrsa

## Start a CA
docker compose up -d

## Generate server certificate
docker compose exec easyrsa bash -c 'cd easyrsa && ./easyrsa build-server-full server1'

## Generate client certificate
docker compose exec easyrsa bash -c 'cd easyrsa && ./easyrsa build-client-full client1'

## Generate ovpn client files
docker compose exec easyrsa /makeovpn/generate.py

## Inspect crt files
docker compose exec easyrsa bash -c 'cd easyrsa && openssl x509 -in pki/ca.crt -text -noout'
