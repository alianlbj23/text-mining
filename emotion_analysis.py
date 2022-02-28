from cnsenti import Emotion
import pandas as pd
import opencc
from decimal import Decimal, ROUND_HALF_UP

def plot_emotion_distr(text, fname, nlp):
    cc_ts = opencc.OpenCC('tw2s')
    cc_st = opencc.OpenCC('s2tw')
    stopwords = open("twzh_stopwords.txt", "r", encoding="utf-8").read().split("\n")

    doc = nlp(cc_ts.convert(text))

    words = []
    for tok in doc:
        if cc_st.convert(tok.text) not in stopwords:
            words.append(tok.text)

    emotion = Emotion()
    # test_text = cc_ts.convert(document)
    result = emotion.emotion_count(" ".join(words)) 
    # print(result)
    
    text_id = []
    for j in range(8):
        if j == 0: text_id.append(fname)
        else: text_id.append("")
    
    w_id = []
    ws_pr = []
    ws_ha = []
    ws_sa = []
    ws_an = []
    ws_fe = []
    ws_hat = []
    ws_su = []
    emotions = []
    counts = []

    for i, w in enumerate(words):
        w_id.append(i+1)
        w_id.append(i+1)
        w_id.append(i+1)
        w_id.append(i+1)
        w_id.append(i+1)
        w_id.append(i+1)
        w_id.append(i+1)
        emotions.append("Preference")
        emotions.append("Happiness")
        emotions.append("Sadness")
        emotions.append("Anger")
        emotions.append("Fear")
        emotions.append("Hate")
        emotions.append("Surprise")
        temp = [0,0,0,0,0,0,0]
        if w in emotion.Haos:
            temp[0] = 1
            ws_pr.append(w)
            for j in temp:
                counts.append(j)
        elif w in emotion.Les:
            temp[1] = 1
            ws_ha.append(w)
            for j in temp:
                counts.append(j)
        elif w in emotion.Ais:
            temp[2] = 1
            ws_sa.append(w)
            for j in temp:
                counts.append(j)
        elif w in emotion.Nus:
            temp[3] = 1
            ws_an.append(w)
            for j in temp:
                counts.append(j)
        elif w in emotion.Jus:
            temp[4] = 1
            ws_fe.append(w)
            for j in temp:
                counts.append(j)
        elif w in emotion.Wus:
            temp[5] = 1
            ws_hat.append(w)
            for j in temp:
                counts.append(j)
        elif w in emotion.Jings:
            temp[6] = 1
            ws_su.append(w)
            for j in temp:
                counts.append(j)
        else:
            for j in temp:
                counts.append(j)
                
    data = {"Translator/Publisher":text_id, "Emotion":["Preference", "Happiness", "Sadness", "Anger", "Fear", "Hate", "Surprise", ""], 
            "Words":[",".join([cc_st.convert(w) for w in ws_pr]), ",".join([cc_st.convert(w) for w in ws_ha]), 
                     ",".join([cc_st.convert(w) for w in ws_sa]), ",".join([cc_st.convert(w) for w in ws_an]), 
                     ",".join([cc_st.convert(w) for w in ws_fe]), ",".join([cc_st.convert(w) for w in ws_hat]), 
                     ",".join([cc_st.convert(w) for w in ws_su]), ""], 
            "Counts":[str(len(ws_pr)), str(len(ws_ha)), str(len(ws_sa)), str(len(ws_an)), str(len(ws_fe)), str(len(ws_hat)), str(len(ws_su)), ""], 
            "Proportion":[str(Decimal(str(Decimal(str(len(ws_pr)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%",
                          str(Decimal(str(Decimal(str(len(ws_ha)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%",
                          str(Decimal(str(Decimal(str(len(ws_sa)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%",
                          str(Decimal(str(Decimal(str(len(ws_an)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%",
                          str(Decimal(str(Decimal(str(len(ws_fe)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%",
                          str(Decimal(str(Decimal(str(len(ws_hat)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%",
                          str(Decimal(str(Decimal(str(len(ws_su)))/Decimal(str(sum(counts))))).quantize(Decimal('.00'), ROUND_HALF_UP)*Decimal(str(100)))+"%", ""]}
    emo_df = pd.DataFrame(data)
#     all_em_df = pd.concat([all_em_df, emo_df], axis=0)

    emotion_df = pd.DataFrame({"Word_Position": w_id, "Emotion": emotions, "Emotion_Appearance": counts})
#     sns.set(font_scale=1.5)
#     sns.set_style("whitegrid")
#     plt.figure(figsize=(25,3))
#     plt.title('Emotion Distribution')
#     ax = sns.lineplot(data=emotion_df, x="Word_Position", y="Emotion_Appearance", hue="Emotion")
#     ax.set_xlim(1,len(words))
#     ax.set_xticks(range(1,len(words),10))
#     ax.set_yticks([0,1])
#     plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#     ax.figure.savefig("C:/Users/BRNM/Desktop/Project_Practice/Plots/"+fname+"_emotion_distr.png", bbox_inches='tight')
    
    return emo_df, emotion_df