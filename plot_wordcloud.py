from wordcloud import WordCloud
def plot_wordcloud(words, max_num):
    text = " ".join(words)
    wc = WordCloud(background_color="white", max_words=max_num, width=600, contour_width=3, contour_color='steelblue', 
                   font_path="./resources/粗明體.ttc", prefer_horizontal=0.9)

    wc.generate(text)
    return wc.to_image()