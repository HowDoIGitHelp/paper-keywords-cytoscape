import json
import pandas as pd


#columns = ['pk','authors','affiliation','venue','year','title','keywords','citations_5']
#data = pd.DataFrame(columns = columns)

#for row in raw_data_object:
#    if row['model'] == 'papers.paper':
#        data.append(pd.DataFrame(dict([('pk',row['pk'])] + list(map(lambda col : (row, row['fields'][col]),columns[1:]))),columns))


#with open('output_27.json','r') as json_file:
#    raw_data_object = json.loads(json_file.read())

#    with open('data2000.json','w+') as output:
#        json.dump(raw_data_object[:2000],output)

def dump_pickle(infile):
    with open(infile,'r') as json_file:
        raw_data_object = json.loads(json_file.read())

    keypaper_set = set()
    paper_metrics_set = set()
    keyword_set = set()

    unique_pk_set = set()

    for row in raw_data_object:
        if row['model'] == 'papers.paper' and row['pk'] not in unique_pk_set:
            paper_metrics_set.add((row['pk'],row['fields']['title'],str(row['fields']['authors']),row['fields']['pagerank_5']))
            for keyword in row['fields']['keywords']:
                keyword_set.add(keyword.lower())
                keypaper_set.add((keyword.lower(),row['pk']))
            unique_pk_set.add(row['pk'])

    keypaper_df = pd.DataFrame(keypaper_set,columns=['keyword','pk'])
    paper_metrics_df = pd.DataFrame(paper_metrics_set,columns=['pk','title','authors','pagerank_5'])
    paper_metrics_df = paper_metrics_df.set_index('pk')

    keywords_df = pd.DataFrame(keyword_set,columns=['keywords'])

    keypaper_df.to_pickle('keypaper.pkl')
    paper_metrics_df.to_pickle('paper_metrics.pkl')
    keywords_df.to_pickle('keywords.pkl')

dump_pickle('data600.json')
