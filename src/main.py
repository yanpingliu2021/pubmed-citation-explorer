
import pubmed_parser as pp
import pandas as pd
import os
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spacy
# Load science tokenizer
nlp = spacy.load("en_core_sci_sm")
import glob
files = sorted(glob.glob('../data/raw/*.xml.gz'))

for f in files:
    print(f"parse file {f.split('/')[-1]}")
    parsed_articles = pp.parse_medline_xml(f,
                                        year_info_only=True,
                                        nlm_category=True,
                                        author_list=False)
    df = pd.DataFrame.from_dict(parsed_articles)\
        .filter(items=['title', 'abstract', 'journal', 'authors', 'pubdate', 'mesh_terms',
                       'publication_types', 'chemical_list', 'keywords', 'country'])
    df = df[df['publication_types'].str.lower().str.contains("journal article")].reset_index(drop=True)
    for yr in sorted(df['pubdate'].unique().tolist()):
        yr_df = df.loc[df['pubdate'] == yr].reset_index(drop=True)
        f_path = f'../data/processed/pubmed_baseline_{yr}.parquet'
        if os.path.exists(f_path):
            tmp_df = pd.read_parquet(f_path)
            yr_df.append(tmp_df).drop_duplicates().reset_index(drop=True).to_parquet(f_path, index=False)
            print(yr_df.shape)
        else:
            yr_df.to_parquet(f_path, index=False)
            print(yr_df.shape)


df.head(5)
df = df.loc[df['pubdate'] != '1979'].reset_index(drop=True)
df.shape
df.head()
df.pubdate.value_counts()
df.abstract.str.strip().astype(bool).sum()
df.title.str.strip().astype(bool).sum()
df.columns
df.dtypes


df = df.loc[df['pubdate'] != '1979'].reset_index(drop=True)
vis_cols = ['title', 'abstract', 'mesh_terms', 'chemical_list', 'keywords']

for col in ['chemical_list']:
    text_df = df\
        .groupby('pubdate')\
        .agg(text = (col, ' '.join))
    # text_df.to_json('../data/title.json')

    # Process whole documents
    for year, row in text_df.iterrows():
        print(year)
        text = row['text']
        doc = nlp(text)

        # # Analyze syntax
        # print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
        # print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

        # Find named entities, phrases and concepts
        # for entity in doc.ents:
        #     print(entity.text, entity.label_)

        # custom_tokens = [token.text for token in doc]
        # # Word Info
        # custom_wordinfo = [(token.text,token.lemma_,token.shape_,token.is_alpha,token.is_stop) for token in doc]
        # custom_postagging = [(word.text,word.tag_,word.pos_,word.dep_) for word in doc]

        # https://www.machinelearningplus.com/spacy-tutorial-nlp/
        # doc_cleaned = [token.lemma_ for token in doc if not token.is_stop
        #             and not token.is_punct and token.is_alpha]
        # doc_cleaned = [token.lemma_ for token in doc if not token.is_stop
        #             and not token.is_punct]

        # doc_cleaned = [word.lower() for word in doc_cleaned if len(word) > 4]

        entities = [x.text for x in doc.ents if not any(map(str.isdigit, x.text))]

        # https://www.datacamp.com/community/tutorials/wordcloud-python
        # Create and generate a word cloud image:
        # wordcloud = WordCloud().generate(' '.join(doc_cleaned))

        stopwords = set(STOPWORDS)
        # stopwords.update(["author", "transl", "study"])

        # lower max_font_size, change the maximum number of word and lighten the background:
        # wordcloud = WordCloud(stopwords=stopwords, max_font_size=50, max_words=100, background_color="white").generate(' '.join(doc_cleaned))
        wordcloud = WordCloud(stopwords=stopwords, max_font_size=50, max_words=100, background_color="white").generate(' '.join(entities))
        # plt.figure()
        # plt.imshow(wordcloud, interpolation="bilinear")
        # plt.axis("off")
        # plt.show()

        wordcloud.to_file(f"../flask_app/static/images/{col}_{year}.png")