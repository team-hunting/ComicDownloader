#!/bin/bash
# renames all the cbz files in a series of directories to have leading zeros up to 0000X
echo "WARNING THIS WILL RENAME EVERYTHING"
read -N 1 "do you want to proceed? y/N" -i "n" ANS
if [[ $ANS == "Y" ]]
then
    BASE=$(pwd)
    for d in *; do
        echo "working with $d"
        cd "$d"
        COUNT=$(ls -1 | grep -c .cbz)
        DIGITS=$(echo "${#COUNT}")
        if [ "$DIGITS" -eq "2" ]; then
            rename -e 's/\d+/sprintf("%02d",$&)/e' -- *.cbz
        elif [ "$DIGITS" -eq "3" ]; then
            rename -e 's/\d+/sprintf("%03d",$&)/e' -- *.cbz
        elif [ "$DIGITS" -eq "4" ]; then
            rename -e 's/\d+/sprintf("%04d",$&)/e' -- *.cbz
        elif [ "$DIGITS" -eq "5" ]; then
            rename -e 's/\d+/sprintf("%05d",$&)/e' -- *.cbz
        fi
        cd "$BASE"
    done
fi
