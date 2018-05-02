# Trees

# Here we want to create a visual grid that shows an overall similarity score
# between two lists of files, along with rendered trees for each.
# For the similarity metric we will use

import json
import pandas
import os
from glob import glob
import seaborn as sns
from singularity.views import make_container_tree, get_template
from singularity.analysis.compare import ( compare_files, compare_lists )

data = glob('data/*files.json')
scores = pandas.DataFrame()

# Lookup for files
lookup = dict()

if not os.path.exists('web'):
    os.mkdir('web')
                                                                                                                                   
for d in data:
    datum = json.load(open(d,'r'))
    osname = os.path.basename(d).replace('-files.json', '')
    files = []
    for f in datum[0]['Analysis']:
        files.append(f['Name'])

    lookup[osname] = files

htmls = dict()

# Now calculate differences (and html tree) for each.
for name1, files1 in lookup.items():
    for name2, files2 in lookup.items():

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
                                               '{{ container_name }}': "%s Tree" %osname})

        with open('web/%s-to-%s.html' %(name1,name2), 'w') as filey:
            filey.writelines(html)

# To plot scores quickly
sns.heatmap(scores, annot=True)
plt.title('Ubuntu Container Similarity Based on Filesystem')
plt.show()

values = ',\n'.join([ str(values.tolist()) for row, values in scores.items()])

# Plot via html
template = get_template('heatmap', {'{{ title }}': "Similarity of Ubuntu Containers based on Filesystem",
                                    '{{ data }}': values,
                                    '{{ X }}': str(scores.index.tolist()),
                                    '{{ Y }}': str(scores.columns.tolist())} )

with open('web/index.html','w') as filey:
    filey.writelines(template)


# Pandas for Packages

import json
import pandas
import os
from glob import glob

data = glob('data/*packages.json')
                                                                                                                                                
df = pandas.DataFrame(columns=['container','name','size','version'])
for d in data:
    datum = json.load(open(d,'r'))
    osname = os.path.basename(d).replace('-packages.json', '')
    for package in datum[0]['Analysis']:                                                                                                                                        
        uid = "%s-%s" %(osname, package['Name'])
        df.loc[uid,:] = [osname,        
                         package['Name'],
                         package['Size'],
                         package['Version']]
    
df.to_csv('data/packages.tsv',sep='\t')
