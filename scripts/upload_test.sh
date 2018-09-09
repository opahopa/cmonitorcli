#!/usr/bin/env bash
BASH_C="bash -c"
HOSTNAME=$(sudo uname -n 2>/dev/null || true)
POD_DIR="/root/scripts/upload-test"

sudo mkdir -p ${POD_DIR}

sudo npm install -g codius

sudo ${BASH_C} 'echo "{
  "manifest": {
    "name": "my-codius-create-react-app",
    "version": "1.0.0",
    "machine": "small",
    "port": "3000",
    "containers": [{
      "id": "app",
      "image": "androswong418/example-pod-1@sha256:8933bced1637e7d3b08c4aa50b96a45aef0b63f504f595bb890f57253af68b11"
    }]
  }
}" > $POD_DIR/codius.json'

sudo ${BASH_C} 'echo "{
  "vars": {
    "public": {},
    "private": {}
  }
}" > $POD_DIR/codiusvars.json'

sudo cd ${POD_DIR}

sudo codius upload --host https://$HOSTNAME --duration 30 -o -y
sudo rm -rf ${POD_DIR}