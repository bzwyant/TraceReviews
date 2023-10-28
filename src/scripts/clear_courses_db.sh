#!/bin/bash

cd ..

# MongoDB connection details
if [[ -f .env ]]; then
    source .env
fi

collection="courseInfo"
# mongosh "$COURSE_INFO_CLIENT_URI" --eval "db.$collection.deleteMany({})"

# echo "Collection $collection in database $database cleared."
