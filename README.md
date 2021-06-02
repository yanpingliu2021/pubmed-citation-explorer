
![Python application](https://github.com/yanpingliu2021/pubmed-citation-explorer/actions/workflows/python-app.yml/badge.svg)](<https://github.com/yanpingliu2021/pubmed-citation-explorer/actions/workflows/python-app.yml>)

# NU MSDS498 Capstone Individual Project

Explore Medline Biomedical Journal Article Topics Using Word Cloud

A simple Flask Web App to visualize the Biomedical Journal Article contents (Title, Keywords, Abstract, Chemical Studied) by year with the intention to see the trend of the research topics over the last ten years in United States.

## Data Source

The Data used is the [MEDLINE](<https://www.nlm.nih.gov/medline/medline_overview.html>) database, the National Library of Medicine’s (NLM) premier bibliographic database that contains more than 27 million references to journal articles in life sciences with a concentration on biomedicine. The data are hosted in [PubMed](<https://pubmed.ncbi.nlm.nih.gov/>) in XML formats and are free to download via FTP through link: <https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/>

The data contains articles back to 1960s across the world, but only the articles from United States and published during the last ten years were visualized.

## Web Interface Screenshot

![alt text](https://github.com/yanpingliu2021/pubmed-citation-explorer/blob/master/app-interface.png?raw=true)

## How to build from scratch

To deploy this Flask app on Google Cloud Platform, you can follow these steps:

### Set up project

Run git clone [git@github.com:yanpingliu2021/pubmed-citation-explorer.git](https://github.com/yanpingliu2021/pubmed-citation-explorer.git) in your desired directory
Install [peotry](https://python-poetry.org/docs/#installation)  npm install -i to install the dependencies
Run npm start to initiate the server listening at <http://localhost:8080/>
Launch Google Cloud Platform, create a new project. Change your current project to it and activate Cloud Shell.
Git clone this repository to your GCP local and cd into it.

Run this app locally
Create a virtual environment and activate it. (To deactivate it, run deactivate).

make set-up
source ~/.covid_venv/bin/activate
Install the required packages.

make install
Run this app, the flask app will be running on <http://127.0.0.1:8080/>.

python3 main.py
You can test it from the frontend website or send a POST request to the running app through a script.

bash predict-local.sh
Deploy this app on GCP
(optional) Verfiy the current project is working. Switch your project if it's not what you want.

gcloud projects describe $GOOGLE_CLOUD_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT
Create app engine in GCP.

gcloud app create
When it asks you to choose a region, select one(in my case is 14 us-central). Type "yes" when it asks you to continue.
Deploy this app on cloud, the app will be running on the provided public url.

gcloud app deploy
You can test it from the frontend website or send a POST request to the running app through a script. Remember to change the website address in predict.sh.

bash predict.sh
Load Test with locust
Run following command, the locust server will be running on <http://0.0.0.0:8089/>.

locust
Go to the webpage, fill out the form and try to test it.

Done!

## Helper

Community fitness functions: <https://cdlib.readthedocs.io/en/latest/reference/evaluation.html></br>
Doctor performance metrics: <https://www.cms.gov/medicare/quality-initiatives-patient-assessment-instruments/compare-dac>

## Reference

<http://wayback.archive-it.org/org-350/20180312141554/https://www.nlm.nih.gov/pubs/factsheets/medline.html>
<https://en.wikipedia.org/wiki/MEDLINE>
<https://en.wikipedia.org/wiki/PubMed>
<https://github.com/titipata/pubmed_parser/wiki>
<https://github.com/titipata/pubmed_parser/wiki/Download-and-preprocess-MEDLINE-dataset>
<https://github.com/titipata/pubmed_parser/wiki/Download-and-preprocess-Pubmed-Open-Access-dataset>
<https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/>
<https://www.youtube.com/watch?v=LP04X795Pt4>

deploy to aws elastic beanstalk
<https://realpython.com/deploying-a-django-app-and-postgresql-to-aws-elastic-beanstalk/>
