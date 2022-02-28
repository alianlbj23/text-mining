import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pandas as pd
import dash_table
import io
import base64
from plot_wordcloud import plot_wordcloud
import spacy
from zh_tokenize import tokenize, tokenize_r_stop_punc, tokenize_r_stop_punc_simple
import plotly.express as px
from parse_contents import parse_contents, parse_contents_for_mining
from ner_render import render, plot_ner_distr
import opencc
import re
import plotly.graph_objs as go
from text_rank import keywords_extraction, keywords_extraction_single_text, text_summarizer, text_summarizer_single_text
from emotion_analysis import plot_emotion_distr
from topic_modeling import plot_lda, predict_topics, plot_lda_single

nlp = spacy.load('zh_core_web_md') 

image_filename = './resources/logo_only.png' 
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Text Mining'

server = app.server

app.layout = html.Div(children=[
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'display':'inline-block', 'width': '2.5%', 'height': '2.5%'}),
    html.H1(children='Text Mining', style={'display':'inline-block', 'margin': '10px'}),
    html.Label('Please upload your file (.xls or .csv only):'),  #or download and use a sample
    html.P('\u26A0 It is necessary to have a "Translator/Publisher" and a "Text" column! \u26A0'),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ', html.A('Select Files')
            ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
            },
        # Allow multiple files to be uploaded
        multiple=True
    ),

    html.Div(id='output-data-upload'),
])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]

        df = [
            parse_contents_for_mining(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)][0]

        # filename = "".join((re.findall("Div\(\[H5\(\'(.*)\.[a-z]+\'\)\, DataTable", str(children[0]))))
        # loc_dt = datetime.datetime.today()
        # loc_dt_format = loc_dt.strftime("%Y%m%d_%H%M%S")
        # df.to_csv("C:/Users/BRNM/Desktop/Project_Practice/Website/Upload_Files/"+filename+"_"+loc_dt_format+".csv", encoding="utf-8", index=False)
        return [html.Div(children),
                html.Div(children=[
                    html.Br(),
                    html.H2(children='Word Cloud \u2601'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': str(i+1)} for i, t in enumerate(df["Translator/Publisher"])], 
                                placeholder="Select a text from the file",
                                id="text-selection1")]),
                    html.Label(["The Number of Words Produced in the Word Cloud (minimum value is 3)", dcc.Input(id='wordcloud-numws-slider', type='number', min=3)]),
                    html.Button("Generate Word Cloud", id="btn_wc", n_clicks=0),
                    html.Br(),
                    html.Button("Generate Word Cloud of All Texts", id="btn_wca", n_clicks=0),
                    html.Br(),
                    html.Br(),
                    dcc.Loading(id="loading-1", children=[html.Div(id="image_wc_upload")], type="default"),
                    html.Br(),
                    dcc.Loading(id="loading-11", children=[html.Div(id="image_wca_upload")], type="default"),
                    html.Br(),
                    html.Br(),

                    html.H2(children='Named Entity Recognition (NER) \U0001F4CD'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': str(i+1)} for i, t in enumerate(df["Translator/Publisher"])], 
                                placeholder="Select a text from the file",
                                id="text-selection2")]),
                    html.Button("Generate NER Marks", id="btn_nerm", n_clicks=0),
                    html.Br(),
                    html.Button("Generate NER Distribution", id="btn_nerd", n_clicks=0),
                    html.Br(),
                    html.Button("Compare NER Distribution of All Texts", id="btn_nerad", n_clicks=0),
                    html.Br(),
                    html.Br(),
                    html.Div(id="ner-labelling"),
                    html.Br(),
                    dcc.Loading(id="loading-2", children=[html.Div(id="ner_graph")], type="default"),
                    html.Br(),
                    dcc.Loading(id="loading-3", children=[html.Div(id="all_ner_graph")], type="default"),
                    html.Br(),
                    html.Br(),
                    
                    html.H2(children='Topic Modeling \U0001F50D'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': t} for i, t in enumerate(["All"]+list(df["Translator/Publisher"]))], 
                                placeholder="Select a text from the file",
                                id="text-selection7")]),
                    html.Label(["The Number of Topics", dcc.Slider(id='lda-slider', min=2, max=20, value=4, marks={str(num): str(num) for num in range(2,21)}, step=None)]),
                    html.I("\u26A0 Please enter a name for the topic modeling file."),
                    dcc.Input(id="input1", type="text", placeholder="topic_modeling_4topics", debounce=True),
                    html.Label(["The Number of Words Shown in Each Topic (minimum value is 1)", dcc.Input(id='topic_ws', type='number', min=1)]),
                    html.Button("Download a File", id="btn_lda"),
                    dcc.Loading(id="loading-11", children=[html.Div(id="lda_file")], type="default"),
                    html.Br(),
                    html.Br(),

                    html.H2(children='Keywords Extraction \U0001F4D1'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': str(i+1)} for i, t in enumerate(df["Translator/Publisher"])], 
                                placeholder="Select a text from the file",
                                id="text-selection3")]),
                    html.Label(["The Number of Keywords (minimum value is 5)", dcc.Input(id='kw-slider', type='number', min=5)]),
                    html.Button("Generate Keywords", id="btn_kw", n_clicks=0),
                    html.Br(),
                    html.Button("Generate Keywords of All Texts", id="btn_allkw", n_clicks=0),
                    html.Br(),
                    html.Br(),
                    dcc.Loading(id="loading-4", children=[html.Div(id="kw_graph")], type="default"),
                    html.Br(),
                    dcc.Loading(id="loading-5", children=[html.Div(id="allkw_graph")], type="default"),
                    html.Br(),
                    html.Br(),

                    html.H2(children='Text Summarizer \U0001F4DD'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': str(i+1)} for i, t in enumerate(df["Translator/Publisher"])], 
                                placeholder="Select a text from the file",
                                id="text-selection4")]),
                    html.Label(["The Number of Sentences (minimum value is 2)", dcc.Input(id='sent-slider', type='number', min=2)]),
                    html.Button("Summarize", id="btn_tsum", n_clicks=0),
                    html.Br(),
                    html.Button("Summarize All Texts", id="btn_atsum", n_clicks=0),
                    html.Br(),
                    html.Br(),
                    dcc.Loading(id="loading-6", children=[html.Div(id="summary")], type="default"),
                    html.Br(),
                    dcc.Loading(id="loading-7", children=[html.Div(id="all_summary")], type="default"),
                    html.Br(),
                    html.Br(),

                    html.H2(children='Emotions Analysis \U0001F603'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': str(i+1)} for i, t in enumerate(df["Translator/Publisher"])], 
                                placeholder="Select a text from the file",
                                id="text-selection5")]),
                    html.Button("Analyze Emotions", id="btn_emo", n_clicks=0),
                    html.Br(),
                    html.Button("Analyze Emotions of All Texts", id="btn_emoa", n_clicks=0),
                    html.Br(),
                    html.Br(),
                    dcc.Loading(id="loading-8", children=[html.Div(id="emo-table")], type="default"),
                    html.Br(),
                    dcc.Loading(id="loading-9", children=[html.Div(id="emoa-table")], type="default"),
                    html.Br(),
                    html.Br(),

                    html.H2(children='Emotions Distribution Analysis \U0001F970'),
                    html.Label(["Text", dcc.Dropdown(options=[{'label': t, 'value': str(i+1)} for i, t in enumerate(df["Translator/Publisher"])], 
                                placeholder="Select a text from the file",
                                id="text-selection6")]),
                    html.Button("Draw Graph", id="btn_drawemo", n_clicks=0),
                    html.Br(),
                    html.Br(),
                    dcc.Loading(id="loading-10", children=[html.Div(id="emo-line-chart")], type="default"),
                    html.Br(),
                    html.Br(),
                ])]


