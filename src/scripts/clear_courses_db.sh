#!/bin/bash

cd ..

# MongoDB connection details
if [[ -f .env ]]; then
    source .env
fi

collection="courseInfo"
mongosh "mongodb+srv://$ATLAS_USERNAME:$ATLAS_PASSWORD@trace.gqna2hn.mongodb.net/reports?retryWrites=true&w=majority" --eval "db.$collection.deleteMany({})"

echo "Collection $collection in database $database cleared."
