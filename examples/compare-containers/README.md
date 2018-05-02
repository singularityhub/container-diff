# Compare Containers

The goal of this work is to make a human friendly tool for better comparing containers.

## Approach
We will build a Docker image to calculate pairwise comparisons for 
some list of containers (including Docker and/or Singularity) 
and calculate an information coefficient (for similarity)
based on the filesystem content. The visualizations and simple metrics are by 
courtesey of the [Singularity Python](https://www.github.com/vsoch/singularity-python/blob/v2.5/singularity/analysis)
analysis tools.

We will calculate a similarity matrix to show pairwise, and then link to plots
that show each container against the other, specifically highlighting files added,
files removed, and files shared. The outputs will be web reports and data files
for your use! 

## Build

```
docker build -t vanessa/compare-containers .
```

## Usage
The compare-containers image can support comparison between Docker and Singularity containers,
in any combination that you like. We do this by way of exporting Singularity containers to .tar.gz,
which is installed. Usage looks like any of the following. Note that for all of these,
the various extraction tools print out error / warning messages for what I think are symlinked 
(non existing files) that are attempting to be assessed for a size:


```
# Compare two Docker containers
mkdir -p /tmp/web
docker run -v /tmp/web:/data -p 8888:8888 -it vanessa/compare-containers centos:6 centos:7
```
```
1. Staring extraction for 2 containers.
/data/centos:6-files.json
/data/centos:7-files.json
2. Calculating comparisons
Open browser to http://0.0.0.0:8888
```

 - the container will serve it's content at port 8888, so you need to expose it
 - you should bind to /data if you want to keep the outputs.

The resulting output files are also saved to `/data` in the container (mounted at `/tmp/web` in the example above).

```bash
 ls /tmp/web/
centos:6-files.json        centos:7-to-centos:6.html
centos:6-to-centos:6.html  centos:7-to-centos:7.html
centos:6-to-centos:7.html  index.html
centos:7-files.json        information-coefficient-scores.tsv
```

## Development
Make sure you are in the directory with some web folder - we will map this to
our container so the web report (output) and data outputs are persisted on the host.

```
docker run -v $PWD:/code -v $PWD/web:/data -p 80:80 --entrypoint bash -it vanessa/compare-containers
```
