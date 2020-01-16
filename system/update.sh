#!/bin/bash
dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "$dt"
echo 'Updating local git repository'
git pull
echo 'Update Complete'
