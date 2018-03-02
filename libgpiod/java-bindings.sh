#!/bin/sh
#
# Create Java bindings as libgpiod.jar
#
# Run in the libgpiod dir of the userspaceio project.
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

log "Generate JNA library for libgpiod"

# Change into java dir
cd java  >> $logfile 2>&1

# Skip JNAerator steps if ARMv8 because "architecture word width mismatch" shart caused by library libbridj.so
if [ "$arch" = "aarch64" ]; then
	if [ ! -f libgpiod.jar ]; then
		log "Copying precompiled libgpiod.jar due to JNAerator ARMv8 issue"
		cp jars/libgpiod.jar .
	fi
else	
	# Generate JNA library if libgpiod.jar doesn't exist
	if [ ! -f libgpiod.jar ]; then
		rm -rf libgpiod >> $logfile 2>&1

	    # Generate classes
		java -jar ../../jnaerator/jnaerator.jar -I /usr/include/arm-linux-gnueabihf -library gpiod -mode Directory -runtime JNA -preferJavac -beanStructs -noLibBundle /usr/local/lib/libgpiod.so /usr/include/linux/time.h ../../../libgpiod/include/gpiod.h ../../../libgpiod/src/lib/core.c >> $logfile 2>&1

		# Patch getFieldOrder(), see https://github.com/nativelibs4java/JNAerator/pull/111/commits/a2b0ae821369d6efed896627dccc1fa1f9677556
		log "Patching generated source"
		cd gpiod >> $logfile 2>&1
		sed -i 's/List<? > getFieldOrder()/List<String> getFieldOrder()/g' *.java >> $logfile 2>&1
		# Patch gpio_chip.java to prevent java.lang.IllegalStateException: Array fields must be initialized
		sed -i 's/public gpiod.gpiod_line.ByReference\[\] lines/public gpiod.gpiod_line.ByReference\[\] lines = new gpiod.gpiod_line.ByReference\[1\]/g' gpiod_chip.java >> $logfile 2>&1

		# Compile library
		log "Compile library"
		cd ../ >> $logfile 2>&1
		javac -cp ../../jnaerator/jna-4.5.0.jar:../../jnaerator/jnaerator-runtime.jar gpiod/*.java >> $logfile 2>&1
		# Create package
		/usr/lib/jvm/jdk1.8.0/bin/jar cf libgpiod.jar gpiod/*.* >> $logfile 2>&1
	fi
fi

# Compile demo code
log "Compiling demo code"
javac -cp ../../jnaerator/jna-4.5.0.jar:../../jnaerator/jnaerator-runtime.jar:libgpiod.jar src/com/codeferm/demo/*.java >> $logfile 2>&1

# Create package
rm -f demo.jar >> $logfile 2>&1
cd src >> $logfile 2>&1
/usr/lib/jvm/jdk1.8.0/bin/jar cf ../demo.jar com/codeferm/demo/*.class >> $logfile 2>&1

log "Done"
