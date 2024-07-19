#!/bin/sh

TAG=$(git describe --tags $(git rev-list --tags --max-count=1))
fpm -t deb -v "$TAG"