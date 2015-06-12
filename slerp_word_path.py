import collections
import numpy as np
import word_path as wp

def build_local_features(w0,w1,features,n_local):
    local_features = wp.Features(empty=True)
    vocab,_,_ = wp.transorthogonal_words(w0,w1,features,n_local)
    feat = np.vstack([features[w] for w in vocab])

    local_features.vocab = vocab
    local_features.features = feat

    local_features.reindex()
    return local_features

def slerp_points(x0,x1,slerp_n):
    ''' N-dimensional slerp interpolation '''
    theta = np.arccos(x0.dot(x1))
    st = np.sin(theta)

    T  = np.linspace(0,1,slerp_n)
    L1 = np.sin((1-T)*theta)/st
    L2 = np.sin(T*theta)/st
    SL = np.outer(L1,x0) + np.outer(L2,x1)
    
    return (SL.T / np.linalg.norm(SL,axis=1)).T

def slerp_word_path(w0,w1,features,
                    slerp_n=20,
                    word_cutoff=35,
                    n_local=3000):

    lf = build_local_features(w0,w1,features,n_local)

    T  = np.linspace(0,1,slerp_n)
    SL = slerp_points(lf[w0],lf[w1],slerp_n)

    GEO = []

    for t,L in zip(T,SL):
        cosine_dist   = np.dot(lf.features, L)
        cosine_dist[cosine_dist>=1] = 1.0
        geodesic_dist = np.arccos(cosine_dist)

        GEO.append(geodesic_dist)

    GEO = np.vstack(GEO)

    # Only choose words that are closer to the path than an end point, e.g.
    # ignore this situation:         (o)  (x)------(x)
    # and accept this situtation:         (x)--o---(x)
    MIN_IDX = np.argmin(GEO,axis=0)
    CONCAVE_MASK = (MIN_IDX>0) & (MIN_IDX<slerp_n-1)

    idx_concave = np.where(CONCAVE_MASK)[0]
    vocab = np.array([lf.index2word(idx) for idx in idx_concave])
    dist  = geodesic_dist[CONCAVE_MASK]
    time  = np.array([T[idx] for idx in MIN_IDX[CONCAVE_MASK]])

    top_idx = np.argsort(dist)[:word_cutoff]
    vocab = vocab[top_idx]
    time  = time [top_idx]
    dist  = dist [top_idx]

    chrono_idx = np.argsort(time)
    vocab = vocab[chrono_idx]
    time  = time [chrono_idx]
    dist  = dist [chrono_idx]

    # Add back in the endpoints
    vocab = np.hstack([[w0],vocab,[w1]])
    time  = np.hstack([[0.],time, [1.]])
    dist  = np.hstack([[0.],dist, [0.]])

    return (vocab, dist, time)



#w1,w2 = "run","walk"
#w1,w2="teacher","scientist"
#w1,w2="fate","destiny"



features = wp.Features()
w0,w1 = "boy","man"

result = slerp_word_path(w0, w1, features, word_cutoff=25)

wp.print_result(result)
