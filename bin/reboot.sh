#!/bin/bash

sleep 30

cd "$(dirname "$0")";
./control-mqtt.py &

exit
