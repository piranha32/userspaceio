#!/bin/sh

# Create Python multiple bindings as for c-periphery

# Run in the c-periphery dir of the userspaceio project.

# Get current directory
curdir=$PWD

# stdout and stderr for commands logged
logfile="$curdir/python-bindings.log"
rm -f $logfile

# Simple logger
log(){
	timestamp=$(date +"%m-%d-%Y %k:%M:%S")
	echo "$timestamp $1"
	echo "$timestamp $1" >> $logfile 2>&1
}

# Install Python package
log "Installing Python package"
cd python/src >> $logfile 2>&1
sudo -H pip3 install -e . >> $logfile 2>&1

log "Done"
