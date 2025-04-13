#!/bin/bash

# Function to clean and sync S3
sync_s3() {
    echo "Syncing EMR scripts..."
    aws s3 rm s3://flight-emr/scripts/ --recursive
    aws s3 sync emr-scripts s3://flight-emr/scripts/ --delete
}

# Function to clean ec2-info S3 bucket and local folder
clean_ec2_info() {
    echo "Cleaning ec2-info in S3 and locally..."
    aws s3 rm s3://flight-px4-logs/ec2-info/ --recursive
    if [ -d "ec2-info" ]; then
        rm -rf ec2-info/
    fi
    mkdir ec2-info
}

# If no arguments are provided, run everything
if [ $# -eq 0 ]; then
    echo "No option provided. Running all tasks..."
    sync_s3
    clean_ec2_info
else
    for arg in "$@"; do
        case $arg in
            --sync-s3)
                sync_s3
                ;;
            --clean-ec2)
                clean_ec2_info
                ;;
            --help)
                echo "Usage: $0 [--sync-s3] [--clean-ec2]"
                echo "If no options are given, all tasks will run."
                exit 0
                ;;
            *)
                echo "Unknown option: $arg"
                echo "Use --help for usage instructions."
                exit 1
                ;;
        esac
    done
fi
