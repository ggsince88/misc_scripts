#!/bin/bash
# Quick shell script to reboot all workspaces
# AWS only allows us to reboot 25 workspaces at a time
workspaces=(`aws workspaces describe-workspaces --directory-id ID_HERE --query 'Workspaces[*].WorkspaceId' --output text`)

i=0
ws_array=()
num_of_ws=${#workspaces[@]}
# num of workspaces
echo ${num_of_ws}

for (( c=0; c<=${num_of_ws}; c++ ));
do
  # array magic
  ws_array+=(${workspaces[@]0:$c:1})
  # AWS only allows us to reboot 25 workspaces at a time
  if [[ ${#ws_array[@]} -eq 24 ]]; then
    echo "Rebooting workspaces"
    aws workspaces reboot-workspaces --reboot-workspace-requests ${ws_array[@]}
    ws_array=()
    sleep 10
  elif [[ $c -eq ${num_of_ws} ]]; then
    echo "Rebooting last of workspaces"
  fi
done
