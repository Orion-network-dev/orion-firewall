#!/bin/sh

# Permet la génération des paquets debian
TAG=$(git describe --tags $(git rev-list --tags --max-count=1))
VERSION="${TAG/-/~/X}"
fpm -t deb -v "$VERSION"