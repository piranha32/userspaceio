#!/bin/sh
#
# Create Java bindings as libpwmio.jar
#
# Run in the libpwmio dir of the userspaceio project.
#

# Get current directory
curdir=$PWD

# stdout and stderr for commands logged
logfile="$curdir/java-bindings.log"
rm -f $logfile

# Simple logger
log(){
	timestamp=$(date +"%m-%d-%Y %k:%M:%S")
	echo "$timestamp $1"
	echo "$timestamp $1" >> $logfile 2>&1
}

# Get architecture
arch=$(uname -m)

log "Generate JNA library for libpwmio"

# Change into java dir
cd java  >> $logfile 2>&1

# Skip JNAerator steps if ARMv8 because "architecture word width mismatch" shart caused by library libbridj.so
if [ "$arch" = "aarch64" ]; then
	if [ ! -f libpwmio.jar ]; then
		log "Copying precompiled libpwmio.jar due to JNAerator ARMv8 issue"
		cp jars/libpwmio.jar .
	fi
else	
	# Generate JNA library if libpwmio.jar doesn't exist
	if [ ! -f libpwmio.jar ]; then
		rm -rf libpwmio >> $logfile 2>&1

	    # Generate classes
		java -jar ../../jnaerator/jnaerator.jar -library pwmio -mode Directory -runtime JNA -preferJavac -beanStructs -noLibBundle /usr/local/lib/libpwmio.so ../c/src/pwmio.h  >> $logfile 2>&1

		# Patch getFieldOrder(), see https://github.com/nativelibs4java/JNAerator/pull/111/commits/a2b0ae821369d6efed896627dccc1fa1f9677556
		log "Patching generated source"
		cd pwmio >> $logfile 2>&1
		sed -i 's/List<? > getFieldOrder()/List<String> getFieldOrder()/g' *.java >> $logfile 2>&1

		# Compile library
		log "Compile library"
		cd ../ >> $logfile 2>&1
		javac -cp ../../jnaerator/jna-4.5.0.jar:../../jnaerator/jnaerator-runtime.jar pwmio/*.java >> $logfile 2>&1
		# Create package
		/usr/lib/jvm/jdk1.8.0/bin/jar cf libpwmio.jar pwmio/*.* >> $logfile 2>&1
	fi
fi

# Compile demo code
log "Compiling demo code"
javac -cp ../../jnaerator/jna-4.5.0.jar:../../jnaerator/jnaerator-runtime.jar:libpwmio.jar src/com/codeferm/*.java src/com/codeferm/demo/*.java >> $logfile 2>&1

# Create package
rm -f demo.jar >> $logfile 2>&1
cd src >> $logfile 2>&1
/usr/lib/jvm/jdk1.8.0/bin/jar cf ../demo.jar com/codeferm/*.class com/codeferm/demo/*.class >> $logfile 2>&1

log "Done"
