#!/bin/sh
#
# Install libgpiod on Armbian mainline.
#
# Run in the libgpiod dir of the userspaceio project.
#

# Use tar.gz instead of git repo
usegitrepo="False"
libgpiodurl="https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/snapshot/"
libgpiodarchive="libgpiod-1.0.tar.gz"

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

# Temp dir for downloads, etc.
tmpdir="$HOME/temp"

log "Installing libgpiod"

# See if project already exists
if [ ! -d "$curdir/../../libgpiod" ]; then
	# Source file
	. /etc/armbian-release 
	# Build kernel header package name
	if [ -z "$BRANCH" ]
	then
		package="linux-headers-$LINUXFAMILY"
 	else
		package="linux-headers-$BRANCH-$LINUXFAMILY"
	fi
	log "Installing Linux headers $package"
	sudo apt-get install -y $package >> $logfile 2>&1
	log "Installing required build packages"
	sudo apt-get install -y libtool pkg-config	>> $logfile 2>&1
	# Move to home dir
	cd $curdir/../../ >> $logfile 2>&1
    # If patchjava is True then install OpenCV's contrib package
    if [ "$usegitrepo" = "True" ]; then	
		log "Cloning libgpiod"
		git clone https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git --branch v1.0.x >> $logfile 2>&1
	else
		# Clean up
		log "Removing $tmpdir"
		rm -rf "$tmpdir" >> $logfile 2>&1
		mkdir -p "$tmpdir" >> $logfile 2>&1
		echo -n "Downloading $libgpiodurl$libgpiodarchive to $tmpdir     "
		wget --directory-prefix=$tmpdir --timestamping --progress=dot "$libgpiodurl$libgpiodarchive" 2>&1 | grep --line-buffered "%" |  sed -u -e "s,\.,,g" | awk '{printf("\b\b\b\b%4s", $2)}'
		echo
		log "Extracting $tmpdir/$libgpiodarchive to $tmpdir"
		tar -xf "$tmpdir/$libgpiodarchive" -C "$tmpdir" >> $logfile 2>&1
		mv $tmpdir/libgipod-1.0 ~/libgipod
		# Clean up
		log "Removing $tmpdir"
		rm -rf "$tmpdir" >> $logfile 2>&1
	fi	
	cd libgpiod >> $logfile 2>&1
	# Add header file missing from Linux user space includes
	mkdir -p $curdir/include/linux >> $logfile 2>&1
	cp /usr/src/linux-headers-$(uname -r)/include/linux/compiler_types.h $curdir/include/linux/. >> $logfile 2>&1	
	log "Running autogen"
	./autogen.sh --enable-tools=yes --prefix=/usr/local CFLAGS="-I/usr/src/linux-headers-$(uname -r)/include/uapi -I$curdir/include" >> $logfile 2>&1
	log "Running make"
	make >> $logfile 2>&1
	log "Make install"
	sudo make install >> $logfile 2>&1
	sudo ldconfig >> $logfile 2>&1
fi

log "Done"
