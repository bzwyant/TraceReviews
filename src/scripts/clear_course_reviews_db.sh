#!/bin/bash

cd ..

# MongoDB connection details
if [[ -f .env ]]; then
    source .env
fi

collection="CourseReviews"
mongosh "$COURSE_REVIEWS_CLIENT_URI" --eval "db.$collection.deleteMany({})"

echo "Collection $collection in database $database cleared."
