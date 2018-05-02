# Compare Ubuntus

This example will show how to extract json objects of files and packages
for sets of images. In this case, we will extract the ubuntu family of
images to see if we can see changes over the years! If you want the version of
this script intended for use in the Docker container that also produces a
simple visualization, see [compare-containers](../compare-containers).

In the script, we set the list of Docker images (to be converted to Singularity)
that we want to compare:

```bash
declare -a uris=("ubuntu:12.04" "ubuntu:14.04" "ubuntu:16.04" "ubuntu:17.04" "ubuntu:18.04")
```

Also note that it's important you have the executable on your path for [analyze-singularity.sh](../../analyze-singularity.sh)
along with [container-diff](https://github.com/GoogleContainerTools/container-diff).


```bash
export PATH=$PATH:../../
```

I tested running with sudo

```
sudo -E ./compare_ubuntu.sh
```

If you want to move the output from the present working directory to a data folder
(as I did) uncomment out the bottom of the script.

```
# And just for repo saving, added to data
# mkdir -p data
# mv *.json data
```

That's it!
