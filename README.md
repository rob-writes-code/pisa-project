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

For the purposes of this project, we will be looking at a sample of **20 countries**. Responses will be submitted gradually over time, to simulate the real-life scenario of collecting data. 

The dataset begins at around 100 responses, but grows to over 100,000 in little over a week's time.

### Project Objectives

The project had three levels of challenge:

- **Level 1:** Develop dashboard charts displaying correct summary data that is no more than an hour old.
- **Level 2:** Same as Level 1, but the data should be no more than a minute old.
- **Level 3:** Same as Level 2, but the data should be up-to-the-second.

## Solution Overview

The Forage Dashboard solution is not only feature-rich but also deeply automated and persistent, making it an indispensable tool for Global Education Insights (GEI) to derive data-driven insights in real-time. Let's delve into the details of how this solution remains current and always accessible:

### Stack

![project_stack](./images/pisa-project-stack.png)

### Automated Data Collection and Integration

The foundation of this solution is built upon 20 Apache Airflow DAGs that execute continuously and autonomously. These DAGs orchestrate the collection and integration of data from 20 distinct AWS RDS sources. This process ensures that the central AWS RDS, which the Forage Dashboard relies upon, is continuously updated with the latest information every 30 seconds. By pooling data from these distributed sources, the dashboard guarantees a comprehensive and up-to-date perspective.

### Real-Time Data Visualization

The web application, programmed in Python using Flask and hosted on a render.com web service, takes center stage in delivering real-time insights. As users interact with the dashboard, they're effectively accessing live data from the central AWS RDS. The automated DAGs ensure that the dataset feeding into the dashboard is always reflective of the latest developments, fostering accurate, real-time analysis and decision-making.

### Apache Airflow DAGs: Automation Backbone

The automated data collection and integration process is executed through the use of Apache Airflow DAGs. These DAGs facilitate the seamless extraction, transformation, and loading (ETL) of data from the distributed AWS RDS sources into the central repository. The DAGs ensure the solution's persistence by continuously refreshing the dataset, providing the dashboard with an ever-evolving pool of data.

### Render.com: Continuous Deployment

The Forage Dashboard remains accessible and available. By hosting the Flask application on render.com, the solution achieves continuous deployment, ensuring that the dashboard is always ready to be accessed by GEI. This continuous availability is crucial for maintaining a persistent connection to real-time data insights.

### Empowering Data-Driven Decisions

The deeply automated and persistent nature of the Forage Dashboard empowers GEI to make data-driven decisions without interruption. The Airflow DAGs ensure that the dataset is perpetually refreshed, enabling the visualisation of real-time trends and patterns. Render.com guarantees that the dashboard is always accessible, whether on a desktop or mobile device, enhancing the user experience and fostering effective decision-making.

By combining Apache Airflow's automation capabilities with render.com's continuous deployment, the Forage Dashboard remains an innovative solution that bridges data science and accessibility for informed education policy and practice improvements.

<hr>

This project is licensed under MIT.
