import pickle


def run():
    with open('word_dict_pickle', 'rb') as f:
        MATRIX = pickle.load(f)

    with open('word_dict_pickle', 'wb') as f:
        pickle.dump(MATRIX, f)
