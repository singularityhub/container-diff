#!/bin/bash

# This example will show how to extract json objects of files and packages
# for sets of images. In this case, we will extract the ubuntu family of
# images to see if we can see changes over the years!

# I tested running with sudo
# sudo -E ./compare_ubuntu.sh

declare -a uris=("ubuntu:12.04" "ubuntu:14.04" "ubuntu:16.04" "ubuntu:17.04" "ubuntu:18.04")

# Make sure you are sitting in the examples directory, or have 
# analyze-singularity on your path!

PATH=$PATH:../

## now loop through the above array
for docker_uri in "${uris[@]}"
do

    echo
    echo "Running Comparison Extraction for ${docker_uri}!"

    # Name based on URI

    image="${docker_uri}.simg"

    # Pull the image if it doesn't exist

    if ! [ -f ${image} ]; then
        singularity pull --name "${image}" "docker://${docker_uri}"    
    fi
 
    # You will see some errors about getting sizes here

    files_json=`exec analyze-singularity.sh "${image}" --type=file   | tail -1`
    mv $files_json "${docker_uri}-files.json"

    packages_json=`exec analyze-singularity.sh "${image}"  | tail -1`
    mv $packages_json "${docker_uri}-packages.json"

done

# And just for repo saving, added to data
# mkdir -p data
# mv *.json data
