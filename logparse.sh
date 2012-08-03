#!/bin/sh

awk 'BEGIN { FS="] " } /objects tested/ { next } /objects migrated/ { next } /Exclusions / { next } /Duplicate slug/ { next } /Field name has been made unique with/ { next } /could not be found/ { next } /^\[.*\] / { print $2 }' $1
