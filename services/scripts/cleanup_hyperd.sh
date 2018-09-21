#!/usr/bin/env bash
# credit to https://www.xrpchat.com/profile/16731-mr_mcfearson/

BASH_C="bash -c"
CURRENT_USER="$(id -un 2>/dev/null || true)"

command_exist() {
  type "$@" > /dev/null 2>&1
}

check_user() {
  if [[ "${CURRENT_USER}" != "root" ]];then
    if (command_exist sudo);then
      SUDO='sudo'
    else
      >&2 echo "This script need root privilege" && exit 1 "This script need root privilege"
    fi
  fi
}
check_user

 # Stop services
sudo systemctl stop hyperd
sudo systemctl stop codiusd

# Unmount all Hyperd-stuff
sudo umount /var/lib/hyper/hosts/* 2>/dev/null || true
sudo umount /run/hyper/vm*/share_dir/* 2>/dev/null || true

# Cleanup
sudo rm -rf /var/lib/hyper/hosts/* 2>/dev/null || true
sudo rm -rf /var/lib/hyper/containers/* 2>/dev/null || true
sudo rm -rf /run/hyper/* 2>/dev/null || true
sudo rm -rf /var/log/hyper/qemu/* 2>/dev/null || true
sudo ifconfig codius0 down 2>/dev/null || true
sudo ifconfig hyper0 down 2>/dev/null || true

#start services
sudo systemctl start hyperd
sudo systemctl start codiusd

echo "hyperd cleanup done"