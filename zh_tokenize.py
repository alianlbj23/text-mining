import opencc

def tokenize(nlp, text):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')

    doc = nlp(cc_ts.convert(text))

    words = []
    for tok in doc:
        words.append(cc_st.convert(tok.text))
        
    return words

def tokenize_r_stop_punc(nlp, text):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    stopwords = open("twzh_stopwords.txt", "r", encoding="utf-8").read().split("\n")
    
    proper_nouns = ['尼克·亚当斯', '厄尼斯特·海明威', '迪克·包尔顿', '比利·泰博萧', 
             '施顾己', '史顾己', '史顾矩', '狄更斯',
             '约翰', '菲尔法斯', '费尔法斯', '费尔法克司',"伊莉莎白","伊丽莎白",
             "布利格斯","布礼革","梅森","约拿‧梅森","约拿斯·梅森","贝莎‧梅森",
             "理察·梅森","贝莎‧安朵娜塔‧梅森","贝莎·安托妮塔·梅森","安朵娜塔",
             "安托妮塔","柏莎","亚黛儿","阿黛尔","阿黛拉","莉亚","莉雅",
             "达美尔‧戴‧罗契斯特","爱德华‧费尔法斯‧罗契斯特","克里奥尔人","普尔",
             "葛瑞丝","葛瑞丝‧普尔","芳夏尔","爱先生","司芬克斯","参孙","印第安人",
             "布兰琪‧英葛兰","白兰琪•英葛","罗兰","贾馨塔","嘉欣姐","克莱拉","柯拉娃",
             "席琳","席琳·薇汉斯","海森先生","罗彻斯特","罗契斯特","简爱","苏菲""伍德",
             "马斯顿荒原战役","试罪法",
             "马德拉","马得拉群岛","牙买加","西班牙","英格兰","芬迪恩庄园",
             "米尔科特","桑费尔德庄园",'西印度群岛',"巴黎","圣彼得堡","罗马",
             "拿坡里","那不勒斯","佛罗伦斯",
             '尼克', '乔治', '迪克•博尔顿', '艾迪',
             '比利•泰布肖', '迪克', '怀特', '麦克纳利',
             '亨利', '狄克．波尔顿', '比利．塔比索', '狄克', '麦克奈利',]
    nlp.tokenizer.pkuseg_update_user_dict(proper_nouns)
    
    doc = nlp(cc_ts.convert(text))

    words = []
    for tok in doc:
        if cc_st.convert(tok.text) not in stopwords:
            words.append(cc_st.convert(tok.text))
        
    return words

def tokenize_r_stop_punc_simple(nlp, text):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    stopwords = open("twzh_stopwords.txt", "r", encoding="utf-8").read().split("\n")

    doc = nlp(cc_ts.convert(text))

    words = []
    for tok in doc:
        if cc_st.convert(tok.text) not in stopwords:
            words.append(tok.text)
        
    return words