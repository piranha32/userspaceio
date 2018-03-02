#!/bin/sh
#
# Install c-periphery.
#
# Run in the c-periphery dir of the userspaceio project.
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

log "Installing c-periphery"

# See if github project already exists
if [ ! -d "$curdir/../../c-periphery" ]; then
	# Move to home dir
	cd $curdir/../../ >> $logfile 2>&1
	log "Cloning c-periphery"
	git clone https://github.com/vsergeev/c-periphery.git >> $logfile 2>&1
	cd c-periphery >> $logfile 2>&1
	# Make shared library for bindings
	make >> $logfile 2>&1
	# Save each obj as a shared library
	ld -shared obj/i2c.o -o libperipheryi2c.so >> $logfile 2>&1
	ld -shared obj/spi.o -o libperipheryspi.so >> $logfile 2>&1
	ld -shared obj/serial.o -o libperipheryserial.so >> $logfile 2>&1
	# Deploy shared libraries
	sudo cp *.so /usr/local/lib/. >> $logfile 2>&1
fi

log "Done"
