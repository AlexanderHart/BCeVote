#!/bin/bash

GETDEFAULTACCOUNT="$(~/node/goal account list -d ~/algodNet/Primary/ -w unencrypted-default-wallet)"

defaultAccount="${GETDEFAULTACCOUNT:9:58}"

~/node/goal clerk send -a 10100000 -f $defaultAccount -t $1 -d ~/algodNet/Primary -w unencrypted-default-wallet
