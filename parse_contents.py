import base64
import io
import pandas as pd
import dash_html_components as html
import dash_table

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xlsx' in filename or 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
                html.H5(filename),
                # html.H6(datetime.datetime.fromtimestamp(date)),

                dash_table.DataTable(
                    style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    data=df.head().to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],

                    ## 限制內容不完全展開
                    css=[{
                        'selector': '.dash-spreadsheet td div',
                        'rule': '''
                            line-height: 15px;
                            max-height: 30px; min-height: 30px; height: 30px;
                            display: block;
                            overflow-y: hidden;
                        '''
                        }],
                ),
            ])

def parse_contents_for_mining(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    
    return df