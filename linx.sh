#!/bin/bash

DIR="/tmp/mytestdir"
FILE="$DIR/hello.txt"

# Check if directory exists
if [ ! -d "$DIR" ]; then
  echo "Directory $DIR does not exist. Creating now..."
  mkdir -p "$DIR"
else
  echo "Directory $DIR already exists."
fi

# Create a file with a message
echo "Hello from RHEL bash script!" > "$FILE"

echo "File $FILE created with message."

