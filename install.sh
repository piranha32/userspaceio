#!/bin/sh
#
# Install cytpesgen, Java, JNAerator and create bindings.
#
# Run in the userspaceio dir.
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

log "Installing User Space IO"

# Install CFFI
cd $curdir/cffi
./install.sh

# Install JNAerator
cd $curdir/jnaerator
./install.sh

# Install libgpiod
cd $curdir/libgpiod
./install.sh

# Generate libgpiod Python bindings
cd $curdir/libgpiod
./python-bindings.sh

# Generate libgpiod Java bindings
cd $curdir/libgpiod
./java-bindings.sh

# Install c-periphery
cd $curdir/c-periphery
./install.sh

# Generate c-periphery Python bindings
cd $curdir/c-periphery
./python-bindings.sh

# Generate libperiphery Java bindings
cd $curdir/c-periphery
./java-bindings.sh

# Install pwmio
cd $curdir/pwmio
./install.sh

# Generate pwmio Python bindings
cd $curdir/pwmio
./python-bindings.sh

# Generate pwmio Java bindings
cd $curdir/pwmio
./java-bindings.sh
