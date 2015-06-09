import logging
import numpy as np

_default_database = "db/features.word2vec"


def validate_word(w, features):
    return w in features

def load_features(f_features=_default_database):
    msg = "Loading feature file {}".format(f_features)
    logging.warning(msg)

    import cPickle as _pickle
    with open(f_features) as FIN:
        features = _pickle.load(FIN)

    features.syn0 = np.load(f_features + ".syn0.npy")

    features.init_sims()
    return features

def closest_approach(x1,x2,W):
    '''
    Define a line segement, L between the two input vectors x1,x2.
    Parameterize the line by t, that linearly goes from 0->1 as x1->x2.
    For each point in the matrix A, return the distance to the line d,
    and where along the line t.
    '''

    x21 = x2 - x1
    x21_norm = np.linalg.norm(x21)

    X10 = x1 - W
    X10_21 = X10.dot(x21)

    T = -X10_21 / x21_norm ** 2

    X10_norm = np.linalg.norm(X10, axis=1)

    D2 = (X10_norm * x21_norm) ** 2 - X10_21 ** 2
    D2 /= x21_norm ** 2
    D = np.sqrt(D2)

    return D, T


def transorthogonal_words(w1, w2, features, word_cutoff=25):

    W  = features.syn0norm
    x1 = features[w1]
    x2 = features[w2]
    
    D, T = closest_approach(x1,x2,W)

    close_idx = np.argsort(D)[:word_cutoff]
    WORDS = np.array([features.index2word[idx] for idx in close_idx])
    timeline = abs(T[close_idx])
    dist = D[close_idx]

    chrono_idx = np.argsort(timeline)

    return (WORDS[chrono_idx],
            dist[chrono_idx],
            timeline[chrono_idx])


if __name__ == "__main__":

    import argparse

    desc = '''
    transorthogonal words

    Moves across the lines spanned by the orthogonal space. 
    Interesting cases: boy man mind body fate destiny 
    teacher scientist girl woman conservative liberal 
    hard soft religion rationalism
    '''
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-f", "--features",
                        help="word2vec feature file",
                        default=_default_database)
    parser.add_argument("--word_cutoff", '-c',
                        help="Number of words to select",
                        type=int, default=25)
    parser.add_argument("words",
                        nargs="*",
                        help="Space separated pairs of words example: "
                        "python word_path.py boy man mind body")

    args = parser.parse_args()

    if args.words is None:
        msg = "You must either pick at least two words"
        raise SyntaxError(msg)

    if len(args.words) % 2 != 0:
        msg = "You input an odd number of words!"
        raise SyntaxError(msg)

    word_pairs = [[w1, w2] for w1, w2 in zip(args.words[::2],
                                             args.words[1::2])]
    
    features = load_features(args.features)


    for w1, w2 in word_pairs:

        result = transorthogonal_words(w1, w2,
                                       features,
                                       args.word_cutoff)

        for word, time, distance in zip(*result):
            print "{:0.5f} {:0.3f} {}".format(time, distance, word)
        print
