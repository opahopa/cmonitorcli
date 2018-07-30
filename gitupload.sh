#/bin/bash

git push origin master
rsync -av --progress ${PWD}/* ../cmonitorserv/cmonitorcli --exclude .git --exclude .idea --exclude .gitignore --exclude builds --exclude venv