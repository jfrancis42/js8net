#!/bin/bash

C=`which curl`
U=`which unzip`

if [[ $C && $U ]]
then
    rm -f l_amat.zip
    echo "Downloading US data..."
    curl ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip --output l_amat.zip
    echo "Extracting files..."
    unzip l_amat.zip EN.dat
    rm -f l_amat.zip

    rm -f amateur_delim.zip
    echo "Downloading CA data..."
    curl https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip --output amateur_delim.zip
    echo "Extracting files..."
    unzip amateur_delim.zip amateur_delim.txt
    rm -f amateur_delim.zip

    rm -f spectra_rrl.zip
    echo "Downloading AU data..."
    curl https://web.acma.gov.au/rrl-updates/spectra_rrl.zip --output spectra_rrl.zip
    echo "Extracting files..."
    unzip spectra_rrl.zip device_details.csv client.csv licence.csv
    rm -f spectra_rrl.zip

    ./make_calldb.py --basedir /tmp/

    echo "Removing temporary files..."
    rm -f EN.dat amateur_delim.txt spectra_rrl.zip device_details.csv client.csv licence.csv

    echo "Done."
else
    echo "Unable to find curl and/or unzip binary."
fi
