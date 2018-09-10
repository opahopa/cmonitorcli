#!/usr/bin/env bash
BASH_C="bash -c"
HOSTNAME=$(sudo uname -n 2>/dev/null || true)
CURRENT_USER="$(id -un 2>/dev/null || true)"
POD_DIR="/root/scripts/upload-test"

command_exist() {
  type "$@" > /dev/null 2>&1
}

check_user() {
  if [[ "${CURRENT_USER}" != "root" ]];then
    if (command_exist sudo);then
      SUDO='sudo'
    else
      echo "This script need root privilege" && exit "This script need root privilege"
    fi
  fi
}
check_user

sudo rm -rf ${POD_DIR} 2>/dev/null || true
sudo mkdir -p ${POD_DIR}

sudo npm install -g codius

cat << EOF > $POD_DIR/codius.json
{
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
}
EOF
cat << EOF > $POD_DIR/codiusvars.json
{
  "vars": {
    "public": {},
    "private": {}
  }
}
EOF

cd ${POD_DIR}

sudo DEBUG=* codius upload --host https://$HOSTNAME --duration 30 -o -y
