#!/usr/bin/env bash
BASH_C="bash -c"
CURRENT_USER="$(id -un 2>/dev/null || true)"
DISTR_TYPE=""

#Color Constant
RED=`tput setaf 1`
GREEN=`tput setaf 2`
YELLOW=`tput setaf 3`
BLUE=`tput setaf 4`
WHITE=`tput setaf 7`
LIGHT=`tput bold `
RESET=`tput sgr0`

#Error Message#Error Message
ERR_ROOT_PRIVILEGE_REQUIRED=(10 "This install script need root privilege, please retry use 'sudo' or root user!")

show_message() {
  case "$1" in
    debug)  echo -e "\n[${BLUE}DEBUG${RESET}] : $2";;
    info)   echo -e -n "\n${WHITE}$2${RESET}" ;;
    warn)   echo -e    "\n[${YELLOW}WARN${RESET}] : $2" ;;
    done|success) echo -e "${LIGHT}${GREEN}$2${RESET}" ;;
    error|failed) echo -e "\n[${RED}ERROR${RESET}] : $2" ;;
  esac
}

command_exist() {
  type "$@" > /dev/null 2>&1
}

check_user() {
  if [[ "${CURRENT_USER}" != "root" ]];then
    if (command_exist sudo);then
      SUDO='sudo'
    else
      show_message error "${ERR_ROOT_PRIVILEGE_REQUIRED[1]}" && exit ${ERR_ROOT_PRIVILEGE_REQUIRED[0]}
    fi
    show_message info "${WHITE}Hint: This installer need root privilege\n"
    ${SUDO} echo -e "\n"
  fi
}
check_user

check_distro() {
    if [ -n "$(command -v lsb_release)" ]; then
        distroname=$(lsb_release -s -d)
    elif [ -f "/etc/os-release" ]; then
        distroname=$(grep PRETTY_NAME /etc/os-release | sed 's/PRETTY_NAME=//g' | tr -d '="')
    elif [ -f "/etc/debian_version" ]; then
        distroname="Debian $(cat /etc/debian_version)"
    elif [ -f "/etc/redhat-release" ]; then
        distroname=$(cat /etc/redhat-release)
    else
        distroname="$(uname -s)"
    fi

    if [[ ${distroname,,} = *"centos"* ]]; then
      DISTR_TYPE="centos"
    elif [[ ${distroname,,} = *"debian"* ]]; then
      DISTR_TYPE="debian"
    elif [[ ${distroname,,} = *"ubuntu"* ]]; then
      DISTR_TYPE="ubuntu"
    elif [[ ${distroname,,} = *"fedora"* ]]; then
      DISTR_TYPE="fedora"
    else
        >&2 echo "Sorry but this linux distribution is not yet supported."
        exit 1
    fi
}
check_distro

#check if installed
if pgrep -x "fail2ban" > /dev/null
then
    echo "fail2ban is already enabled on your host"
    exit 1
fi

enable_firewalld() {
    ${SUDO} firewall-cmd --zone=public --add-service=http --permanent
    ${SUDO} firewall-cmd --zone=public --add-service=https --permanent
    ${SUDO} firewall-cmd --zone=public --add-service=ssh --permanent 2>/dev/null || true
    ${SUDO} systemctl enable firewalld 2>/dev/null || true
    ${SUDO} systemctl start firewalld 2>/dev/null || true
}


if [[ ${DISTR_TYPE} == "centos" ]]; then
    ${SUDO} yum install -y epel-release
    ${SUDO} yum install -y fail2ban fail2ban-systemd
    ${SUDO} yum update -y selinux-policy
    enable_firewalld
elif [[ ${DISTR_TYPE} == "ubuntu" ]] || [[ ${DISTR_TYPE} == "debian" ]]; then
    ${SUDO} apt-get update -y && apt-get upgrade -y
    ${SUDO} apt-get install -y fail2ban
    ${SUDO} ufw allow ssh
    ${SUDO} ufw allow https
    ${SUDO} ufw allow http
    ${SUDO} ufw enable
elif [[ ${DISTR_TYPE} == "fedora" ]]; then
    ${SUDO} dnf update -y
    ${SUDO} dnf install -y fail2ban
    enable_firewalld
else
    >&2 echo "Sorry but this linux distribution is not yet supported."
    exit 1
fi

${SUDO} cp -pf /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

sudo ${BASH_C} 'echo "[sshd]
enabled = true
port = ssh
#action = firewallcmd-ipset
logpath = %(sshd_log)s
maxretry = 5
bantime = 86400" > /etc/fail2ban/jail.d/sshd.local'

${SUDO} systemctl enable fail2ban 2>/dev/null || true
${SUDO} systemctl start fail2ban

show_message info "Installation done! \n"
exit 0