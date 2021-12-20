# most-wanted-programming-skills-finder

# Table of contents

* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Application view](#application-view)

## General info

<details>
    <summary>Click here to see general information about application!</summary>
        <br>
        With this app, you can see what programming skills are most in demand in the
        current job market.

</details>

## Technologies

<details>
    <summary>Click here to see the technologies used!</summary>
        <ul>
            <li>Airflow 2.0</li>
            <li>AWS EMR 5.25</li>
            <li>AWS Lambda</li>
            <li>Boto3 1.20.0</li>
            <li>Docker 20.10.7</li>
            <li>Docker-compose 1.29.2</li>
            <li>Django 3.2.5</li>
            <li>Hadoop 2.8.5</li>
            <li>Pandas 1.3.4</li>
            <li>Python 3.8.5</li>
            <li>Postgres 12.5</li>
            <li>Scrapy 1.7.3</li>
            <li>Serverless 2.64.1</li>
            <li>Terraform 1.0.3</li>
        </ul>
</details>

## Setup

---
### Prepare skills scraper
1. Write your AWS credentials into __/skills_finder_web/.env__ and also __/.aws/credentials__ files.
2. Run this below commands (to execute this commands you must use __Linux__ system!)
```shell
chmod +x create_aws_env.sh
./create_aws_env.sh
```
---
### Run ETL data pipeline
3. After that you can start ETL data pipeline by using Airflow (available on http://127.0.0.1:8080)
```
docker-compose -f .\docker-compose-airflow.yml up --build
```
---
### Run web server
4. Finally, when all dags complete their activities it is time to launch the web app. Just
navigate to /skills_finder_web directory and up another container.
```
docker-compose -f .\docker-compose-web.yml up --build
```

Application will be available on http://127.0.0.1:8000

## Application view

### ETL data pipeline
![data_pipeline_top](https://user-images.githubusercontent.com/57534862/144881540-3e060653-b0d4-4176-bf1c-61633dd2838d.PNG)

### Below charts are generated in "skill-finder-web" app

#### Most wanted backend skills
![backend-chart](https://user-images.githubusercontent.com/57534862/146748302-c8f426a6-cbc2-49a0-a3ed-163dcf0c5412.PNG)


#### Most wanted big-data skills
![big-data-chart](https://user-images.githubusercontent.com/57534862/146749177-d2830848-cdfa-4be2-8b30-356f6c7b99ac.PNG)



