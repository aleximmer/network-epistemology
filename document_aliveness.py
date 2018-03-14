import numpy as np
import pandas as pd
import pickle
from scipy.spatial.distance import cdist
from tqdm import tqdm

from loading import load_corpus, load_doc_topics


def obtain_min_dist_split(X_topic, years, max_mem=10**9):
    res = {}
    for year in tqdm(sorted(list(years))[1:]):
        cols = np.arange(0, 100)
        X_prev = X_topic[X_topic['year'] < year][cols]
        X_cur = X_topic[X_topic['year'] == year][cols]
        ix_stepsize = int(max_mem / len(X_cur))

        min_dist = pd.DataFrame(index=X_prev.index, columns=['min_dist', 'closest_doc'])
        for i in tqdm(range(0, len(X_prev), ix_stepsize)):
            dists = cdist(X_prev.iloc[i: i+ix_stepsize].values, X_cur.values, metric='cityblock')
            min_dist.iloc[i: i+ix_stepsize, 0] = dists.min(axis=1)
            min_dist.iloc[i: i+ix_stepsize, 1] = X_cur.index[dists.argmin(axis=1)]

        res[year] = min_dist
    return res


def obtain_min_distances(X_topic, years):
    res = {}
    for year in tqdm(sorted(list(years))[1:]):
        cols = np.arange(0, 100)
        X_prev = X_topic[X_topic['year'] < year][cols]
        X_cur = X_topic[X_topic['year'] == year][cols]
        min_dist = cdist(X_prev.values, X_cur.values, metric='cityblock').min(axis=1)
        min_dist = pd.DataFrame(min_dist, index=X_prev.index)
        res[year] = min_dist
    return res


if __name__ == '__main__':
    # compute distance list following the scheme
    # list[year] : DataFrame.loc[pubs before year] : dist to closest pub of year in [0, 1]
    print('load corpus')
    ids_corpus, _, dates_corpus = load_corpus()
    print('load doc topics')
    X_multopic = load_doc_topics()
    X_multopic = pd.DataFrame(X_multopic, index=ids_corpus)
    X_multopic['year'] = dates_corpus
    print('compute distances')
    min_dists = obtain_min_dist_split(X_multopic, set(dates_corpus), max_mem=10**9)
    print('dump results')
    pickle.dump(min_dists, open('data/min_dists.pkl', 'wb'))
    print('finished.')