@app.callback(Output('image_wc_upload', 'children'),
              Input('btn_wc', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection1', 'value'),
              Input('wordcloud-numws-slider', 'value'),
)
def make_image_wc(n_clicks, list_of_contents, list_of_names, list_of_dates, textid, num_ws):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            imgs = []
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]
            
            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts

            text = tokenize_r_stop_punc(nlp, df["Text"][int(textid)-1])
            img = io.BytesIO()
            plot_wordcloud(text, int(num_ws)).save(img, format='PNG')
            wc_img = 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
            return html.Div(children=[html.H5(html.B("\U0001F4D4 Word Cloud of "+df["Translator/Publisher"][int(textid)-1])),
                                      html.Img(src=wc_img),])
            

@app.callback(Output('image_wca_upload', 'children'),
              Input('btn_wca', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('wordcloud-numws-slider', 'value'),
)
def make_image_wc_all(n_clicks, list_of_contents, list_of_names, list_of_dates, num_ws):
    if n_clicks > 0:
        data = []
        df = [parse_contents_for_mining(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)][0]
        
        clean_texts = []
        for t in df["Text"]:
            t = re.sub("[　\n]", "", t)
            clean_texts.append(t)
            
        df["Text"] = clean_texts

        for i, t in enumerate(df["Text"]):
            data.append(html.H5(html.B("\U0001F4D4 Word Cloud of "+df["Translator/Publisher"][i])))
            text = tokenize_r_stop_punc(nlp, t)
            img = io.BytesIO()
            plot_wordcloud(text, int(num_ws)).save(img, format='PNG')
            wc_img = 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
            data.append(html.Img(src=wc_img))
            data.append(html.Br())
            data.append(html.Br())
        return data


@app.callback(Output('ner-labelling', 'children'),
              Input('btn_nerm', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection2', 'value'),
)
def make_ner_marks(n_clicks, list_of_contents, list_of_names, list_of_dates, textid):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]
            
            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts

            cc_ts = opencc.OpenCC('tw2s')
            text = df["Text"][int(textid)-1]
            text_ts = cc_ts.convert(text)
            doc = nlp(text_ts)
            children = render(doc)
            return children


@app.callback(Output('ner_graph', 'children'),
              Input('btn_nerd', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection2', 'value'),
)
def make_ner_distr(n_clicks, list_of_contents, list_of_names, list_of_dates, textid):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]
                
            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts

            cc_ts = opencc.OpenCC('tw2s')
            text = df["Text"][int(textid)-1]
            text_ts = cc_ts.convert(text)
            doc = nlp(text_ts)
            return dcc.Graph(figure={
                                'data': plot_ner_distr(doc),
                                'layout': {'title': 'NER Distribution of '+df["Translator/Publisher"][int(textid)-1],
                                            'xaxis': {'title': 'NER Category'},
                                            'yaxis': {'title': 'Count'}}
                                })


@app.callback(Output('all_ner_graph', 'children'),
              Input('btn_nerad', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
)
def make_all_ner_distr(n_clicks, list_of_contents, list_of_names, list_of_dates):
    if n_clicks > 0:
        df = [parse_contents_for_mining(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)][0]
        cc_ts = opencc.OpenCC('tw2s')

        clean_texts = []
        for t in df["Text"]:
            t = re.sub("[　\n]", "", t)
            clean_texts.append(t)
            
        df["Text"] = clean_texts

        datas = []
        for i, text in enumerate(df["Text"]):
            text_ts = cc_ts.convert(text)
            doc = nlp(text_ts)
            data = plot_ner_distr(doc)
            data[0]["name"] = df["Translator/Publisher"][i]
            datas.append(data[0])
        return dcc.Graph(figure={
                            'data': datas,
                            'layout': {'title': 'NER Distribution of All Texts',
                                        'xaxis': {'title': 'NER Category'},
                                        'yaxis': {'title': 'Count'}}
                            })


@app.callback(Output('kw_graph', 'children'),
              Input('btn_kw', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection3', 'value'),
              Input('kw-slider', 'value'),
)
def keywords_graph(n_clicks, list_of_contents, list_of_names, list_of_dates, textid, kwnum):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]

            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts
            text = df["Text"][int(textid)-1]
            data = keywords_extraction_single_text(text, int(kwnum))[0]

            return dcc.Graph(figure={
                                'data': [data],
                                'layout': {'title': 'Keywords of '+df["Translator/Publisher"][int(textid)-1],
                                            'xaxis': {'title': 'Weight'},
                                            'yaxis': {'title': 'Keywords'}}})


@app.callback(Output('allkw_graph', 'children'),
              Input('btn_allkw', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('kw-slider', 'value'),
)
def all_keywords_graph(n_clicks, list_of_contents, list_of_names, list_of_dates, kwnum):
    if n_clicks > 0:
        df = [parse_contents_for_mining(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)][0]

        clean_texts = []
        for t in df["Text"]:
            t = re.sub("[　\n]", "", t)
            clean_texts.append(t)
            
        df["Text"] = clean_texts
        data = keywords_extraction(df, int(kwnum))[0]

        return dcc.Graph(figure={
                            'data': [data],
                            'layout': {'title': 'Keywords of All Texts',
                                            'xaxis': {'title': 'Weight'},
                                            'yaxis': {'title': 'Keywords'}}})


@app.callback(Output('summary', 'children'),
              Input('btn_tsum', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection4', 'value'),
              Input('sent-slider', 'value'),
)
def text_summary(n_clicks, list_of_contents, list_of_names, list_of_dates, textid, sentnum):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]

            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts
            text = df["Text"][int(textid)-1]
            data = text_summarizer_single_text(text, int(sentnum))

            if len(data) == 0:
                return "The text is too short, please try summarizing all the texts."
            else:
                return html.Div(children=[html.H5(html.B("\U0001F4D4 Summary of "+df["Translator/Publisher"][int(textid)-1])),
                                          html.P(children=data),])


@app.callback(Output('all_summary', 'children'),
              Input('btn_atsum', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('sent-slider', 'value'),
)
def all_text_summary(n_clicks, list_of_contents, list_of_names, list_of_dates, sentnum):
    if n_clicks > 0:
        df = [parse_contents_for_mining(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)][0]

        clean_texts = []
        for t in df["Text"]:
            t = re.sub("[　\n]", "", t)
            clean_texts.append(t)
            
        df["Text"] = clean_texts
        data = text_summarizer(df, int(sentnum))

        return html.Div(children=[html.H5(html.B("\U0001F4D4 Summary of All Texts")),
                                          html.P(children=data),])


@app.callback(Output('emo-table', 'children'),
              Input('btn_emo', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection5', 'value'),
)
def emotion_analysis(n_clicks, list_of_contents, list_of_names, list_of_dates, textid):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]

            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts
            text = df["Text"][int(textid)-1]
            emotion_df = plot_emotion_distr(text, df["Translator/Publisher"][int(textid)-1], nlp)[0]
            emotion_df = emotion_df.iloc[0:len(emotion_df)-1, :]

            return dash_table.DataTable(columns=[{"name": i, "id": i} for i in emotion_df.columns],
                                        data=emotion_df.to_dict('records'), export_format='xlsx'
                                        )


@app.callback(Output('emoa-table', 'children'),
              Input('btn_emoa', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
)
def all_emotion_analysis(n_clicks, list_of_contents, list_of_names, list_of_dates):
    if n_clicks > 0:
        df = [parse_contents_for_mining(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)][0]

        clean_texts = []
        for t in df["Text"]:
            t = re.sub("[　\n]", "", t)
            clean_texts.append(t)
            
        df["Text"] = clean_texts

        all_em_df = pd.DataFrame(columns=["Translator/Publisher", "Emotion", "Words", "Counts", "Proportion"])
        for i, t in enumerate(df["Text"]):
            emo_df = plot_emotion_distr(t, fname=df["Translator/Publisher"][i], nlp=nlp)[0]
            all_em_df = pd.concat([all_em_df, emo_df], axis=0)
            all_em_df = all_em_df.iloc[0:len(all_em_df)-1, :]

        return dash_table.DataTable(columns=[{"name": i, "id": i} for i in all_em_df.columns],
                                    data=all_em_df.to_dict('records'), export_format='xlsx',
                                    )


@app.callback(Output('emo-line-chart', 'children'),
              Input('btn_drawemo', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('text-selection6', 'value'),
)
def draw_emotion_distri(n_clicks, list_of_contents, list_of_names, list_of_dates, textid):
    if n_clicks > 0:
        if textid is None:
            return "Please select a text."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]

            clean_texts = []
            for t in df["Text"]:
                t = re.sub("[　\n]", "", t)
                clean_texts.append(t)
                
            df["Text"] = clean_texts
            text = df["Text"][int(textid)-1]
            emotion_distri_df = plot_emotion_distr(text, "Text "+str(textid), nlp)[1]
            emotion_distri_df2 = emotion_distri_df

            for i, ea in enumerate(emotion_distri_df["Emotion_Appearance"]):
                if ea == 0:
                    emotion_distri_df2 = emotion_distri_df2.drop(i)

            emotion_distri_df2 = emotion_distri_df2.reset_index(drop=True)

            for ei, e in enumerate(emotion_distri_df2["Emotion"]):
                if e == "Preference" or e == "Happiness":
                    emotion_distri_df2["Emotion_Appearance"][ei] = 1
                elif e == "Surprise":
                    emotion_distri_df2["Emotion_Appearance"][ei] = 0
                elif e == "Sadness" or e == "Anger" or e == "Fear" or e == "Hate":
                    emotion_distri_df2["Emotion_Appearance"][ei] = -1

            groups = emotion_distri_df2.groupby(by='Emotion')
            data = []
            colors=['red', 'black', 'yellow', 'grey', 'pink', 'blue', 'green']

            data.append(go.Scatter(x=list(emotion_distri_df2["Word_Position"]), 
                                    y=list(emotion_distri_df2["Emotion_Appearance"]), 
                                    mode = 'lines', 
                                    name='Trends in Emotions', 
                                    line_color="#B4A582", line_shape='spline'))

            for group, dataframe in groups:
                if group == "Preference":
                    colour = "#E87A90"
                elif group == "Happiness":
                    colour = "#FFC408"
                elif group == "Sadness":
                    colour = "#2EA9DF"
                elif group == "Anger":
                    colour = "#9F353A"
                elif group == "Fear":
                    colour = "#08192D"
                elif group == "Hate":
                    colour = "#8A6BBE"
                elif group == "Surprise":
                    colour = "#F75C2F"

                trace = go.Scatter(x=dataframe.Word_Position.tolist(), 
                                y=dataframe.Emotion_Appearance.tolist(),
                                mode='markers',
                                marker=dict(color=colour, size=15),
                                name=group)
                data.append(trace)

            layout =  go.Layout(title= 'Emotions Distribution of '+df["Translator/Publisher"][int(textid)-1],
                                xaxis={'title': 'The Position of the Appearance of Emotional Words in the Text'},
                                yaxis={'title': 'Emotion Appearance'},
                                margin={'l': 40, 'b': 40, 't': 50, 'r': 50},
                                hovermode='closest')

            figure = go.Figure(data=data, layout=layout)

            emotion_words_df = plot_emotion_distr(text, "Text "+str(textid), nlp)[0]
            emotion_words_df = emotion_words_df.iloc[0:len(emotion_words_df)-1, :]

            text_split = text
            for j, ws in enumerate(emotion_words_df["Words"]):
                queries = ws.split(",")
                if queries  == ['']:
                    pass
                else:
                    for q in queries:
                        if type(text_split) != list:
                            text_split = text.split(q)

                            if emotion_words_df['Emotion'][j] == "Preference":
                                colour = "#E87A90"
                            elif emotion_words_df['Emotion'][j] == "Happiness":
                                colour = "#FFC408"
                            elif emotion_words_df['Emotion'][j] == "Sadness":
                                colour = "#2EA9DF"
                            elif emotion_words_df['Emotion'][j] == "Anger":
                                colour = "#DB4D6D"
                            elif emotion_words_df['Emotion'][j] == "Fear":
                                colour = "#787D7B"
                            elif emotion_words_df['Emotion'][j] == "Hate":
                                colour = "#B481BB"
                            elif emotion_words_df['Emotion'][j] == "Surprise":
                                colour = "#F75C2F"
                            text_split.insert(1, html.Mark(q, style={"background": colour,"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}))
                        else:
                            for tsi, ts in enumerate(text_split):
                                if type(ts) == str:
                                    if re.search(q, ts):
                                        if emotion_words_df['Emotion'][j] == "Preference":
                                            colour = "#E87A90"
                                        elif emotion_words_df['Emotion'][j] == "Happiness":
                                            colour = "#FFC408"
                                        elif emotion_words_df['Emotion'][j] == "Sadness":
                                            colour = "#2EA9DF"
                                        elif emotion_words_df['Emotion'][j] == "Anger":
                                            colour = "#DB4D6D"
                                        elif emotion_words_df['Emotion'][j] == "Fear":
                                            colour = "#787D7B"
                                        elif emotion_words_df['Emotion'][j] == "Hate":
                                            colour = "#B481BB"
                                        elif emotion_words_df['Emotion'][j] == "Surprise":
                                            colour = "#F75C2F"
                                        
                                        ts = ts.split(q)
                                        ts.insert(1, html.Mark(q, style={"background": colour,"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}))

                                        text_split.remove(text_split[tsi])
                                        for i, tt in enumerate(ts):
                                            text_split.insert(tsi+i, tt)

            return html.Div([dcc.Graph(figure={
                                                'data': data,
                                                'layout': layout,
                                                }),
                            html.Br(),
                            html.Br(),
                            html.P(text_split),
                            html.Br(),
                            html.Br(),])


@app.callback(Output('lda_file', 'children'),
              Input('btn_lda', 'n_clicks'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified'),
              Input('lda-slider', 'value'),
              Input('input1', 'value'),
              Input('text-selection7', 'value'),
              Input('topic_ws', 'value')
)
def download_lda(n_clicks, list_of_contents, list_of_names, list_of_dates, topicnum, fname, target, num_ws):
    if n_clicks > 0:
        if fname is None:
            return "Please enter a file name."
        elif num_ws is None:
            return "Please specify a number of words."
        else:
            df = [parse_contents_for_mining(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)][0]

            if target == "All":
                clean_texts = []
                for t in df["Text"]:
                    t = re.sub("[　\n]", "", t)
                    clean_texts.append(t)
                    
                df["Text"] = clean_texts
                
                lda_df = plot_lda(df, topicnum, nlp, fname, num_ws)
            else:
                for i, tp in enumerate(df["Translator/Publisher"]):
                    if tp == target:
                        t = re.sub("[　\n]", "", df["Text"][i])
                        lda_df = plot_lda_single(t, topicnum, nlp, fname, num_ws)

            return [html.Div(children=[html.Mark("Done!", style={"background": "#FAD689","padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}),
                                       html.Br(),
                                       html.Br(),
                                       dash_table.DataTable(columns=[{"name": i, "id": i} for i in lda_df.columns],
                                                            data=lda_df.to_dict('records'), export_format='xlsx',
                                                            )
                                    #    html.H5("Predict which topics your text belongs to."),
                                    #    dcc.Textarea(
                                    #                 id='user_text',
                                    #                 style={'width': '100%', 'height': 30},
                                    #                 ),
                                    #     html.P("Model name"),
                                    #     dcc.Input(id="model_name", type="text", placeholder="topic_modeling_4topics"),
                                    #     html.Button("Predict", id="btn_pred_topics", n_clicks=0),
                                    #     html.Br(),
                                    #     html.Br(),
                                    #     dcc.Loading(id="loading-12", children=[html.Div(id="topics_pred_results")], type="default"),
                                    #     html.Br(),
                                    #     html.Br(),
                                    ])]


# @app.callback(Output('topics_pred_results', 'children'),
#               Input('btn_pred_topics', 'n_clicks'),
#               Input('user_text', 'value'),
#               Input('lda-slider', 'value'),
#               Input('num_words', 'value'),
#               Input('upload-data', 'contents'),
#               Input('upload-data', 'filename'),
#               Input('upload-data', 'last_modified'),
#               Input('model_name', 'value'),
# )
# def predict_user_topics(n_clicks, text, num_topics, num_words, list_of_contents, list_of_names, list_of_dates, model_name):
#     if n_clicks > 0:
#         df = [parse_contents_for_mining(c, n, d) for c, n, d in
#                 zip(list_of_contents, list_of_names, list_of_dates)][0]

#         clean_texts = []
#         for t in df["Text"]:
#             t = re.sub("[　\n]", "", t)
#             clean_texts.append(t)
            
#         df["Text"] = clean_texts
#         print(model_name)

#         pred_df = predict_topics(df, nlp, text, num_topics, num_words, model_name)

#         return dash_table.DataTable(columns=[{"name": i, "id": i} for i in pred_df.columns],
#                                     data=pred_df.to_dict('records'), export_format='xlsx',
#                                     )

if __name__ == '__main__':
    app.run_server(debug=False,port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')