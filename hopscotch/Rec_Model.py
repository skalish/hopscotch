import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')

def length_filter(t):
    return [s for s in t if len(s) > 2]

# Count vectorizer function
def cv(data):
    count_vectorizer = CountVectorizer()

    emb = count_vectorizer.fit_transform(data)

    return emb, count_vectorizer

# Generate cosine similarity matrix
def gen_cos_sim(df):
    # Vectorize nose notes
    counts, counts_vectorizer = cv(df["Nose"].tolist())

    # Vectorize palate notes and catenate to current array
    counts2, counts_vectorizer = cv(df["Palate"].tolist())
    counts = hstack((counts, counts2))

    # Vectorize finish notes and catenate to current array
    counts2, counts_vectorizer = cv(df["Finish"].tolist())
    counts = hstack((counts, counts2))

    # OPTIONAL: Catenate region information, weight relative to individual words
    region_weight = 2
    region_array = df[['reg_0', 'reg_1', 'reg_2', 'reg_3', 'reg_4', 'reg_5', 'reg_6', 'reg_7']].values
    counts = hstack((counts, region_weight * region_array))
    
    # Return cosine similarity matrix
    return cosine_similarity(counts)

def ApplyModel(rec_df, liked_list = [], disliked_list = []):
    # Generate tokenized note descriptions
    rec_df['Nose_tokens'] = rec_df['Nose_clean'].apply(tokenizer.tokenize).apply(length_filter)
    rec_df['Palate_tokens'] = rec_df['Palate_clean'].apply(tokenizer.tokenize).apply(length_filter)
    rec_df['Finish_tokens'] = rec_df['Finish_clean'].apply(tokenizer.tokenize).apply(length_filter)


    # Initialize lists of liked and disliked notes
    nose_liked_notes = []
    nose_disliked_notes = []
    palate_liked_notes = []
    palate_disliked_notes = []
    finish_liked_notes = []
    finish_disliked_notes = []
    
    # Set user_pref column values from lists supplied by user
    rec_df['user_pref'] = np.zeros(rec_df.shape[0])
    for name in liked_list:
        rec_df.loc[rec_df['name'] == name, 'user_pref'] = 1
        nose_liked_notes.extend(rec_df.loc[rec_df['name'] == name, 'Nose_tokens'].values[0])
        palate_liked_notes.extend(rec_df.loc[rec_df['name'] == name, 'Palate_tokens'].values[0])
        finish_liked_notes.extend(rec_df.loc[rec_df['name'] == name, 'Finish_tokens'].values[0])
    for name in disliked_list:
        rec_df.loc[rec_df['name'] == name, 'user_pref'] = -1
        nose_disliked_notes.extend(rec_df.loc[rec_df['name'] == name, 'Nose_tokens'].values[0])
        palate_disliked_notes.extend(rec_df.loc[rec_df['name'] == name, 'Palate_tokens'].values[0])
        finish_disliked_notes.extend(rec_df.loc[rec_df['name'] == name, 'Finish_tokens'].values[0])

    nose_liked_notes = set(nose_liked_notes) - set(nose_disliked_notes)
    
    palate_liked_notes = set(palate_liked_notes) - set(palate_disliked_notes)
    
    finish_liked_notes = set(finish_liked_notes) - set(finish_disliked_notes)
    
    
    # Generate cosine similarity matrix
    cos_sim = gen_cos_sim(rec_df)
    
    # Calculate scores and store in rec_df
    rec_df['score'] = list(np.array(rec_df['user_pref']).dot(cos_sim))
    #rec_df['Nose_common'] = rec_df['Nose_tokens'].apply(type)
    rec_df['Nose_common'] = rec_df['Nose_tokens'].apply(set).apply(nose_liked_notes.intersection).apply(list).apply(', '.join)
    rec_df['Palate_common'] = rec_df['Palate_tokens'].apply(set).apply(nose_liked_notes.intersection).apply(list).apply(', '.join)
    rec_df['Finish_common'] = rec_df['Finish_tokens'].apply(set).apply(nose_liked_notes.intersection).apply(list).apply(', '.join)
    
    # Sort by score and exclude items that have already been rated
    result = rec_df[rec_df['user_pref'] == 0].sort_values(by='score', ascending = False)
    
    return result
