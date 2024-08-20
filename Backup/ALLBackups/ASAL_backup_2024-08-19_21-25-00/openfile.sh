#!/bin/sh

FIFO1="/tmp/fifo1"



echo "1" > "$FIFO1"
sleep 10
# Write '1' to FIFO1
echo "2" > "$FIFO1"

# Wait for 5 minutes
sleep 60

# Write '1' to FIFO1 again after 5 minutes
echo "1" > "$FIFO1"

