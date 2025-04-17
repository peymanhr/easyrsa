#!/usr/bin/env python3

"""
Author: Peyman Hooshmandi Raad
Email: phooshmand@gmail.com
Description: Generate ovpn client files from easyrsa.

License: GNU General Public License v3.0 (GPL-3.0)
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import json
import yaml
import re
import shutil
import zipfile
from glob import glob
from jinja2 import Environment, FileSystemLoader

def is_client_cert(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return "Client" in f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

easyrsa_dir = "/ca/easyrsa"
issued_dir = f"{easyrsa_dir}/pki/issued"
clients_dir = "/openvpn/clients"

with open(f"{easyrsa_dir}/tls-crypt.key") as f:
    tls_crypt_key = f.read()

with open(f"{easyrsa_dir}/pki/ca.crt") as f:
    ca = f.read()

with open("/openvpn/config.yaml") as f:
    config = yaml.safe_load(f)

try: 
    with open("/openvpn/clients.json") as f:
        clients = json.load(f)
except FileNotFoundError as e:
    clients = None    

client_certs = [
    f for f in os.listdir(issued_dir)
    if f.endswith(".crt") and is_client_cert(os.path.join(issued_dir, f))
]

env = Environment(loader=FileSystemLoader("/makeovpn/templates"))

# Delete all client ovpn files
for file in glob(f'{clients_dir}/*.zip'):
    os.remove(file)

# Filter client certs with clients.json
client_certs = [cert for cert in client_certs if cert.split(".")[0] in clients] if clients else client_certs

for cert in client_certs:
    
    cn = cert.split(".")[0]
    
    with open(f"{easyrsa_dir}/pki/issued/{cn}.crt") as f:
        content = f.read()
        pem_pattern = re.compile(r"(-----BEGIN CERTIFICATE-----\n[A-Za-z0-9+/=\n]+?\n-----END CERTIFICATE-----)", re.DOTALL)
        cert = pem_pattern.search(content).group(1)

    with open(f"{easyrsa_dir}/pki/private/{cn}.key") as f:
        key = f.read()

    cn_dir = f"{clients_dir}/{cn}"
    try:
        os.mkdir(cn_dir)
    except FileExistsError:
        pass
    
    for name, info in config["servers"].items():

        if not clients or clients[cn] == "all" or name in clients[cn]:

            data = {"host": info["host"],
                    "params": config["params"],
                    "ca": ca,
                    "cert": cert,
                    "key": key,
                    "tls_crypt_key": tls_crypt_key}

            if "udp" in info:
                filename = f"{cn_dir}/{cn}_{name.upper()}1.ovpn"
                data["port"] = info["udp"]["port"]
                with open(filename, "w") as f:
                    f.write(env.get_template("/udp.conf.j2").render(data))

            if "tcp" in info:
                filename = f"{cn_dir}/{cn}_{name.upper()}2.ovpn"
                data["port"] = info["tcp"]["port"]
                with open(filename, "w") as f:
                    f.write(env.get_template("/tcp.conf.j2").render(data))

    with zipfile.ZipFile(f"{cn_dir}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in glob(os.path.join(cn_dir, "*")):
            zipf.write(file, os.path.basename(file))
    
    shutil.rmtree(cn_dir)
    print(f"{cn_dir}.zip")
    