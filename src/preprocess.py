"""
data preprocess for word cloud
"""
import pandas as pd
import psycopg2
import os
import pandas.io.sql as sqlio
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import nltk
# nltk.download('words')
# nltk.download('wordnet')
words = set(nltk.corpus.words.words())
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from utils import load_config, copy_from_stringio

# load database configs
database_name, table_name, user, password, host, port = load_config()

# connect to AWS RDS postgresSQL
connection = psycopg2.connect(user=user,
                            password=password,
                            host = host,
                            port = port,
                            database=database_name)
connection.autocommit = True
# cursor = connection.cursor()

# cursor.execute(f"Select count(*) FROM {table_name}")
# print(f"table records: {cursor.fetchall()[0][0]}")

# cursor.execute(f"DELETE FROM {table_name} WHERE pubdate > 2020")
# connection.commit()
# cursor.execute(f"select pubdate from {table_name} group by pubdate;")
# cursor.fetchall()
# cursor.close()

year_df = sqlio.read_sql_query(
    f"select pubdate from {table_name} group by pubdate;",
    connection)
year_list = year_df['pubdate'].tolist()
viz_cols = ['title', 'abstract', 'chemical_list', 'keywords']

for col in ['title', 'abstract']:
    sql = f"select pubdate, {col} from {table_name} where {col} is not null;"
    df = sqlio.read_sql_query(sql, connection)
    df = df[df[col] !=''].reset_index(drop=True)

    for year in sorted(df['pubdate'].unique().tolist()):
        print(year)
        df.loc[df['pubdate']==year, col] = df.loc[df['pubdate']==year, col]\
            .apply(lambda txt:' '.join(
                    [lemmatizer.lemmatize(x) for x in nltk.wordpunct_tokenize(txt) if x.lower() in words]))
    df.shape
    tfidf = TfidfVectorizer(ngram_range=(1,1), max_df=0.25)
    tfidf_matrix = tfidf.fit_transform(df[col])
    keep_words = set(tfidf.get_feature_names())
    len(keep_words)
    text_df = df\
        .groupby('pubdate')\
        .agg(text = (col, ' '.join))

    text_df['text'] = text_df['text']\
        .apply(lambda txt:' '.join(
                [x for x in txt.split() if x in keep_words]))
    # text_df['text'].apply(len)

    vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,1))
    count_matrix = vectorizer.fit_transform(text_df['text'])
    count_matrix.shape
    count_matrix_df = pd.DataFrame(count_matrix.toarray(),
                                   columns=vectorizer.get_feature_names(),
                                   index=text_df.index)
    count_matrix_df = count_matrix_df.sort_index().T.reset_index()
    freq_matrix_df = count_matrix_df.copy()
    freq_matrix_df.iloc[:, 1:] = count_matrix_df.iloc[:, 1:]/df.groupby('pubdate').size()
    # freq_matrix_df.columns
    # freq_matrix_df.sort_values(by=2011, ascending=False)

    lower_idx = (freq_matrix_df.iloc[:, 1:]>=0.00005).any(axis=1)
    upper_idx = (freq_matrix_df.iloc[:, 1:]<=0.02).any(axis=1)
    count_matrix_df.name = None
    count_matrix_df.columns = ['word'] + [f'Y_{x}' for x in count_matrix_df.columns[1:]]
    count_matrix_df = count_matrix_df[lower_idx & upper_idx].reset_index(drop=True)
    print(f'total words: {count_matrix_df.shape}')
    # count_matrix_df.sort_values(by='Y_2011', ascending=False)


    # SQL query to create a new table
    cursor = connection.cursor()
    cursor.execute(f"drop table if exists pubmed_{col}")
    connection.commit()
    create_table_query = f'''CREATE TABLE pubmed_{col}
        (word TEXT,
        Y_2011 INT,
        Y_2012 INT,
        Y_2013 INT,
        Y_2014 INT,
        Y_2015 INT,
        Y_2016 INT,
        Y_2017 INT,
        Y_2018 INT,
        Y_2019 INT,
        Y_2020 INT
        ); '''
    # Execute a command: this creates a new table
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    cursor.execute(f"Select count(*) FROM pubmed_{col}")
    before_n = cursor.fetchall()[0][0]
    print(f"table records before upload: {before_n}")
    copy_from_stringio(connection,count_matrix_df,f"pubmed_{col}")
    cursor.execute(f"Select count(*) FROM pubmed_{col}")
    after_n = cursor.fetchall()[0][0]
    print(f"table records after upload: {after_n}")
    cursor.close()




