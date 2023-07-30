#!/usr/bin/env bash

PPP=ppp.py

autoRotate="Auto rotate JPG files by Exif orientation"
rotate90="Rotate 90° CW"
rotate180="Rotate 180° CW"
rotate270="Rotate 270° CW"
web="Prepare for WWW publishing"

files=.
if [[ $# > 0 ]]
then
    # perform action only on selected files
    files=$(echo -e "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" | awk 'BEGIN {FS = "\n" } { printf "\"%s\" ", $1 }' | sed -e s#\"\"##)
    filesText="($# files selected)"
fi

answer=$(zenity --list --radiolist --title="Prepare Pictures and Photos" --hide-header --width=500 --height=300 \
    --text="What do you want to do: $filesText" --column="" --column="Action" \
    true "$autoRotate" false "$rotate90" false "$rotate180" false "$rotate270" false "$web" )
ret=$?
logFile=/tmp/ppp.log

if [[ $ret == 0 ]]
then
    case $answer in
    $autoRotate)
        $PPP auto-rotate $files >$logFile 2>&1
        ret=$?
        ;;
    $rotate90)
        $PPP rotate 90 $files >$logFile 2>&1
        ret=$?
        ;;
    $rotate180)
        $PPP rotate 180 $files >$logFile 2>&1
        ret=$?
        ;;
    $rotate270)
        $PPP rotate 270 $files >$logFile 2>&1
        ret=$?
        ;;
    $web)
        $PPP web $files >$logFile 2>&1
        ret=$?
        ;;
    esac

    if [ $ret != 0 ]
    then
        zenity --text-info --filename=$logFile --width=500 --height=300
    fi
fi

