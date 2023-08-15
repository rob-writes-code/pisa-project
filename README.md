# PISA Project

The final project of the Makers Data Engineering specialist track.

## Project Overview

The goal of the project was to leverage data engineering skills to analyse the PISA 2018 dataset and develop a functioning dashboard that GEI can use to easily visualise and interpret the data. The project is carried out in a distributed environment in the Cloud to allow for efficient data processing and collaboration.

I completed the project in a team, with two other colleagues.

### About Global Education Insights (GEI)

Global Education Insights (GEI) is a non-profit organisation dedicated to improving education systems worldwide. They work with governments, educational institutions, and stakeholders to provide data-driven insights and recommendations for educational policy and practice.

### About PISA and the Dataset

PISA is the OECD's "Programme for International Student Assessment", which assesses educational practices around the world and uses its findings to influence policy.

The dataset used in this project is a real-life dataset, collected in 2018 by PISA. It contains responses from hundreds of thousands of students, teachers and educational facilitators from 79 countries, providing information about their backgrounds and experiences in education.

For more information about the 2018 dataset, please follow this [link](https://www.oecd.org/pisa/data/2018database/).

For the purposes of this project, we took a sample of **20 countries**. Responses were submitted gradually over time, to simulate the real-life scenario of collecting data. 

The dataset began at around 100 responses, but grew to over 100,000 in little over a week's time.

### Project Objectives

The project had three levels of challenge:

- **Level 1:** Develop dashboard charts displaying correct summary data that is no more than an hour old.
- **Level 2:** Same as Level 1, but the data should be no more than a minute old.
- **Level 3:** Same as Level 2, but the data should be up-to-the-second.

## Solution Overview

For our solution we implemented the following:

- Airflow to routinely extract data from 20 source databases and load into an analytical database held on AWS RDS
- Flask app to transform and serve data to our dashboard app
- Dashboard app tp poll endpoint each second to constantly update data visualisations as responses are submitted
- All running in the Cloud, using AWS EC2 and Render (PaaS provider)

Data Pipeline - Planning Stage
![pipeline_plan](/images/pipeline_plan.png)

Data Pipeline - Implemented
![pipeline_implemented](/images/pipeline_implemented.png)



### Stack

The tech stack used in this project.

![project_stack](./images/pisa-project-stack.png)

### Apache Airflow

Workflow orchestration tool used to pull data from 20 source databases and load them into an analytical database held on AWS RDS.

Tasks and order of flow defined in a Directed Acyclic Graph (DAG):

[pisa_dag](/airflow/pisa_dag.py)

![overview_of_dag_flow](/images/dag_flow.png)

DAG scheduled to run every 30 seconds to continuously and automatically keep pulling any new submissions, pooling them into a central database on which our dashboard was based.

Benefits of approach:
- **Resusable** - code accepts list of countries; more can easily be added to increase scope of project.
- **Scalable** - designed to only extract new entries to reduce latency. Runtime remained consistent, despite growing dataset.
- **Data Integrity** - checks made for duplicates and conflicts updated with new values, to ensure integrity and freshness of data.

Disadvantage:
- Minimum runtime of the DAG was 15 seconds, meaning the analytical database would be slightly out of date / not exactly real-time.
- Could be improved by reconfiguring concurrency / parallelism settings, or by redesigining project to use a data streaming service, such as Kafka.


### Real-Time Data Visualization

The web application, programmed in Python using Flask and hosted on a render.com web service, takes center stage in delivering real-time insights. As users interact with the dashboard, they're effectively accessing live data from the central AWS RDS. The automated DAGs ensure that the dataset feeding into the dashboard is always reflective of the latest developments, fostering accurate, real-time analysis and decision-making.

### Apache Airflow DAGs: Automation Backbone

The automated data collection and integration process is executed through the use of Apache Airflow DAGs. These DAGs facilitate the seamless extraction, transformation, and loading (ETL) of data from the distributed AWS RDS sources into the central repository. The DAGs ensure the solution's persistence by continuously refreshing the dataset, providing the dashboard with an ever-evolving pool of data.

### Render.com: Continuous Deployment

The Forage Dashboard remains accessible and available. By hosting the Flask application on render.com, the solution achieves continuous deployment, ensuring that the dashboard is always ready to be accessed by GEI. This continuous availability is crucial for maintaining a persistent connection to real-time data insights.

### Empowering Data-Driven Decisions

The automated and persistent nature of the Forage Dashboard empowers GEI to make data-driven decisions without interruption. The Airflow DAGs ensure that the dataset is perpetually refreshed, enabling the visualisation of real-time trends and patterns. Render.com guarantees that the dashboard is always accessible, whether on a desktop or mobile device, enhancing the user experience and fostering effective decision-making.

By combining Apache Airflow's automation capabilities with render.com's continuous deployment, the Forage Dashboard remains an innovative solution that bridges data science and accessibility for informed education policy and practice improvements.

<hr>

This project is licensed under MIT.
