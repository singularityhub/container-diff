#!/usr/bin/env python
#
# Copyright (C) 2018 Vanessa Sochat.
#
# This is a basic python script that will compare two containers. If we have
# a Docker container (or container-diff) supported container, we use that.
# If we have Singularity, we do a conversion first.
# The conversion itself is just an information coefficient from the flies
# github.com/vsoch/singularity-python/blob/v2.5/singularity/analysis/metrics.py
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


from spython.main import Client
from spython.utils import run_command

import argparse
import http.server
import json
import os
import pandas
from random import choice
import re
import shutil
import socketserver
import sys

from singularity.views import make_container_tree, get_template
from singularity.analysis.compare import ( compare_files, compare_lists )


# Sanity Checks ################################################################
# Make sure we have environment variables, exit if not

analyze = os.environ.get('ANALYZE_SINGULARITY', 'analyze-singularity.sh')
output = os.environ.get('WEB_OUTPUT', '/data')


# Helper #######################################################################


def get_parser():
    parser = argparse.ArgumentParser(description="Container Comparison Tool")
    parser.add_argument('containers', nargs='*',
                        help="list of containers to compare.", 
                        default=None)
    return parser


def run_analyze(container, dest, files=True):
    ''' a wrapper to run the command to generate the json object, calling
        analyze-singularity.sh that should be on the path, and renaming
        to the file wanted by the calling script.
    '''

    cmd = [analyze, container]
    if files is True:
        cmd.append('--type=file')
    try:
        stdout, stderr = Client._run_command(cmd)

        files = [x for x in stdout.split('\n') if x]
        output_file = files[-1]
        if os.path.exists(output_file):
            shutil.move(output_file, dest)
        return dest
    except:
        print('Problem with %s' %cmd)



def run_container_diff(container, dest, files=True):
    ''' a wrapper around container diff.
    '''

    cmd = ['container-diff', 'analyze', '--json']
    if files is True:
        cmd.append('--type=file')

    cmd = cmd + [container]
    stdout, stderr = Client._run_command(cmd)

    with open(dest,'w') as filey:
        filey.writelines(stdout)

    return dest



def main():
    '''main is the entrypoint to run a container comparison.
    '''

    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    if args.containers in [None, '', []]:
        print('Please provide a list of one or more containers to compare.')


# Step 1: Extraction of files

    print('1. Staring extraction for %s containers.' %len(args.containers))
  
    # We will save lists of files for comparison
    data = []

    for container in args.containers:

        # if the file exists, assume it's singularity

        func = run_analyze

        if os.path.exists(container):
            print('Found Singularity container file %s' %container)

        # If it starts with shub:// or docker:// we want to singularity pull

        if re.search('^(docker|shub)[://]', container):
            print('Pulling Singularity container %s' %container)
            container = Client.pull(container, pull_folder='/tmp')

        # Otherwise, must be docker container

        else:
            func = run_container_diff

        # Prefix of container for output
        name = os.path.basename(container)

        # Just generate files
        output_files = os.path.join(output, '%s-files.json' %name)

        # Run the analyze-singularity.sh for each of files and packages
        if not os.path.exists(output_files):
            print("Performing Extraction for %s" %container)
            dest = func(container, dest=output_files)
        else:
            dest = output_files
        print(dest)
        data.append(dest)

# Step 2: Generation of Web Interfaces

    print('2. Calculating comparisons')
    scores = pandas.DataFrame()

    # Lookup for files
    lookup = dict()
    htmls = dict()
                                                                                                                                   
    for d in data:
        datum = json.load(open(d,'r'))
        osname = os.path.basename(d).replace('-files.json', '')
        files = []
        for f in datum[0]['Analysis']:
            files.append(f['Name'])

        lookup[osname] = files

    # Now calculate differences (and html tree) for each.
    for name1, files1 in lookup.items():
        for name2, files2 in lookup.items():

            # browser can have trouble with weird characters
            name = ("%s-%s" %(name1, name2)).replace(':','').replace('/','-')

            # Calculate the score in matrix
            comparison = compare_lists(files1, files2)
            score = compare_files(files1, files2)
            scores.loc[name1,name2] = score

            # Create labels lookup to show which were added and removed
            labels = dict()
            allfiles = set(files1).union(set(files2))
            for afile in allfiles:
                if afile in comparison['shared']: labels[afile] = 'shared'
                elif afile in comparison['added']: labels[afile] = 'added'
                elif afile in comparison['removed']: labels[afile] = 'removed'

            # Generate tree that shows added and subtracted nodes
            tree = make_container_tree(allfiles, labels=labels)
            html = get_template('container_tree', {'{{ files | safe }}': json.dumps(tree['files']),
                                                   '{{ graph | safe }}': json.dumps(tree['graph']),
                                                   '{{ container_name }}': "%s --> %s Tree" %(name1, name2)})

            html_file = '%s/%s.html' %(output,name)
            htmls['%s vs. %s' %(name1, name2)] = html_file
            with open(html_file, 'w') as filey:
                filey.writelines(html)


    # Create web plot
    values = ',\n'.join([ str(values.tolist()) for row, values in scores.items()])

    # Write list of html files
    extra = '<br><div><h2>View Comparison</h2><ul>'
    for name, html_file in htmls.items():
        extra += '<li><a href="%s">%s</a></li>\n' %(os.path.basename(html_file), name)
    extra += '</ul></div></body>'

    # Plot via html
    template = get_template('heatmap', {'{{ title }}': "Similarity of Containers based on Filesystem",
                                        '{{ data }}': values,
                                        '{{ X }}': str(scores.index.tolist()),
                                        '{{ Y }}': str(scores.columns.tolist()),
                                        '</body>': extra })

    # Save scores for user as data frame
    scores.to_csv('%s/information-coefficient-scores.tsv' %output, sep='\t')

    with open('%s/index.html' %output,'w') as filey:
        filey.writelines(template)

    # Open browser there
    os.chdir(output)    
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8888), Handler) as httpd:
        print("Open browser to http://0.0.0.0:8888")
        httpd.serve_forever()


if __name__ == '__main__':
    main()
