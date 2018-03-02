#!/bin/sh
#
# Install JNAerator
#
# Run in the jnaerator dir of the userspaceio project.
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

log "Installing JNAerator"

# Install Java
if ! command -v java
then
	sudo ./install-java.sh
fi

# Get architecture
arch=$(uname -m)

# Skip JNAerator steps if ARMv8 because "architecture word width mismatch" shart caused by library libbridj.so
if [ "$arch" = "aarch64" ]; then
	log "Skipping JNAerator install due to ARMv8 issue"
	if [ ! -f jnaerator-runtime.jar ]; then
		log "Copying precompiled jnaerator-runtime.jar due to JNAerator ARMv8 issue"
		cp jars/jnaerator-runtime.jar .
	fi	
else	
	# Download JNAerator
	if [ ! -f jnaerator.jar ]; then
		log "Download JNAerator"
		wget -O jnaerator.jar https://oss.sonatype.org/content/groups/public/com/nativelibs4java/jnaerator/0.13-SNAPSHOT/jnaerator-0.13-20150328.111636-4-shaded.jar >> $logfile 2>&1
	fi
	# Add JNAerator dependencies
	if [ ! -f jnaerator-runtime.jar ]; then
		log "Building JNAerator dependencies"
		rm -rf com >> $logfile 2>&1
		mkdir -p com/ochafik/lang/jnaerator/runtime >> $logfile 2>&1
		cd com/ochafik/lang/jnaerator/runtime >> $logfile 2>&1
		wget https://raw.githubusercontent.com/nativelibs4java/JNAerator/master/jnaerator-runtime/src/main/java/com/ochafik/lang/jnaerator/runtime/NativeSize.java >> $logfile 2>&1
		wget https://raw.githubusercontent.com/nativelibs4java/JNAerator/master/jnaerator-runtime/src/main/java/com/ochafik/lang/jnaerator/runtime/CharByReference.java >> $logfile 2>&1
		cd $curdir >> $logfile 2>&1
		# Compile dependency code
		javac -cp jna-4.5.0.jar com/ochafik/lang/jnaerator/runtime/*.java >> $logfile 2>&1
		# Create package
		/usr/lib/jvm/jdk1.8.0/bin/jar cf jnaerator-runtime.jar com/ochafik/lang/jnaerator/runtime/*.* >> $logfile 2>&1
	fi
fi

log "Done"
