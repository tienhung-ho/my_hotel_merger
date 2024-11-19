#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage:"
    echo "  $0 <hotel_ids> <destination_ids>"
    echo ""
    echo "Examples:"
    echo "  $0 hotel_id_1,hotel_id_2,hotel_id_3 destination_id_1,destination_id_2"
    echo "  $0 hotel_id_4,hotel_id_5 none"
    echo "  $0 none destination_id_3"
    echo ""
    exit 1
fi

# Execute the CLI application with provided arguments
python3 -m hotel_merger.main "$1" "$2"
