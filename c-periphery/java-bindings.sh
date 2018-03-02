#!/bin/sh
#
# Create Java bindings as libperiphery.jar
#
# Run in the c-periphery dir of the userspaceio project.
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

log "Generate JNA library for c-periphery"

# Change into java dir
cd java  >> $logfile 2>&1

# Skip JNAerator steps if ARMv8 because "architecture word width mismatch" shart caused by library libbridj.so
if [ "$arch" = "aarch64" ]; then
	if [ ! -f libperiphery.jar ]; then
		log "Copying precompiled libperiphery.jar due to JNAerator ARMv8 issue"
		cp jars/libperiphery.jar .
	fi
else	
	# Generate JNA library if libperiphery.jar doesn't exist
	if [ ! -f libperiphery.jar ]; then
	    # Generate classes
		java -jar ../../jnaerator/jnaerator.jar -library peripheryi2c -mode Directory -runtime JNA -preferJavac -beanStructs -noLibBundle /usr/local/lib/libperipheryi2c.so /usr/include/arm-linux-gnueabihf/asm/types.h /usr/include/linux/types.h  /usr/include/linux/i2c.h ../../../c-periphery/src/i2c.h >> $logfile 2>&1
		java -jar ../../jnaerator/jnaerator.jar -library peripheryserial -mode Directory -runtime JNA -preferJavac -beanStructs -noLibBundle /usr/local/lib/libperipheryserial.so /usr/include/linux/spi/spidev.h ../../../c-periphery/src/serial.h >> $logfile 2>&1
		java -jar ../../jnaerator/jnaerator.jar -library peripheryspi -mode Directory -runtime JNA -preferJavac -beanStructs -noLibBundle /usr/local/lib/libperipheryspi.so ../../../c-periphery/src/spi.h >> $logfile 2>&1

		# Patch getFieldOrder(), see https://github.com/nativelibs4java/JNAerator/pull/111/commits/a2b0ae821369d6efed896627dccc1fa1f9677556
		log "Patching generated source"
		cd peripheryi2c >> $logfile 2>&1
		sed -i 's/List<? > getFieldOrder()/List<String> getFieldOrder()/g' *.java >> $logfile 2>&1
		# Remove class to fix byte reserved Java word in source
		rm i2c_smbus_data.java i2c_smbus_ioctl_data.java >> $logfile 2>&1
		cd ../peripheryserial >> $logfile 2>&1
		sed -i 's/List<? > getFieldOrder()/List<String> getFieldOrder()/g' *.java >> $logfile 2>&1
		cd ../peripheryspi >> $logfile 2>&1
		sed -i 's/List<? > getFieldOrder()/List<String> getFieldOrder()/g' *.java >> $logfile 2>&1

		# Compile library
		log "Compile library"
		cd ../ >> $logfile 2>&1
		javac -cp ../../jnaerator/jna-4.5.0.jar:../../jnaerator/jnaerator-runtime.jar peripheryi2c/*.java peripheryserial/*.java peripheryspi/*.java >> $logfile 2>&1

		# Create package
		/usr/lib/jvm/jdk1.8.0/bin/jar cf libperiphery.jar peripheryi2c/*.* peripheryserial/*.* peripheryspi/*.* >> $logfile 2>&1
	fi
fi

# Compile demo code
log "Compiling demo code"
javac -cp ../../jnaerator/jna-4.5.0.jar:../../jnaerator/jnaerator-runtime.jar:libperiphery.jar src/com/codeferm/*.java src/com/codeferm/demo/*.java >> $logfile 2>&1

# Create package
rm -f demo.jar >> $logfile 2>&1
cd src >> $logfile 2>&1
/usr/lib/jvm/jdk1.8.0/bin/jar cf ../demo.jar com/codeferm/*.class com/codeferm/demo/*.class >> $logfile 2>&1

log "Done"
