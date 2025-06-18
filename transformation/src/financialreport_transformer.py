#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, MapType
from pyspark.sql.functions import col, lit, coalesce, when

def transform_financial_reports():
    # Load Environment Variables
    load_dotenv()
    
    # Fetch MongoDB credentials and config
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    mongo_db_name = os.getenv("MONGODB_DATABASE_NAME")
    mongo_input_collection = os.getenv("COLLECTION_FINANCIAL_REPORTS")
    mongo_output_collection = "Docker_Transformasi_Laporan_Keuangan"
    
    # Construct URIs
    mongo_input_uri = mongo_connection_string
    mongo_output_uri = mongo_connection_string
    
    if not all([mongo_connection_string, mongo_db_name, mongo_input_collection]):
        raise ValueError("One or more MongoDB environment variables are missing. Check your .env file.")
    
    print(f"Using Database: {mongo_db_name}")
    print(f"Input Collection: {mongo_input_collection}")
    print(f"Output Collection: {mongo_output_collection}")
    
    # Set up Spark with JARs
    jars_path = "."
    jars = ",".join([
        os.path.join(jars_path, "mongo-spark-connector_2.12-3.0.1.jar"),
        os.path.join(jars_path, "mongo-java-driver-3.12.10.jar")
    ])
    
    for jar_file in jars.split(','):
        if not os.path.exists(jar_file):
            print(f"Warning: JAR file not found at {jar_file}. Download it or update the path.")
    
    spark = SparkSession.builder \
        .appName("MongoDBSparkTransform") \
        .config("spark.jars", jars) \
        .config("spark.mongodb.input.uri", mongo_input_uri) \
        .config("spark.mongodb.input.database", mongo_db_name) \
        .config("spark.mongodb.input.collection", mongo_input_collection) \
        .config("spark.mongodb.output.uri", mongo_output_uri) \
        .config("spark.mongodb.output.database", mongo_db_name) \
        .config("spark.mongodb.output.collection", mongo_output_collection) \
        .getOrCreate()
    
    # Define schema for xbrl_data
    xbrl_schema = StructType([
        StructField("EntityName", StringType(), True),
        StructField("EntityCode", StringType(), True),
        StructField("SalesAndRevenue", StringType(), True),
        StructField("GrossProfit", StringType(), True),
        StructField("ProfitFromOperation", StringType(), True),
        StructField("ProfitLoss", StringType(), True),
        StructField("CashAndCashEquivalents", StringType(), True),
        StructField("Assets", StringType(), True),
        StructField("ShortTermBankLoans", StringType(), True),
        StructField("LongTermBankLoans", StringType(), True),
        StructField("EquityAttributableToEquityOwnersOfParentEntity", StringType(), True),
        StructField("NetCashFlowsReceivedFromUsedInOperatingActivities", StringType(), True),
        StructField("NetCashFlowsReceivedFromUsedInInvestingActivities", StringType(), True),
        StructField("NetCashFlowsReceivedFromUsedInFinancingActivities", StringType(), True),
        StructField("PeriodOfFinancialStatementsSubmissions", StringType(), True),
        StructField("DateOfBoardOfDirectorsStatementLetter", StringType(), True),
        StructField("CurrentPeriodStartDate", StringType(), True),
        StructField("CurrentPeriodEndDate", StringType(), True),
        StructField("PriorYearEndDate", StringType(), True),
        StructField("PriorPeriodStartDate", StringType(), True),
        StructField("PriorPeriodEndDate", StringType(), True),
        StructField("Prior2YearEndDate", StringType(), True),
    ])
    
    # Define top-level schema
    input_schema = StructType([
        StructField("_id", StringType(), True),
        StructField("company", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("taxonomy", MapType(StringType(), StringType()), True),
        StructField("xbrl_data", xbrl_schema, True),
    ])
    
    # Load data with specified schema

    # Define schema for existing data in the output collection
    existing_df_fields = [
        StructField("EntityName", StringType(), True),
        StructField("EntityCode", StringType(), True),
        StructField("SalesAndRevenue", DoubleType(), True),
        StructField("GrossProfit", DoubleType(), True),
        StructField("ProfitFromOperation", DoubleType(), True),
        StructField("ProfitLoss", DoubleType(), True),
        StructField("CashAndCashEquivalents", DoubleType(), True),
        StructField("Assets", DoubleType(), True),
        StructField("ShortTermBankLoans", DoubleType(), True),
        StructField("LongTermBankLoans", DoubleType(), True),
        StructField("EquityAttributableToEquityOwnersOfParentEntity", DoubleType(), True),
        StructField("NetCashFlowOp", DoubleType(), True),
        StructField("NetCashFlowInv", DoubleType(), True),
        StructField("NetCashFlowFin", DoubleType(), True),
        StructField("PeriodOfFinancialStatementsSubmissions", StringType(), True),
        StructField("DateOfBoardOfDirectorsStatementLetter", StringType(), True),
        StructField("CurrentPeriodStartDate", StringType(), True),
        StructField("CurrentPeriodEndDate", StringType(), True),
        StructField("PriorYearEndDate", StringType(), True),
        StructField("PriorPeriodStartDate", StringType(), True),
        StructField("PriorPeriodEndDate", StringType(), True),
        StructField("Prior2YearEndDate", StringType(), True),
        StructField("DebtToEquityRatio", DoubleType(), True),
        StructField("ReturnOnAssets", DoubleType(), True)
    ]
    existing_df_schema = StructType(existing_df_fields)

    # Try to read existing data from the output collection
    try:
        existing_df = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
            .option("uri", mongo_output_uri) \
            .option("database", mongo_db_name) \
            .option("collection", mongo_output_collection) \
            .schema(existing_df_schema) \
            .load()
        print(f"Read existing data from {mongo_output_collection}.") # Rephrased
    except Exception as e:
        print(f"Could not read existing data from {mongo_output_collection} (may not exist or be empty): {str(e)}. Proceeding with an empty DataFrame for existing data.")
        existing_df = spark.createDataFrame([], existing_df_schema) # Create an empty DataFrame with the correct schema

    # Removed: count and show for existing_df

    df = spark.read.format("com.mongodb.spark.sql.DefaultSource").schema(input_schema).load()
    
    # Transform data
    spark.conf.set("spark.sql.caseSensitive", True)
    
    df_selected = df.withColumn("EntityName", col("xbrl_data.EntityName")) \
        .withColumn("EntityCode", col("xbrl_data.EntityCode")) \
        .withColumn("SalesAndRevenue", col("xbrl_data.SalesAndRevenue").cast(DoubleType())) \
        .withColumn("GrossProfit", col("xbrl_data.GrossProfit").cast(DoubleType())) \
        .withColumn("ProfitFromOperation", col("xbrl_data.ProfitFromOperation").cast(DoubleType())) \
        .withColumn("ProfitLoss", col("xbrl_data.ProfitLoss").cast(DoubleType())) \
        .withColumn("CashAndCashEquivalents", col("xbrl_data.CashAndCashEquivalents").cast(DoubleType())) \
        .withColumn("Assets", col("xbrl_data.Assets").cast(DoubleType())) \
        .withColumn("ShortTermBankLoans", col("xbrl_data.ShortTermBankLoans").cast(DoubleType())) \
        .withColumn("LongTermBankLoans", col("xbrl_data.LongTermBankLoans").cast(DoubleType())) \
        .withColumn("EquityAttributableToEquityOwnersOfParentEntity", 
                   col("xbrl_data.EquityAttributableToEquityOwnersOfParentEntity").cast(DoubleType())) \
        .withColumn("NetCashFlowOp", 
                   col("xbrl_data.NetCashFlowsReceivedFromUsedInOperatingActivities").cast(DoubleType())) \
        .withColumn("NetCashFlowInv", 
                   col("xbrl_data.NetCashFlowsReceivedFromUsedInInvestingActivities").cast(DoubleType())) \
        .withColumn("NetCashFlowFin", 
                   col("xbrl_data.NetCashFlowsReceivedFromUsedInFinancingActivities").cast(DoubleType())) \
        .withColumn("PeriodOfFinancialStatementsSubmissions", 
                   col("xbrl_data.PeriodOfFinancialStatementsSubmissions")) \
        .withColumn("DateOfBoardOfDirectorsStatementLetter", 
                   col("xbrl_data.DateOfBoardOfDirectorsStatementLetter")) \
        .withColumn("CurrentPeriodStartDate", col("xbrl_data.CurrentPeriodStartDate")) \
        .withColumn("CurrentPeriodEndDate", col("xbrl_data.CurrentPeriodEndDate")) \
        .withColumn("PriorYearEndDate", col("xbrl_data.PriorYearEndDate")) \
        .withColumn("PriorPeriodStartDate", col("xbrl_data.PriorPeriodStartDate")) \
        .withColumn("PriorPeriodEndDate", col("xbrl_data.PriorPeriodEndDate")) \
        .withColumn("Prior2YearEndDate", col("xbrl_data.Prior2YearEndDate")) \
        .withColumn("DebtToEquityRatio", 
                   (col("ShortTermBankLoans") + col("LongTermBankLoans")) / 
                   coalesce(col("EquityAttributableToEquityOwnersOfParentEntity"), lit(1.0))) \
        .withColumn("ReturnOnAssets", 
                   col("ProfitLoss") / coalesce(col("Assets"), lit(1.0)))
    
    # Define the final schema for output
    output_schema = StructType([
        StructField("EntityName", StringType(), True),
        StructField("EntityCode", StringType(), True),
        StructField("SalesAndRevenue", DoubleType(), True),
        StructField("GrossProfit", DoubleType(), True),
        StructField("ProfitFromOperation", DoubleType(), True),
        StructField("ProfitLoss", DoubleType(), True),
        StructField("CashAndCashEquivalents", DoubleType(), True),
        StructField("Assets", DoubleType(), True),
        StructField("ShortTermBankLoans", DoubleType(), True),
        StructField("LongTermBankLoans", DoubleType(), True),
        StructField("EquityAttributableToEquityOwnersOfParentEntity", DoubleType(), True),
        StructField("NetCashFlowOp", DoubleType(), True),
        StructField("NetCashFlowInv", DoubleType(), True),
        StructField("NetCashFlowFin", DoubleType(), True),
        StructField("PeriodOfFinancialStatementsSubmissions", StringType(), True),
        StructField("DateOfBoardOfDirectorsStatementLetter", StringType(), True),
        StructField("CurrentPeriodStartDate", StringType(), True),
        StructField("CurrentPeriodEndDate", StringType(), True),
        StructField("PriorYearEndDate", StringType(), True),
        StructField("PriorPeriodStartDate", StringType(), True),
        StructField("PriorPeriodEndDate", StringType(), True),
        StructField("Prior2YearEndDate", StringType(), True),
        StructField("DebtToEquityRatio", DoubleType(), True),
        StructField("ReturnOnAssets", DoubleType(), True)
    ])
    
    # Select only the columns in the output schema
    df_final = df_selected.select(output_schema.fieldNames())
    
    # Fill null values with 0 for numeric fields
    df_final = df_final.na.fill(0)

    print("New data (df_final) prepared for joining.") # Rephrased
    # Removed: show for df_final

    # Perform join with existing data
    # Add prefixes to distinguish columns after join
    existing_df_aliased = existing_df.alias("old")
    df_final_aliased = df_final.alias("new")

    join_condition = (col("old.EntityCode") == col("new.EntityCode")) & \
                     (col("old.CurrentPeriodEndDate") == col("new.CurrentPeriodEndDate"))

    # Perform full outer join
    merged_df = existing_df_aliased.join(
        df_final_aliased,
        join_condition,
        "full_outer"
    )

    # Removed: printSchema, count, and show for merged_df

    # Resolve columns using coalesce from 'new' and 'old' data
    key_fields = ["EntityCode", "CurrentPeriodEndDate"]
    all_field_names = existing_df_schema.fieldNames() # Using existing_df_schema as it's available

    select_exprs = []

    # Handle key fields first
    select_exprs.append(coalesce(col("new.EntityCode"), col("old.EntityCode")).alias("EntityCode"))
    select_exprs.append(coalesce(col("new.CurrentPeriodEndDate"), col("old.CurrentPeriodEndDate")).alias("CurrentPeriodEndDate"))

    # Handle the rest of the fields
    for field_name in all_field_names:
        if field_name not in key_fields:
            select_exprs.append(coalesce(col(f"new.{field_name}"), col(f"old.{field_name}")).alias(field_name))

    # Create the final DataFrame with resolved columns
    resolved_df = merged_df.select(select_exprs)

    # Removed: printSchema, count, and show for resolved_df before na.fill(0)

    # Fill null values with 0 for numeric fields in the final resolved DataFrame
    resolved_df = resolved_df.na.fill(0)
    
    # Removed: printSchema, count, and show for resolved_df after na.fill(0) and before write to temp
    # Removed: resolved_df.show(20, truncate=False) 

    # Write to temporary, read back, then write to main
    mongo_output_collection_temp = mongo_output_collection + "_temp"
    print(f"Writing resolved data to temporary collection {mongo_output_collection_temp}...") # Rephrased
    try:
        resolved_df.write \
            .format("com.mongodb.spark.sql.DefaultSource") \
            .mode("overwrite") \
            .option("collection", mongo_output_collection_temp) \
            .option("ignoreNullFields", "false") \
            .save()
        print(f"Successfully wrote to temporary collection {mongo_output_collection_temp}.") # Rephrased

        # Now, read from the temporary collection
        print(f"Reading data from temporary collection {mongo_output_collection_temp} for verification...") # Rephrased
        verified_df = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
            .option("uri", mongo_output_uri) \
            .option("database", mongo_db_name) \
            .option("collection", mongo_output_collection_temp) \
            .schema(existing_df_schema) \
            .load()
        
        # Removed: verified_df.show(5, truncate=False)
        verified_count = verified_df.count() # Keep count for conditional write
        print(f"Successfully read data from temporary collection {mongo_output_collection_temp} into verified_df.") # Rephrased

        if verified_count > 0: # Proceed only if verified_df is not empty
            # Now, write verified_df to the MAIN output collection
            print(f"Writing verified data to main collection {mongo_output_collection}...") # Rephrased
            verified_df.write \
                .format("com.mongodb.spark.sql.DefaultSource") \
                .mode("overwrite") \
                .option("collection", mongo_output_collection) \
                .option("ignoreNullFields", "false") \
                .save()
            print(f"Data successfully written from verified_df to MongoDB database '{mongo_db_name}', collection '{mongo_output_collection}'")
        else:
            print(f"Skipping write to main collection as verified data from temporary collection is empty.") # Rephrased

    except Exception as e_write_read_write:
        # Rephrased error message for the entire block
        print(f"ERROR during write/read operation involving temporary collection {mongo_output_collection_temp}: {str(e_write_read_write)}")

    # The original direct write of resolved_df to the main collection is now replaced by the block above.
    # print(f"Original write to {mongo_output_collection} is SKIPPED for this diagnostic run.") 
    # # resolved_df.write \
    # #     .format("com.mongodb.spark.sql.DefaultSource") \
    # #     .mode("overwrite") \
    # #     .option("ignoreNullFields", "false") \
    # #     .save()
    # # print(f"Data successfully written to MongoDB database '{mongo_db_name}', collection '{mongo_output_collection}'")
    
    spark.stop()

if __name__ == "__main__":
    transform_financial_reports()