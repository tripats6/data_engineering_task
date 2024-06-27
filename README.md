# data_engineering_task

## Task Notes

### Incremental Read from DynamoDB:
- Use DynamoDB Streams or a timestamp-based incremental reading strategy to handle new and updated records efficiently.

### Data Transformation:
- Use AWS Glue to flatten and join the data.
- Flatten the `progressDetails` array in `user_Campaign` so each entry becomes a separate row.
- Enhance the flattened data by joining with `campaignInfo` on `campaignID` and `taskID` to add the `taskDeadline`.

### Data Storage and Cataloging:
- Store the transformed data in an S3 bucket.
- Partition the data by `createdAt` for efficient querying.
- Catalog the S3 data in AWS Glue Data Catalog for easier querying with Athena.

# Solution Notes

# Data Pipeline with AWS Services

This repository demonstrates the implementation of a data pipeline using various AWS services to handle, process, and analyze data efficiently.

## Services Used

### AWS DynamoDB
**Use Case:** AWS DynamoDB is ideal for real-time applications, gaming platforms, IoT devices, and mobile apps that need fast and scalable NoSQL database capabilities.  
- **Usage:** Used to store the source table information.

### AWS Glue
**Use Case:** AWS Glue simplifies the ETL (Extract, Transform, Load) process for data preparation and loading into analytics solutions.  
- **Usage:**
  - Crawling data from DynamoDB tables into Glue Catalog Tables, enabling metadata management.
  - Executing ETL jobs to transform and clean data, making it analysis-ready.
  - Orchestrating complex data workflows through Glue Workflows, ensuring streamlined and automated data processing pipelines.

### AWS Lambda (Optional)
**Use Case:** AWS Lambda functions complement AWS Glue by enabling event-driven data processing and automation.  
- **Usage:**
  - Triggering Glue ETL jobs based on DynamoDB streams, allowing real-time data updates and transformations.

### AWS S3
**Use Case:** AWS S3 provides scalable, secure, and cost-effective object storage.  
- **Usage:** Storing flattened data after ETL processes performed by AWS Glue, serving as a data lake for analytics.

### AWS Athena
**Use Case:** AWS Athena enables SQL querying directly on data stored in S3.  
- **Usage:** Querying and exploration of cleansed and transformed data in S3 without the need for managing infrastructure.

### AWS IAM
**Use Case:** AWS IAM provides centralized identity and access management capabilities.  
- **Usage:** 
  - Securely controlling access to AWS services and resources across various AWS environments.
  - Defining and enforcing granular permissions and policies based on user roles and organizational requirements.

## Implementation Steps

1. **DynamoDB Table Creation and Stream Configuration:**
   - Two tables are created in DynamoDB based on the provided schema: `user_Campaign` and `campaignInfo`.
   - DynamoDB Streams are enabled on both tables to capture item-level changes, including insertions, updates, and deletions, enabling efficient handling of new and updated records.

2. **Glue Crawler Setup:**
   - AWS Glue Crawlers are configured to crawl the `user_Campaign` and `campaignInfo` tables in DynamoDB.
   - The crawlers create Glue Data Catalog tables that reflect the structure and schema of the DynamoDB tables, making them accessible for ETL operations.

3. **Glue ETL Job Creation:**
   - An AWS Glue ETL job is created using Apache Spark to process the data.
   - The ETL job performs the following tasks:
     - **Flattening:** The `progressDetails` array in the `user_Campaign` table is flattened so each entry becomes a separate row.
     - **Enhancement:** The flattened data is joined with `campaignInfo` on `campaignID` and `taskID` to add the `taskDeadline` attribute.
     - The `explode` function is used to flatten arrays.
   - The transformed data is then stored in an Amazon S3 bucket for further processing and analysis.

4. **Glue Workflow for Orchestration:**
   - A Glue Workflow is set up to orchestrate the entire ETL process, ensuring that all steps are executed in the correct sequence.
   - The workflow includes:
     - Running the Glue Crawlers to update the catalog tables.
     - Executing the Glue ETL job for data transformation.
     - Running a Glue Crawler on the transformed data in S3 to update the catalog.

5. **Scheduled Workflow Trigger:**
   - The Glue Workflow is scheduled to run every hour using a time-based trigger. This ensures that any changes in the source DynamoDB tables are captured and processed periodically.

6. **Alternative Event-Driven Approach with Lambda:**
   - To capture changes in real-time, a Lambda function is created with DynamoDB Streams as the event source.
   - The Lambda function is triggered for any change in the `user_Campaign` and `campaignInfo` tables.
   - The Lambda function then triggers the Glue Workflow, ensuring that the ETL process runs immediately upon detecting changes.

7. **Data Storage and Partitioning in S3:**
   - The transformed and enhanced data is stored in an S3 bucket.
   - The data is partitioned by the `createdAt` column to optimize query performance and data organization.
   - A Glue Crawler is run on the S3 data to catalog it, making it accessible for querying and analysis using services like AWS Athena.
  
![image](https://github.com/tripats6/data_engineering_task/assets/168261501/7f491ca7-175c-422c-b21e-9f57dd1b95da)

## Glue Workflow

![image](https://github.com/tripats6/data_engineering_task/assets/168261501/a1662702-c2a9-40fc-8b58-643c746ac205)


## Contributing

Feel free to fork this repository, submit issues, and send pull requests.

## License

This project is licensed under the MIT License.
