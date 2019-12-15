import cv2
from urllib.request import urlopen
import urllib.parse as parse
import simplejson
from os.path import join, isfile
import os
import numpy as np

dataset = [join('static/database', f) for f in os.listdir('static/database') if isfile(join('static/database', f))]


BASE_LINK = 'http://localhost:8983/solr/csdl_dpt/select?q='

# method to compare
method = {'Correlation': cv2.HISTCMP_CORREL, 'Chi-Squared': cv2.HISTCMP_CHISQR,
          'Intersection': cv2.HISTCMP_INTERSECT, 'Hellinger': cv2.HISTCMP_BHATTACHARYYA}

def convert_img_to_hist(img):
    img = cv2.imread(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (225, 225))
    img = cv2.GaussianBlur(img, (5, 5), 0)
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist


# query is link_img, dataset is a set of link in database
def compare(query, method_name, dataset):
    index = {}
    images = {}
    id = {}
    img_link = query
    query = convert_img_to_hist(query)
    for imgPath in dataset:
        img = cv2.imread(imgPath)
        images[imgPath] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hist = convert_img_to_hist(imgPath)
        index[imgPath] = hist
    results = {}
    reverse = False
    # correlation, intersection: larger value indicates higher similarity
    # Chi-squared, hellinger: smaller value indicates higher similarity

    if method_name in ('Correlation', 'Intersection'):
        reverse = True
    for (k, hist) in index.items():
        d = cv2.compareHist(query, hist, method[method_name])
        if(d<0.7):
            continue
        results[k] = d
    results = sorted([(v, k) for (k, v) in results.items()], reverse=reverse)
    results = [k for (_, k) in results]
    results = np.array(results)[:10]
    return results

def get_conn(link):
    conn = urlopen(link)
    return conn

def normalizier_query(query):
    if(query == 'None'):
        return parse.quote('type:') +'*&rows=852'
    return parse.quote('type:"{}"'.format(query)) + '&rows=852'

def executeQuery(query, image_query):
    query = normalizier_query(query)
    link = BASE_LINK + query
    conn = get_conn(link)
    data = simplejson.load(conn)
    data = data['response']['docs']
    id = {}
    datasets = []
    for d in data:
        temp_data = []
        for img in d['images']:
            temp_data.append('static{}'.format(img))
        if(len(compare(image_query,'Correlation',temp_data))==0):
            continue
        img = compare(image_query, 'Correlation', temp_data)[0]
        datasets.append(img)
        id[img] = d
    print(id)
    return datasets, id
# print(compare('static/query/ao.jpeg','Correlation',dataset))
executeQuery('áo blazer nam','static/query/ao.jpeg')