#!/bin/bash

if pip install -r requirements.txt; then
    pip install --upgrade pip
    printf '\n%s\n' "$(tput bold)Requirements installed successfully$(tput sgr0)"
    sleep 4
    clear
else
    printf '\n%s\n' "$(tput bold)Requirements could not be installed$(tput sgr0)"
    exit 1 #failure
fi