for col in ['chemical_list', 'keywords']:
    sql = f"select pubdate, {col} from {table_name} where {col} is not null;"
    df = sqlio.read_sql_query(sql, connection)
    df = df[df[col] !=''].reset_index(drop=True)
    df.shape

    if col == 'chemical_list':
        sep = ';'
    else:
        sep = ' '
    text_df = df\
        .groupby('pubdate')\
        .agg(text = (col, sep.join))

    # text_df['text'].apply(len)
    if col == 'chemical_list':
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,1), tokenizer=lambda x: x.split(';'))
    else:
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,1))

    count_matrix = vectorizer.fit_transform(text_df['text'])
    count_matrix.shape
    count_matrix_df = pd.DataFrame(count_matrix.toarray(),
                                   columns=vectorizer.get_feature_names(),
                                   index=text_df.index)
    count_matrix_df = count_matrix_df.sort_index().T.reset_index()
    count_matrix_df['index'] = vectorizer.get_feature_names()
    freq_matrix_df = count_matrix_df.copy()
    freq_matrix_df.iloc[:, 1:] = count_matrix_df.iloc[:, 1:]/df.groupby('pubdate').size()
    # freq_matrix_df.columns
    # freq_matrix_df.sort_values(by=2011, ascending=False)

    lower_idx = (freq_matrix_df.iloc[:, 1:]>=0.00005).any(axis=1)
    upper_idx = (freq_matrix_df.iloc[:, 1:]<=0.02).any(axis=1)
    count_matrix_df.name = None
    count_matrix_df.columns = ['word'] + [f'Y_{x}' for x in count_matrix_df.columns[1:]]
    count_matrix_df = count_matrix_df[lower_idx & upper_idx].reset_index(drop=True)
    print(f'total words: {count_matrix_df.shape}')
    # count_matrix_df.sort_values(by='Y_2011', ascending=False)


    # SQL query to create a new table
    cursor = connection.cursor()
    cursor.execute(f"drop table if exists pubmed_{col}")
    connection.commit()
    create_table_query = f'''CREATE TABLE pubmed_{col}
        (word TEXT,
        Y_2011 INT,
        Y_2012 INT,
        Y_2013 INT,
        Y_2014 INT,
        Y_2015 INT,
        Y_2016 INT,
        Y_2017 INT,
        Y_2018 INT,
        Y_2019 INT,
        Y_2020 INT
        ); '''
    # Execute a command: this creates a new table
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    cursor.execute(f"Select count(*) FROM pubmed_{col}")
    before_n = cursor.fetchall()[0][0]
    print(f"table records before upload: {before_n}")
    copy_from_stringio(connection,count_matrix_df,f"pubmed_{col}")
    cursor.execute(f"Select count(*) FROM pubmed_{col}")
    after_n = cursor.fetchall()[0][0]
    print(f"table records after upload: {after_n}")
    cursor.close()

def wordcloud(freq_df):
    # count_matrix_df.to_excel('../data/count_matrix.xlsx')
    tuples = [tuple(x) for x in freq_df.values]
    stopwords = set(STOPWORDS)
    # stopwords.update(["author", "transl", "study"])

    wordcloud = WordCloud(stopwords=stopwords,
                          max_font_size=40, max_words=5000,
                          background_color="white")\
                .generate_from_frequencies(dict(tuples))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
