#!/bin/bash

# Run scraping script from src
cd ./trace_spider
# pwd

# Record the start time
start_time=$(date +%s)

scrapy crawl course_spider -o test_course_output.json

end_time=$(date +%s)

# Calculate the elapsed time in seconds
elapsed_seconds=$((end_time - start_time))

# Convert elapsed time to minutes and seconds
elapsed_minutes=$((elapsed_seconds / 60))
remaining_seconds=$((elapsed_seconds % 60))

echo "Elapsed time: $elapsed_minutes minutes and $remaining_seconds seconds"
