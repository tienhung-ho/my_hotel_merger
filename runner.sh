#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Execute the CLI application with provided arguments
python3 -m hotel_merger.main "$1" "$2" "${@:3}"
