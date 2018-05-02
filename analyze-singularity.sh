#! /bin/bash
#
# analyze-singularity.sh will run GoogleContainerTools container-diff
#                             analyze for a Singularity image
#
# USAGE: analyze-singularity.sh foobar.simg [container diff analyze options]
#
# Copyright (C) 2018 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


set -o errexit
set -o nounset

USAGE="USAGE: analyze-singularity.sh [image_file] [container_diff_options]"

# Sanity Checks ################################################################

is_installed() {
    software=${1:-}
    resource=${2:-}
    if hash ${software} 2>/dev/null; then
        echo "${software} is installed!"
    else
        echo "Missing ${software}, install or add to path first!"
        echo "${resource}"
        exit 1
    fi
}


# Ensure the user has container-diff installed
is_installed container-diff "https://github.com/GoogleContainerTools/container-diff"

# Ensure tar is installed
is_installed tar

# Ensure the user has singularity installed
is_installed singularity "https://github.com/singularityware/singularity"


if [ $# == 0 ] ; then
    echo $USAGE
    exit 1;
fi

image=$1
shift 

echo ""
echo "Image: ${image}"

container_id=`sha256sum ${image} | awk '{print $1}'`
TMPDIR=$(mktemp -u -d)
mkdir -p $TMPDIR
HERE=${PWD}

# Image Export #################################################################

build_sandbox="${TMPDIR}/build"                     # container export folder
build_package="${TMPDIR}/package"                   # image package
layer_folder="${build_package}/${container_id}"     # layer folder in package

echo "(1/7) Creating build folders..."
mkdir -p ${layer_folder}

# If running as user, make sandbox

if [ "$EUID" -ne 0 ]; then
    echo "(2/7) Exporting filesystem..."
    singularity build --sandbox ${build_sandbox} ${image}

    echo "(3/7) Creating layer..."
    cd ${build_sandbox} && tar -cf ${layer_folder}/layer.tar * --ignore-failed-read && cd ${HERE}

# If running as root (in Docker container) use image.export
else
    echo "(2/7) Exporting filesystem..."
    singularity image.export -f ${layer_folder}/layer.tar ${image}

    echo "(3/7) Creating layer..."

fi


# "Metadata" ###################################################################

echo "(4/7) Dummy metadata..."
echo "[{\"Config\":\"config.json\",\"Layers\": [\"${container_id}/layer.tar\"]}]" > "${build_package}/manifest.json"
echo "{}" > ${build_package}/config.json


# Image Compression #############################################################

echo "(5/7) Finishing package!"
container_package="${TMPDIR}/${container_id}.tar"
cd ${build_package} && tar -cf ${container_package} * --ignore-failed-read && cd ${HERE}

echo "(6/7) Running container analyze"
output_file="${TMPDIR}/singularity-analyze-${container_id}.json"
container-diff analyze ${container_package} --json "$@" > ${output_file}

echo "(7/7) Cleaning up!"
rm -rf ${build_sandbox}
rm -rf ${build_package}
rm -rf ${container_package}

echo "Complete. Result is at:"
echo "${output_file}"

# container-diff analyze ${container_package} "$@"
