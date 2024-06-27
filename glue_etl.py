import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import explode, col

# Initialise the GlueContext and SparkContext
args = getResolvedOptions(sys.argv, [])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init('test2', args)

# Define parameters
database_name = 'kgendata'
user_campaign_table = 'user_campaign'
campaign_info_table = 'campaigninfo'
output_path = 's3://flatten-data-de-project/data/'  # Fixed output path

# Read the user_campaign data from Glue Catalog table
user_campaign_dynamic_frame = glueContext.create_dynamic_frame.from_catalog(database=database_name, table_name=user_campaign_table)
user_campaign_df = user_campaign_dynamic_frame.toDF()

# Read the campaign_info data from Glue Catalog table
campaign_info_dynamic_frame = glueContext.create_dynamic_frame.from_catalog(database=database_name, table_name=campaign_info_table)
campaign_info_df = campaign_info_dynamic_frame.toDF()

# Explode the campaignTasks array to flatten the structure
campaign_info_exploded_df = campaign_info_df.withColumn("task", explode(col("campaigntasks"))) \
    .select(
        col("campaignid"),
        col("title"),
        col("rewardclaimdeadline"),
        col("endsattimestamp"),
        col("createdat"),
        col("updatedat"),
        col("task.taskID").alias("taskID"),
        col("task.rewardAmount").alias("rewardAmount"),
        col("task.taskDeadline").alias("taskDeadline")
    )

# Flatten the user_campaign JSON array
flattened_df = user_campaign_df.withColumn("pd", explode(col("progressdetails"))) \
    .select(
        col("userid"),
        col("campaignid"),
        col("createdat"),
        col("totaltaskrewardsearned"),
        col("updatedat"),
        col("usercampaignprogressstate"),
        col("pd.userCampaignTaskProgressState").alias("userCampaignTaskProgressState"),
        col("pd.rewardEarned").alias("rewardEarned"),
        col("pd.taskID").alias("taskID"),
        col("pd.validatedAt").alias("validatedAt"),
        col("pd.validationFailureReason").alias("validationFailureReason")
    )

# Join with campaign_info_exploded_df on campaignID and taskID to add taskDeadline
enhanced_df = flattened_df.join(
    campaign_info_exploded_df,
    (flattened_df.campaignid == campaign_info_exploded_df.campaignid) & (flattened_df.taskID == campaign_info_exploded_df.taskID),
    "left"
).select(
    flattened_df["*"],
    campaign_info_exploded_df["taskDeadline"]
)

# Partition by createdat column
partitioned_df = enhanced_df.withColumn("createdat_date", col("createdat").substr(1, 10)) \
    .drop("createdat")  # Drop the original createdat column to prevent duplication

# Adjust the output path to include partitioning
partitioned_output_path = output_path + "partitioned/"

# Write the result partitioned by createdat as Parquet files
partitioned_df.write.partitionBy("createdat_date") \
    .parquet(partitioned_output_path, mode="overwrite")

job.commit()

