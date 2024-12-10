# Databricks notebook source
import dlt
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.functions import col, to_timestamp, when

# Azure Blob Storage configuration
storage_account_name = "customersbdtest"
storage_account_key = "G+IfR7Ld8F/ruzCZYv6ipuKPuYzY7omq937Bx1/QGLhjXeDHe1s1Bxy3/77hfN6mRVPGQoNOsuSj+AStDm65Ig=="
container_name = "datalake1"
source_path = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/bronze/public/Customer_Support/"

# Set the storage account key for Databricks to access Azure Blob
spark.conf.set(f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net", storage_account_key)

# Define the schema for the customer support data
schema = StructType([
    StructField("support_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("interaction_date", TimestampType(), True),
    StructField("issue_description", StringType(), True),
    StructField("resolution_status", StringType(), True)
])

# Create a raw Delta Live Table for ingesting data
# Ingest raw data and cast columns to the correct types
@dlt.table(
    comment="Raw customer support data ingested from Azure Blob Storage with type casting."
)
def raw_customer_support_data():
    return (
        spark.read.format("parquet")
        .load("wasbs://datalake1@customersbdtest.blob.core.windows.net/bronze/public/Customer_Support/")
        .withColumn("support_id", col("support_id").cast("string"))  # Cast integer to string
        .withColumn("customer_id", col("customer_id").cast("string"))  # Cast integer to string
    )

# Process and clean data
@dlt.table(
    comment="Processed customer support data with added transformations."
)
def processed_customer_support_data():
    return (
        dlt.read("raw_customer_support_data")
        .withColumn("interaction_date", col("interaction_date"))
        .withColumn("priority", 
                    when(col("resolution_status") == "Unresolved", "High")
                    .when(col("resolution_status") == "Pending", "Medium")
                    .otherwise("Low"))
    )

# COMMAND ----------

# MAGIC %md
# MAGIC End-to-End Data Pipeline with Delta Live Tables and Dashboards

# COMMAND ----------

# MAGIC %md
# MAGIC Overview
# MAGIC This document provides a step-by-step guide to implementing a data pipeline in Databricks using Delta Live Tables (DLT), transforming the data, and creating interactive dashboards for visualization.

# COMMAND ----------

# MAGIC %md
# MAGIC Pipeline Overview
# MAGIC
# MAGIC Data Source
# MAGIC
# MAGIC Source: Azure Blob Storage
# MAGIC
# MAGIC Format: Parquet files
# MAGIC
# MAGIC Schema:
# MAGIC support_id: integer
# MAGIC customer_id: integer
# MAGIC interaction_date: timestamp
# MAGIC issue_description: string
# MAGIC resolution_status: string
# MAGIC Pipeline Steps
# MAGIC 1. Ingest Raw Data: Read data from Azure Blob Storage into a raw Delta Live Table.
# MAGIC 2. Process Data: Transform and clean data (e.g., casting types, creating calculated fields).
# MAGIC 3. Visualize Data: Use Databricks SQL to create dashboards for interactive analysis.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Create Delta Live Tables (DLT)
# MAGIC
# MAGIC Ingest Raw Data
# MAGIC
# MAGIC The raw data is read from Azure Blob Storage and stored in a Delta table. Type mismatches are resolved by casting support_id and customer_id to STRING.

# COMMAND ----------

# import dlt
# from pyspark.sql.functions import col

# @dlt.table(
#     comment="Raw customer support data ingested from Azure Blob Storage with type casting."
# )
# def raw_customer_support_data():
#     return (
#         spark.read.format("parquet")
#         .load("wasbs://datalake1@customersbdtest.blob.core.windows.net/bronze/public/Customer_Support/")
#         .withColumn("support_id", col("support_id").cast("string"))
#         .withColumn("customer_id", col("customer_id").cast("string"))
#     )


# COMMAND ----------

# MAGIC %md
# MAGIC Process Data
# MAGIC
# MAGIC Create a processed Delta Live Table with calculated fields:
# MAGIC
# MAGIC
# MAGIC priority: Derived from resolution_status.
# MAGIC
# MAGIC Transformations:
# MAGIC
# MAGIC High priority: resolution_status = "Unresolved"
# MAGIC
# MAGIC Medium priority: resolution_status = "Pending"
# MAGIC
# MAGIC Low priority: Default value.

# COMMAND ----------

# @dlt.table(
#     comment="Processed customer support data with added transformations."
# )
# def processed_customer_support_data():
#     return (
#         dlt.read("raw_customer_support_data")
#         .withColumn("priority", 
#                     when(col("resolution_status") == "Unresolved", "High")
#                     .when(col("resolution_status") == "Pending", "Medium")
#                     .otherwise("Low"))
#     )


# COMMAND ----------

# MAGIC %md
# MAGIC 2. Run the Delta Live Table Pipeline
# MAGIC
# MAGIC Configure Pipeline:
# MAGIC
# MAGIC Target: default schema (or a custom schema configured in the pipeline).
# MAGIC
# MAGIC Storage location: Azure Blob Storage.
# MAGIC
# MAGIC Start the Pipeline:
# MAGIC
# MAGIC Open the Delta Live Tables interface in Databricks.
# MAGIC
# MAGIC Run the pipeline in Development Mode for testing.
# MAGIC
# MAGIC Once verified, switch to Production Mode.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Create Dashboards in Databricks SQL

# COMMAND ----------

# MAGIC %md
# MAGIC Visualizations
# MAGIC
# MAGIC Table of Most Repeated Issues

# COMMAND ----------

# %sql
# SELECT issue_description, COUNT(*) as count
# FROM processed_customer_support_data
# GROUP BY issue_description
# ORDER BY count DESC
# LIMIT 10;


# COMMAND ----------

# MAGIC %md
# MAGIC Visualization: Simple table listing issue descriptions with their counts.

# COMMAND ----------

# MAGIC %md
# MAGIC Number of Support Interactions by Priority

# COMMAND ----------

# %sql
# SELECT priority, COUNT(support_id) as count
# FROM processed_customer_support_data
# GROUP BY priority
# ORDER BY count DESC;


# COMMAND ----------

# MAGIC %md
# MAGIC Visualization: Bar chart showing the count of support interactions by priority.

# COMMAND ----------

# MAGIC %md
# MAGIC Resolution Status Distribution

# COMMAND ----------

# %sql
# SELECT resolution_status, COUNT(*) as count
# FROM processed_customer_support_data
# GROUP BY resolution_status;


# COMMAND ----------

# MAGIC %md
# MAGIC Visualization: Pie chart showing the proportion of records for each resolution status.

# COMMAND ----------

# MAGIC %md
# MAGIC Publish Dashboards
# MAGIC
# MAGIC Create Dashboard:
# MAGIC
# MAGIC Use Databricks SQL to add all visualizations to a single dashboard.
# MAGIC
# MAGIC Title: "Customer Support Analysis"
# MAGIC
# MAGIC Schedule Refresh:
# MAGIC
# MAGIC Configure the dashboard to refresh periodically (e.g., every hour) to ensure updated data.
# MAGIC
# MAGIC Share Dashboard:
# MAGIC
# MAGIC Share the dashboard with team members or stakeholders for collaborative analysis.
# MAGIC
# MAGIC
# MAGIC Monitor the Pipeline and Dashboard
# MAGIC
# MAGIC Use the Delta Live Tables interface to monitor pipeline runs and ensure data freshness.
# MAGIC
# MAGIC Check logs for any failures and troubleshoot as needed.

# COMMAND ----------

# MAGIC %md
# MAGIC Best Practices
# MAGIC
# MAGIC Data Validation:
# MAGIC
# MAGIC Always inspect the source data schema using df.printSchema() before creating Delta Live Tables.
# MAGIC
# MAGIC Error Handling:
# MAGIC
# MAGIC Use .cast() to handle data type mismatches in the source data.
# MAGIC
# MAGIC Pipeline Optimization:
# MAGIC
# MAGIC Use mergeSchema if the source schema evolves over time.
# MAGIC
# MAGIC Visualization Updates:
# MAGIC
# MAGIC Periodically review dashboards to add or modify visualizations based on new requirements.