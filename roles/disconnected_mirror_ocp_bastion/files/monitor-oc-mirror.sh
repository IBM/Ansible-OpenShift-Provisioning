#!/bin/bash
# Script: monitor-oc-mirror.sh
# Description: Real-time monitoring of oc-mirror progress
# Usage: ./monitor-oc-mirror.sh [log-file-path]

LOG_FILE="${1:-/opt/oc-mirror/oc-mirror-progress.log}"

if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file not found: $LOG_FILE"
    echo "Usage: $0 [log-file-path]"
    exit 1
fi

echo "=========================================="
echo "OC-Mirror Progress Monitor"
echo "=========================================="
echo "Log file: $LOG_FILE"
echo "Press Ctrl+C to exit"
echo "=========================================="
echo ""

# Function to display statistics
show_stats() {
    local total_images=$(grep -c "sha256" "$LOG_FILE" 2>/dev/null || echo "0")
    local errors=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
    local warnings=$(grep -c "WARN" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo ""
    echo "=========================================="
    echo "Statistics ($(date '+%Y-%m-%d %H:%M:%S'))"
    echo "=========================================="
    echo "Images processed: $total_images"
    echo "Errors: $errors"
    echo "Warnings: $warnings"
    echo "=========================================="
    echo ""
}

# Show initial stats
show_stats

# Monitor log file with filtering for relevant information
tail -f "$LOG_FILE" | while read -r line; do
    # Filter and colorize output
    if echo "$line" | grep -q "ERROR"; then
        echo -e "\033[0;31m[ERROR]\033[0m $line"
    elif echo "$line" | grep -q "WARN"; then
        echo -e "\033[0;33m[WARN]\033[0m $line"
    elif echo "$line" | grep -qE "mirroring|copying"; then
        echo -e "\033[0;36m[MIRROR]\033[0m $line"
    elif echo "$line" | grep -q "sha256"; then
        # Extract image name if possible
        image=$(echo "$line" | grep -oP '(?<=copying )[^ ]+' || echo "$line")
        echo -e "\033[0;32m[IMAGE]\033[0m $image"
    elif echo "$line" | grep -qE "INFO.*collecting|INFO.*found"; then
        echo -e "\033[0;34m[INFO]\033[0m $line"
    fi
    
    # Show stats every 50 lines
    if [ $((RANDOM % 50)) -eq 0 ]; then
        show_stats
    fi
done

# Made with Bob
