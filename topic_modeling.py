from gensim import corpora, models
import re
import pyLDAvis
import pyLDAvis.gensim
from zh_tokenize import tokenize_r_stop_punc
import warnings
warnings.filterwarnings("ignore")
import pandas as pd

def plot_lda_single(t, num_topics, nlp, fname, num_words):
    docs = [tokenize_r_stop_punc(nlp, t)]
    # docs = [words, words]

    dictionary_LDA = corpora.Dictionary(docs)
    corpus = [dictionary_LDA.doc2bow(list_of_tokens) for list_of_tokens in docs]

    lda_model = models.LdaModel(corpus, num_topics=num_topics, \
                                  id2word=dictionary_LDA, \
                                  passes=4, alpha=[0.01]*num_topics, \
                                  eta=[0.01]*len(dictionary_LDA.keys()))

    # lda_model.save(fname+"_lda_single")

    vis = pyLDAvis.gensim.prepare(topic_model=lda_model, corpus=corpus, dictionary=dictionary_LDA)
    pyLDAvis.save_html(vis, fname+'.html')

    topics = lda_model.show_topics(formatted=True, num_topics=num_topics, num_words=num_words)
    pred_df = pd.DataFrame([(el[0]+1, el[1]) for el in topics], columns=['topic #', 'words in topic'])
    
    return pred_df

def plot_lda(df, num_topics, nlp, fname, num_words):
    docs = []
    for t in df["Text"]:
        words = tokenize_r_stop_punc(nlp, t)
        docs.append(words)

    dictionary_LDA = corpora.Dictionary(docs)
    dictionary_LDA.filter_extremes(no_below=1)
    corpus = [dictionary_LDA.doc2bow(list_of_tokens) for list_of_tokens in docs]

    lda_model = models.LdaModel(corpus, num_topics=num_topics, \
                                  id2word=dictionary_LDA, \
                                  passes=4, alpha=[0.01]*num_topics, \
                                  eta=[0.01]*len(dictionary_LDA.keys()))

    # lda_model.save(fname+"_lda")

    vis = pyLDAvis.gensim.prepare(topic_model=lda_model, corpus=corpus, dictionary=dictionary_LDA)
    pyLDAvis.save_html(vis, fname+'.html')
    
    topics = lda_model.show_topics(formatted=True, num_topics=num_topics, num_words=num_words)
    pred_df = pd.DataFrame([(el[0]+1, el[1]) for el in topics], columns=['topic #', 'words in topic'])
    
    return pred_df

def predict_topics(df, nlp, text, num_topics, num_words, model_name):
    lda_model = models.LdaModel.load(model_name)
    tokens = tokenize_r_stop_punc(nlp, text)
    topics = lda_model.show_topics(formatted=True, num_topics=num_topics, num_words=num_words)
    print(topics)

    docs = []
    for t in df["Text"]:
        words = tokenize_r_stop_punc(nlp, t)
        docs.append(words)

    dictionary_LDA = corpora.Dictionary(docs)
    # dictionary_LDA.filter_extremes(no_below=1)

    pred_df = pd.DataFrame([(el[0]+1, round(el[1],2), topics[el[0]][1]) for el in lda_model[dictionary_LDA.doc2bow(tokens)]], columns=['topic #', 'weight', 'words in topic'])
    
    return pred_df