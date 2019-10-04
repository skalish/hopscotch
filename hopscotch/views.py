from flask import render_template
from flask import request
from hopscotch import app
from hopscotch.Rec_Model import ApplyModel
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

# Connect to Postgres scotch database
user = 'skalish'
host = 'localhost'
dbname = 'scotch_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user, host = host, password = 'password')

@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Visitor' }
       )

# Page displaying all scotches in database
@app.route('/db_fancy')
def scotch_page_fancy():
    sql_query = """
                SELECT * FROM scotch_data_table_clean;
                """
    query_results=pd.read_sql_query(sql_query,con)
    query_results=query_results.sort_values(by='name')
    scotches = []
    for i in range(0,query_results.shape[0]):
        scotches.append(dict(name=query_results.iloc[i]['name'],
                           region=query_results.iloc[i]['Region']))
    return render_template('scotches.html', scotches=scotches)

# Input page for users to provide liked and disliked scotches and price range
@app.route('/')
@app.route('/input')
def scotch_input():
    # Get all scotches from database
    query = "SELECT name FROM scotch_data_table_clean"
    query_results = pd.read_sql_query(query,con)

    # Create list of scotch names for user selection
    scotch_list = []
    for i in range(0,query_results.shape[0]):
        scotch_list.append(query_results.iloc[i]['name'])

    return render_template("input.html",
                           scotch_list = sorted(scotch_list))

# Output page providing scotch recommendations based on user input
@app.route('/output')
def scotch_output():
    # Get 'liked' and 'disliked' scotch names from input fields and store them
    good_products = request.args.getlist('likes')
    bad_products = request.args.getlist('dislikes')

    # Get price range from input fields
    low_price = request.args.get('low_price')
    high_price = request.args.get('high_price')
    
    # Create dataframe from scotch database
    rec_query = "SELECT * FROM scotch_data_table_clean"
    rec_df=pd.read_sql_query(rec_query,con)

    # Apply model returning dataframe sorted by recommendation score
    scored_df = ApplyModel(rec_df, good_products, bad_products)

    # Filter by user price range. If conversion to float fails, ignore
    try:
        scored_df = scored_df[scored_df.price_usd >= float(low_price)]
    except:
        pass
    try:
        scored_df = scored_df[scored_df.price_usd <= float(high_price)]
    except:
        pass
    
    # Recommend scotches only from 1000 most popular products (optional)
    # scored_df = scored_df[scored_df.index < 1000]

    # Create list of top 10 recommended scotches to pass to output
    scotches = []
    for i in range(min(10, scored_df.shape[0])):
        scotches.append(dict(index=scored_df.iloc[i]['index'],
                             name=scored_df.iloc[i]['name'],
                             price=scored_df.iloc[i]['price_usd'],
                             region=scored_df.iloc[i]['Region'],
                             score=scored_df.iloc[i]['score'],
                             nose=scored_df.iloc[i]['Nose_common'],
                             palate=scored_df.iloc[i]['Palate_common'],
                             finish=scored_df.iloc[i]['Finish_common']))
    
    return render_template("output.html",
                           scotch_list = scotch_list,
                           scotches = scotches)
