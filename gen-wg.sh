#!/bin/bash

mkdir wg
cd wg
umask 077
wg genkey > privkey
cat privkey | wg pubkey > pubkey
