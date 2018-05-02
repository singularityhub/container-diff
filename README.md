# Singularity Container Diff

[Container Diff](https://github.com/GoogleContainerTools/container-diff) is a tool provided by Google
to do static analysis and comparison of images. You can imagine this would be very useful to do for Singularity 
images as well, and so this wrapper provides functions to do that! This is the underlying library
that is driving cool things!

 - [compare-ubuntus](examples/compare-ubuntus): This is a very basic example of using the tool to compare ubuntu containers
 - [container-api](https://www.github.com/singularityhub/api) that will serve a static API for Singularity Hub container packages and files
 - [compare containers](examples/compare-containers): to generate visualizations to compare containers on demand.
   - and see the [demo](https://singularityhub.github.io/container-diff/examples/demo) of outputs from here!

## Quick Start
To see it in action, quickly, you can try the third of the options above, and run for two of your favorite Docker containers.
See more detail at the third link for how to change this up!

```bash
mkdir -p /tmp/web
docker run -v /tmp/web:/data -p 8888:8888 -it vanessa/container-diff centos:6 centos:7
```

An an [EXAMPLE](https://singularityhub.github.io/container-diff/examples/demo) is provided. The biggest differences between using the executable natively (first or second options) and in a Docker container (third option) are the following:

 - the Docker container does an [image.export](http://singularity.lbl.gov/docs-export) instead of a build because it requires root. If we try doing build with root it strangely fails. 
 - the Docker container can handle Singularity and/or Docker images (or other types supported by container-diff), while the native version doesn't have any logic to just run container-diff on a Docker image. It's just intended for singularity (and you could call the container-diff command yourself for other types!)

For more (verbosity) about use cases, see my [writing about container-diff](https://vsoch.github.io/2018/container-diff) post!


## Analysis Metrics
There are multiple metrics you might want to look at to analyze an image. 
Specifically, these are a subset of those listed in the Container
Diff repository, minus the ones that are exclusively Docker related.

 - Image file system
 - Apt packages
 - RPM packages
 - pip packages
 - npm packages

## Usage
To use container-diff, you mostly just need to get the files and run the executables. You can clone the repository to do that!

```bash
git clone https://www.github.com/singularityhub/container-diff.git
cd container-diff
```

## Single Image Analysis

The first kind of analysis is with respect to a single image, and for this we will be using
the [analyze-singularity.sh](analyze-singularity.sh) script. The basic usage is to provide your
Singularity image file as the first argument, followed by any arguments you want passed to container-diff.
By default, all results are saved to json for research use. For example:

```bash
./analyze-singularity.sh <image>                [defaults]
./analyze-singularity.sh <image> --type=file    [filesystem]
./analyze-singularity.sh <image> --type=rpm     [rpm]
./analyze-singularity.sh <image> --type=pip     [pip]
./analyze-singularity.sh <image> --type=apt     [apt]
./analyze-singularity.sh <image> --type=node    [Node]
```

Here is a quick example:

```bash
singularity pull --name vsoch-hello.simg shub://vsoch/hello-world
./analyze-singularity.sh vsoch-hello.simg
```

If you want to use sudo for the various commands:

```bash
sudo -E ./analyze-singularity.sh vsoch-hello.simg
```
```
container-diff is installed!
tar is installed!
singularity is installed!

Image: vsoch-hello.simg
(1/7) Creating build folders...
(2/7) Exporting filesystem...
Building from local image: vsoch-hello.simg
Singularity container built: /tmp/tmp.JUrsSuUp1Q/build
Cleaning up...
(3/7) Creating layer...
(4/7) Dummy metadata...
(5/7) Finishing package!
(6/7) Running container analyze
Retrieving image /tmp/tmp.JUrsSuUp1Q/4d398430ceded6a261a2304df3e75efe558892ba94eec25d2392991fe3a13dce.tar from source Tar Archive
Retrieving analyses
(7/7) Cleaning up!
Complete. Result is at:
/tmp/tmp.JUrsSuUp1Q/singularity-analyze-4d398430ceded6a261a2304df3e75efe558892ba94eec25d2392991fe3a13dce.json
```

And then go forth and use the output json files in all your awesome analyses!

## Enhancements
Here are some ideas for features to add!

 - Adding labels and Singularity environment to analyze export
 - Another script wrapper for the diff command of container-diff
 - When proper integration of Singularity goes into Go, adding to Container Diff proper
