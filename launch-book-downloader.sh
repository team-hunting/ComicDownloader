#!/bin/bash

# TODO: convert this all to a python script or go object

# TODO: let the user pick where they want books downloaded
# TODO: add metadata from series page
# TODO: enable wget on all parts
# TODO: check that the number of images match (grep output for blogspot or whatever and wc that against the number of pictures)
# TODO: add check for png or other images
# TODO: figure out a better way to hunt down links (issues/full/TPB)
# TODO: add a check to stop folder creation if there are no comics/images downloaded
# TODO: add a search option and have it download everything on the search page
# TODO: add a flag to not delete the downloads on script exit
# TODO: add a flag for just download
# TODO: add a flag for just processing files into CBZ's
# TODO: add an option to download in low or high quality, also offer the option to downgrade the final file

# prints usage
# TODO: add some cleanup
# TODO: add usage with chrome, ctrl+s, wait for download. ctrl+w, press any key in terminal window
function usage() {
    echo "This tool streamlines downloading comics from readcomiconline.li"
    echo ""
    echo "Run with:"
    echo "  launch-book-downloader.sh https://readcomiconline.li/Comic/The-Sandman-1989"
    echo ""
    echo "Notes:"
    echo "  The url passed needs to be of a single comic series i.e. https://readcomiconline.li/Comic/The-Sandman-1989"
    echo "  The resulting books will be downloaded to $HOME/book/series-name in the CBZ format"
    echo ""
    echo "Things to consider:"
    echo "  This only works on unix systems, needs wget and grep"
    echo "  Consider using the high quality option on the website"
    echo ""
    exit
}

# adds a tmp location to download files to
# TODO: find a better solution than cd-ing into tmp and running
mkdir -p /tmp/book
mkdir -p $HOME/book/
LAND=/tmp/book
cd $LAND

# download the main comic page, builds the filename var, and checks for duplicate names
# TODO: add a check for name duplicates
# TODO: update usage for more than one kind of input
if [ -z "$1" ]; then
    usage
else
    URL="$1"
    FILENAME=$(echo $URL | grep -o Comic/.* | grep -o [^Comic/].*)
    # check if the book is already downloaded
    if [ -d "$HOME/book/$FILENAME" ]; then
        # TODO: python, check if the folder is empty and only download what isn't already downloaded
        echo "Folder $FILENAME already exists. Quitting"
        exit
    fi
    wget $URL
    mkdir -p "$HOME/book"
fi

# get the links from the listing page, if there are issues
# TODO: python, can be better used for string manipulation. might solve the TBD/etc name problems
# TODO: invert the list, runs from latest to earliest
# doenst work super well for TBP without a number and for names that fall out of convention (30th Anniversary Edition, etc)
LINKS=$(for x in $(cat $FILENAME | grep -o "href=\"/Comic/$FILENAME/.*\"" | grep -o /[^/]*\" | grep -o /[^/]*[^\"]) ; do echo "$URL$x"; done)
echo "$LINKS" > book-links.txt
for link in $LINKS
do
    # verify image checking
    # add a wget for the images, and move the book processing into this for loop
    # add a check for number of images being correct
    # add a check for when the chrome window closes
    echo "Opening $link"
    google-chrome --new-window "$link"
    read -n 1 -p "enter any key for next book " output
done

# verify that all links have been downloaded, then redownload ones that were missed
rm ./$FILENAME
rm ./*html

# run through each issue
for issue in */
do
    # this just checks if full was the issue number
    # add a check for Full and one for TPB
    LINE=$(echo $issue)
    if [[ "$LINE" == *"Full"* ]];
    then
        NUM="Full"
    elif [[ "$LINE" == *"TPB"* ]];
    then
        # TODO: fix this
        # refactor this part, doesn't count for partial books. Like 3.5 or 5.5 two part books
        num=$(echo $issue | grep -o TPB.[0-9]*)
        NUM=$(echo $num | tr -d ' ')
        # NUM=$(echo $num |  | sed 's/ /-/g')
    else
        num=$(echo $issue | grep -o \#[0-9]*)
        NUM=$(echo $num | grep -o ^\#[0-9]*)
    fi
    echo ""
    echo "NUM is $NUM"
    echo ""
    cd "$issue"
    mkdir -p "$FILENAME-$NUM"
    mv ./*jpg ./"$FILENAME-$NUM"
    mv ./*JPG ./"$FILENAME-$NUM"
    cd ./"$FILENAME-$NUM"

    for image in *
    do
        mv "$image" "$(echo $image | grep -o RCO[0-9]\* | grep -o [0-9]\*).jpg"
    done

    zip "$FILENAME-$NUM".cbz ./*
    mkdir -p ~/book/$FILENAME
    mv ./*.cbz ~/book/$FILENAME
    cd $LAND
done

rm -rf /tmp/book/*
echo "books downloaded:"
ls ~/book/$FILENAME

# get the size of the comic book
SINGLESIZE=$(du -hs "$HOME/book/$FILENAME/" | cut -f1)
echo "Total size of $FILENAME is $SINGLESIZE"
