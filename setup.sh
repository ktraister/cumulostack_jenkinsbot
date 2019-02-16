#!/bin/bash

read "ACCESS_TOKEN"
read "BOT_TOKEN"
read "JENKINS_PASS"

sed -i "s/ACCESS_TOKEN/$ACCESS/" chatbot.py
sed -i "s/BOT_TOKEN/$BOT/" chatbot.py

