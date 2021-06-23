#!/usr/bin/env python3
import datetime
import bibtexparser
import pandas as pd
import math


def clean(text):
    if pd.isna(text):
        return ''
    return text.replace('{','').replace('}','')

def yyyymmdd(row):
    def month(month_name):
        datetime_object = datetime.datetime.strptime(month_name, "%b")
        return f'{datetime_object.month:02}'
    mon = '01' if pd.isna(row['month']) else month(row['month'])
    return str(row['year'])+'-'+mon+'-01'

def reference(row, max_authors=99):
    author = authors(row, max_authors)
    journal = clean(row['journal'])
    vol = row['volume']
    pp = row['pages']
    yyyy = row['year']
    arx_ident = clean(row['eprint'])
    if not pd.isna(vol) and not pd.isna(pp):
        return author+", [{} **{}**, {} ({})](http://dx.doi.org/{})".format(journal, vol, pp, yyyy, clean(row['doi']))
    elif arx_ident != '':
        return author+', '+arXiv(row)
    else:
        return author+', '+(journal.strip() + ' (' + str(yyyy) + ')').strip()

def flatten(list, sep=' '):
    text = ''
    for each in list:
        text += each
        if each!=list[-1] : text += sep
    return text

def author_list(row):
    list = clean(row['author']).split(' and ')
    fixed_list = []
    for each in list:
        name = each.split(',')
        name.reverse()
        fixed_list.append(flatten(name,' ').strip())
    return fixed_list

def arXiv(row):
    ident = clean(row['eprint'])
    if ident == '' : return ''
    return '[arXiv:'+ident+'](http://arxiv.org/abs/'+ident+')'


def authors(row, max=99, etal=4):
    al = author_list(row)
    if len(al) <= max:
        return flatten(al,', ')
    else:
        return flatten(al[:etal],', ')+', _et al._'

def file_name(row):
    t = clean(row['title']).replace(',','').replace('.','').replace('/','')
    l = t.split(' ')
    for each in l:
        each = ''.join(e for e in each if e.isalnum())
    title = flatten(l,'_')
    return yyyymmdd(row)+'-'+title+'.md'

def doi(row):
    ident = clean(row['doi'])
    if ident == '' : return ''
    return '[doi:'+ident+'](http://dx.doi.org/'+ident+')'

with open("bib.bib") as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

df = pd.DataFrame(bib_database.entries)
# selection = df[['doi', 'number']]
# selection.to_csv('temp.csv', index=False)

df = df.sort_values(['year', 'month'])

header = '---\nusemathjax: true\nlayout: publication\n'

for index, row in df.iterrows():
    fname = file_name(row)
    text = header+'title: '+clean(row['title']) + '\n---\n\n'
    text += reference(row,4)+'\n\n'
    text += doi(row)+'\n\n'
    text += arXiv(row)+'\n\n'
    text += str(row['abstract'])+'\n\n'
    text += " * "+reference(row)+'\n'
    print(fname)
    file  = open("./out/"+fname, "w+")
    file.write(text)
