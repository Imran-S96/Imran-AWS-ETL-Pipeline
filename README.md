# Brewtopia-Final-Project

# Elevator pitch

**Our target customer** - Owner of the coffee shop, their managers and staff

**Statement of need** - no way of identifying trends, meaning they are potentially losing out on major revenue streams

**Product/project name** - Brewtopia

**Product Type** - Cafe Cloud App

**Key benefits of product** - Our software will Generate reports for all branches, it will streamline the entire process making it time efficient, the software will Gathering meaningful data for the company on the whole.


## Setting up a venv

### Python 3.4 and above:
```python -m venv venv ```

### All other Python versions:

```pip install virtualenv ```

```virtualenv [directory] ```


## venv activation 
### In cmd.exe

``` venv\Scripts\activate.bat ```

### In Powershell 
```venv\Scripts\Activate.ps1 ```


## Linux and MacOS
```source myvenv/bin/activate ```


## Installing libaries from requirements.txt

```pip install -r requirements.txt ```



## Team Members AKA The Fabulous 5


### Imran (Scrum Master)


## Ways of working

Our approach each week we chose a Scrumaster. They were responsible for allocating tickets to individuals or groups. Taking an Agile approach we had 15 minute daily stand ups to allocate tickets assign to individuals of groups and 15 minute daily debriefs to check the progress of tickets and potential issues that arose.

If any problems arose we would collectivly discuss the issues and brainstorm ideas for potential fixes. For example breaking up tickets into smaller more managable tickets or re-assigning tickets to different individuals or groups.

Communication and teamwork were significant factors in our working approach. We used platforms such as Slack, Trello and Zoom as they had a variety of tools that we could benefit from. 

Code was shared on Github consistenyly to ensure all members of the group had access to the updated script. This was done by commiting, pushing and pulling branches onto the online repository then carefully reviewed by all members before being merged onto the main branch.

## Components

AWS (Amazon Web Services) our Cloud infrastructure of choice:

s3 (Simple Storage Service) An object storage service by AWS for scalable, inexpensive and secure storage of large data.

EC2 (Elastic Compute Cloud) A virtual server in the AWS cloud, allowing a pay-as-you go model for scalable compute.

Redshift is a fully managed datawarehouse service by AWS for analysing large datasets.

CloudWatch is a monitoring and observability service by AWS for tracking and managing cloud resources.

Lambda is a serverless, on demand computing service by AWS that lets us run code without provisioning or managing servers.

Grafana is data visualisation platform with high accessibility and a wide range of tools including monitoring. 

# How does it work?

## *ETL Pipeline Architecture*

![alt text](<ETL Pipeline BrewTopia.png>)

We used an ETL pipeline for our application as it was cost effective and ensured data protection.
The process consisted of cleaning and organising raw data to prepare it for storage and data analytics.

### *Extract*
Firstly, CSV's are uploaded onto a RAW s3 bucket which invokes the first Lambda known as the "Extract/transform" Lambda. The python code is then activated and the CSV's are cleansed and normalised using the pandas dataframe. This stage is important as it removes sensitive data, reducing the workload for the coming steps priming it for the transormation stage of the pipeline.

### *Transform*
Once the files have been put into the Transformed s3 bucket it then triggers another invocation from the second Lambda known as the "Load" Lambda. This then takes the data from transformed bucket and loads them onto Redshift data warehouse. Boto3 and psycopg2 played a crucial role in establishing a connection to the database cluster.

### *Load*
Once this stage has been succesfully accomplished we can use various components such as Grafana and Cloudwatch supported by docker and AWS EC2 instance making it accessible to anyone, anywhere who has access to the private VPC. These components provided tools to visualise and monitor the data now presented as tables and graphs allowing many beneficial business analysis possibilities. This can include top grossing products, most active times of day, highest demanded products, errors in the data files, overall and individual revenue of franchises and many more.


## What could be done better?

There is always room for improvement and given more time and resources here are some things we could have done better.

Implemented more early stage Unit testing - enabling us to catch defects early in the application development process, before the code is integrated with other components. This can save significant time and cost by preventing defects from propagating to other parts of the system and reducing the complexity of debugging


# not sure what SQS is?

Included SQS mechanism - SQS would have allowed us decouple application components so that they run and fail independently, increasing the overall fault tolerance of the system. Multiple copies of every message are stored redundantly across multiple availability zones so that they are available whenever needed

advantages: more reliability, better security, scalability to handle spikes in activity, Durable

