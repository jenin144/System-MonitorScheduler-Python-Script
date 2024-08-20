#!/bin/sh

FIFO1="/tmp/fifo1"
FIFO2="/tmp/fifo2"

# Create FIFOs if they do not exist
[ ! -p "$FIFO1" ] && mkfifo "$FIFO1"
[ ! -p "$FIFO2" ] && mkfifo "$FIFO2"

# Infinite loop to check FIFO1
while true; do
    # Read from FIFO1
    if read DATA < "$FIFO1"; then
        echo "Read value: $DATA"
        
        # Check if the value is not 3
        if [ "$DATA" -ne 3 ]; then
            echo "Pass"
        fi

        # Check if the value is 2
        if [ "$DATA" -eq 2 ]; then
            echo "3" > "$FIFO1"
        fi
    fi
done

