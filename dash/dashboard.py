import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from sqlalchemy import create_engine, Column, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Define your SQLAlchemy model
class SecurityWiseHoldings(Base):
    __tablename__ = 'SecurityWiseHoldings'

    isin = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    indicative_value = Column(Float)

# Your database connection string
DATABASE_CONNECTION_STRING = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:ccildindia-scraping-server.database.windows.net,1433;Database=SecurityWiseHoldings;Uid=sqladmin;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

app = dash.Dash(__name__)

# Layout with dropdown and graph
app.layout = html.Div([
    dcc.Dropdown(
        id='isin-dropdown',
        value=None
    ),
    dcc.Graph(id='indicator-graph'),
])

# Callback to populate dropdown options
@app.callback(
    Output('isin-dropdown', 'options'),
    [Input('isin-dropdown', 'value')]
)
def update_dropdown(selected_isin):
    # Create engine and session
    engine = create_engine(DATABASE_CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Execute the query to get unique isin values
    unique_isin = session.query(SecurityWiseHoldings.isin).distinct().all()

    # Close the session
    session.close()

    # Return unique isin values
    return [{'label': isin[0], 'value': isin[0]} for isin in unique_isin]

# Define callback to update the graph based on selected ISIN
@app.callback(
    Output('indicator-graph', 'figure'),
    [Input('isin-dropdown', 'value')]
)
def update_graph(selected_isin):
    if selected_isin:
        # Create engine and session
        engine = create_engine(DATABASE_CONNECTION_STRING)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Fetch rows for the selected ISIN ordered by date (latest to earliest)
        rows = session.query(SecurityWiseHoldings.date, SecurityWiseHoldings.indicative_value).\
            filter(SecurityWiseHoldings.isin == selected_isin).order_by(SecurityWiseHoldings.date.desc()).all()

        # Close the session
        session.close()

        # Create a plot using Plotly Express
        if rows:
            import plotly.express as px
            import pandas as pd
            df = pd.DataFrame(rows, columns=['date', 'indicative_value'])
            fig = px.line(df, x='date', y='indicative_value', title=f'Indicative Value for {selected_isin}')
            return fig

    # Return an empty graph if no data is available or no ISIN selected
    return px.line(title='Indicative Value')

if __name__ == '__main__':
    app.run_server(debug=True)
