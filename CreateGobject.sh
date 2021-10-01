#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/CreateGobject $@"

exec ./dist/CreateGobject $@

