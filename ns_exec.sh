#!/bin/bash
# $1 = namespace, rest = command
NS=$1
shift
sudo ip netns exec "$NS" "$@"
#sudo ip netns exec $NS "$@"
