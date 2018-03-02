#!/bin/sh
#
# Install CFFI
#
# Run in the cffi dir of the userspaceio project.
#

# Get current directory
curdir=$PWD

# stdout and stderr for commands logged
logfile="$curdir/install.log"
rm -f $logfile

# Simple logger
log(){
	timestamp=$(date +"%m-%d-%Y %k:%M:%S")
	echo "$timestamp $1"
	echo "$timestamp $1" >> $logfile 2>&1
}

log "Installing CFFI"

# Install python-dev
if [ $(dpkg-query -W -f='${Status}' python3-dev 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
	log "Installing Python 3 and CFFI dev packages"
	sudo apt-get -y install build-essential python3-dev libffi-dev >> $logfile 2>&1
fi

# Install pip and cffi
if ! command -v pip3
then
	log "Installing pip and cffi"
	sudo apt-get -y install python3-pip >> $logfile 2>&1
	sudo -H pip3 install --upgrade pip setuptools >> $logfile 2>&1
	sudo -H pip3 install --upgrade cffi >> $logfile 2>&1
fi

log "Done"
