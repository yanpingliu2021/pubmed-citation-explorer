
![Python application](https://github.com/yanpingliu2021/pubmed-citation-explorer/actions/workflows/python-app.yml/badge.svg)](<https://github.com/yanpingliu2021/pubmed-citation-explorer/actions/workflows/python-app.yml>)

# NU MSDS498 Capstone Individual Project

Explore Medline Biomedical Journal Article Topics Using Word Cloud

A simple Flask Web App to visualize the Biomedical Journal Article contents (Title, Keywords, Abstract, Chemical Studied) by year with the intention to see the trend of the research topics over the last ten years in United States.
</br>

## Data Source

The Data used is the [MEDLINE](<https://www.nlm.nih.gov/medline/medline_overview.html>) database, the National Library of Medicine’s (NLM) premier bibliographic database that contains more than 27 million references to journal articles in life sciences with a concentration on biomedicine. The data are hosted in [PubMed](<https://pubmed.ncbi.nlm.nih.gov/>) in XML formats and are free to download via FTP through link: <https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/>

The data contains articles back to 1960s across the world, but only the articles from United States and published during the last ten years were visualized.
</br>

## Web Interface Screenshot

![alt text](https://github.com/yanpingliu2021/pubmed-citation-explorer/blob/master/app-interface.PNG?raw=true)
</br>

## Tool Landscape

1. Testing Framework
   * pytest
2. App Deployment
   * AWS Elastic Beanstalk
3. Editor
   * VS Code
4. Web Framework
   * Flask
5. CI/CD
   * Github Actions
6. Database
   * AWS RDS PostgreSQL
7. Storage
   * AWS S3
</br>

## How to build from scratch

To deploy this Flask app on AWS Elastic Beanstalk Platform, you can follow these steps:

### Set up project

Run ```git clone https://github.com/yanpingliu2021/pubmed-citation-explorer.git``` in your desired directory </br>
Run ```make setup install``` to set up virtual environment</br>
Install [peotry](https://python-poetry.org/docs/#installation) and Run ```poetry install``` to install the dependencies</br>

### Set up AWS Services

Go to [AWS console](https://console.aws.amazon.com/) </br>
Set up a user in [AWS IAM page](https://console.aws.amazon.com/iam), record Access Key and Secret Key, and assign the following permissions to the user:  </br>

* AmazonRDSFullAccess
* AmazonEC2FullAccess
* AmazonS3FullAccess
* AdministratorAccess-AWSElasticBeanstalk

Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) tool, run ```aws configure``` to config access key, secret key and region </br>
Go to [AWS RDS page](https://console.aws.amazon.com/rds) to set up a PostgreSQL database</br>
Go to [AWS Elastic Beanstalk Page](https://console.aws.amazon.com/elasticbeanstalk) to set up an python application and create an environment for the application</br>
Go to [AWS S3](https://s3.console.aws.amazon.com/s3) and create a S3 bucket to store code base

### Run the application in Local Development

To run the application in local, first you will need to set up the following environment variables in local PC or MAC
</br>
</br>
Property name|Description|Property value
-------------|-----------|--------------
RDS_HOSTNAME|The hostname of the DB instance|On the Connectivity & security tab on the Amazon RDS console: Endpoint.
RDS_PORT|The port on which the DB instance accepts connections.|On the Connectivity & security tab on the Amazon RDS console: Port.
RDS_DB_NAME|The database name|this can be arbitrary, we will create the database using python
RDS_USERNAME|The username that you configured for your database.|On the Configuration tab on the Amazon RDS console: Master username.
RDS_PASSWORD|The password that you configured for your database.|Not available for reference in the Amazon RDS console.
RDS_TB_NAME|The table name to store the data|This can be arbitrary, we will create it using python

</br>Then run the ```download.py```, ```upload.py```, and ```preprocess.py``` python file under the ```src``` folder to download the data and upload them to AWS RDS PostgreSQL database. It may take one day to load the data as the files are pretty large

Finally, run ```make start-api``` to launch the App
</br>

### Deploy the app to AWS Elastic Beanstalk

To achieve continuous deployment to AWS Elastic Beanstalk using github actions,
first create the following [secrets](https://docs.github.com/en/actions/reference/encrypted-secrets) in your github repo

* RDS_HOSTNAME
* RDS_USERNAME
* RDS_DB_NAME
* RDS_PASSWORD
* RDS_PORT
* RDS_TB_NAME
* MY_AWS_ACCESS_KEY
* MY_AWS_SECRET_KEY

Update the value for following environment variables in ```python-app.yml``` file under ```.github/workflows/```

* EB_PACKAGE_S3_BUCKET_NAME
* EB_APPLICATION_NAME
* EB_ENVIRONMENT_NAME
* AWS_REGION_NAME

Following this [AWS document](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/rds-external-defaultvpc.html) to config Elastic Beanstalk so that it can connect to the PostgreSQL database created.

Push changes to the github repo and github actions will automaically deploy the APP to ElasticBeanstalk
