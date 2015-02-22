#!/bin/bash

source settings.sh

FORCE=false

# Did I set a force flag (no termination check)?
while getopts "f" o; do
	case "${o}" in
		f) FORCE=true;;
	esac
done

DONE=~/.ftp_done

# Did I alredy uploaded everything?
if [ -f $DONE ]; then
	exit 0
fi

# Do I want to check for the termination notice?
if [ "$FORCE" != true ]; then
	echo "Checking termination notice"
	CONTENTS=`curl -i -s http://169.254.169.254/latest/meta-data/spot/termination-time`
	HEADER=`echo "${CONTENTS}" | head -n 1 | cut -d ' ' -f2`

	if [ $HEADER != "200" ]; then
        	exit 0
	fi
fi

# Result files
FILES=~/results/*
for f in $FILES
do
  echo "Processing $f file..."
  ftp -inp $FTP_HOST << EOF
user $FTP_USER $FTP_PWD
put "$f" "${f##*/}"
bye
EOF
done

# Hashes file
FILES=~/hashes/*
for f in $FILES
do
  echo "Processing $f file..."
  ftp -inp $FTP_HOST << EOF
user $FTP_USER $FTP_PWD
put "$f" "${f##*/}"
bye
EOF
done

# HashCat restore files
ftp -inp $FTP_HOST << EOF
user $FTP_USER $FTP_PWD
put ~/cudaHashcat.pot cudaHashcat.pot
put ~/cudaHashcat.restore cudaHashcat.restore
bye
EOF

# Create the "done flag" only if I'm not forcing the script
if [ "$FORCE" != true ]; then
		touch ~/.ftp_done
fi
