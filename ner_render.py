import spacy
from spacy.displacy.render import DEFAULT_LABEL_COLORS
import dash
import dash_html_components as html
import opencc

cc_st = opencc.OpenCC('s2tw')

def entname(name):
    return html.Span(name, style={
        "font-size": "0.8em",
        "font-weight": "bold",
        "line-height": "2",
        "border-radius": "0.35em",
        "text-transform": "uppercase",
        "vertical-align": "middle",
        "margin-left": "0.5rem"
    })


def entbox(children, color):
    return html.Mark(children, style={
        "background": color,
        "padding": "0.35em 0.6em",
        "margin": "0 0.25em",
        "line-height": "2",
        "border-radius": "0.35em",
    })


def entity(children, name):
    if type(children) is str:
        children = [children]

    children.append(entname(cc_st.convert(name)))
    if name == "FAC":
        name = "FACILITY"
    color = DEFAULT_LABEL_COLORS[name]
    return entbox(children, color)


def render(doc):
    children = []
    last_idx = 0
    for ent in doc.ents:
        children.append(cc_st.convert(doc.text[last_idx:ent.start_char]))
        children.append(
            entity(cc_st.convert(doc.text[ent.start_char:ent.end_char]), ent.label_))
        last_idx = ent.end_char
    children.append(cc_st.convert(doc.text[last_idx:]))
    return children

def plot_ner_distr(doc):
    ners = []
    for ent in doc.ents:
        ners.append(ent.label_)

    unique_ner = list(set(ners))
    counts = []

    for un in unique_ner:
        counts.append(ners.count(un))

    data = [{'x': unique_ner, 'y': counts, 'type': 'bar'}]
    
    return data