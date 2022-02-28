from textrank4zh import TextRank4Keyword, TextRank4Sentence
from decimal import Decimal, ROUND_HALF_UP
import plotly.graph_objs as go
import opencc
import pandas as pd

def keywords_extraction(df, kw_num):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    text = cc_ts.convert("".join(t for t in df["Text"]))

    tr4w = TextRank4Keyword()

    tr4w.analyze(text=text, lower=True, window=2)    # py2中text必須是utf8編碼的str或者unicode對象，py3中必須是utf8編碼的bytes或者str對象

    kws = []
    kws_weight = []

    for item in tr4w.get_keywords(kw_num, word_min_len=1):
        kws.append(cc_st.convert(item.word))
        kws_weight.append(float(Decimal(str(item.weight)).quantize(Decimal('.000'), ROUND_HALF_UP)))
    #     print(cc_st.convert(item.word), Decimal(str(item.weight)).quantize(Decimal('.000'), ROUND_HALF_UP))

    kws_df = pd.DataFrame({"Keyword":kws, "Weight":kws_weight})
    kws_df = kws_df.sort_values(by=['Weight'])
    data = [go.Bar(x=kws_df["Weight"], y=kws_df["Keyword"], orientation='h', marker=go.bar.Marker(color='#4A225D'))]
    
    return data

def keywords_extraction_single_text(t, kw_num):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    text = cc_ts.convert(t)

    tr4w = TextRank4Keyword()

    tr4w.analyze(text=text, lower=True, window=2)    # py2中text必須是utf8編碼的str或者unicode對象，py3中必須是utf8編碼的bytes或者str對象

    kws = []
    kws_weight = []

    for item in tr4w.get_keywords(kw_num, word_min_len=1):
        kws.append(cc_st.convert(item.word))
        kws_weight.append(float(Decimal(str(item.weight)).quantize(Decimal('.000'), ROUND_HALF_UP)))
    #     print(cc_st.convert(item.word), Decimal(str(item.weight)).quantize(Decimal('.000'), ROUND_HALF_UP))

    kws_df = pd.DataFrame({"Keyword":kws, "Weight":kws_weight})
    kws_df = kws_df.sort_values(by=['Weight'])
    data = [go.Bar(x=kws_df["Weight"], y=kws_df["Keyword"], orientation='h', marker=go.bar.Marker(color='#4A225D'))]
    
    return data

def text_summarizer(df, sents_num):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    text = cc_ts.convert("".join(t for t in df["Text"]))

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source='all_filters')

    sents = []
    for item in tr4s.get_key_sentences(num=sents_num):
        sents.append(cc_st.convert(item.sentence))
    
    summarization = "。".join(sents)+"。"
    return summarization

def text_summarizer_single_text(t, sents_num):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    text = cc_ts.convert(t)

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source='all_filters')

    sents = []
    for item in tr4s.get_key_sentences(num=sents_num):
        sents.append(cc_st.convert(item.sentence))
    
    summarization = "。".join(sents)+"。"
    return summarization