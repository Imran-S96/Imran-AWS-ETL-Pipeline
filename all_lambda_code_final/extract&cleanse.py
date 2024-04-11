import json
import boto3
import pandas as pd
import io
import csv
import datetime

s3 = boto3.client('s3')

def remove_sensitive_data(file_obj):
    # Define column names and read CSV file
    colnames = ['Date & Time', 'Location', 'Names', 'Orders', 'Total Amount', 'Payment Option', 'Card Number']
    df = pd.read_csv(file_obj['Body'], names=colnames, header=None)
    
    # Remove unnecessary and sensitive data columns
    columns_to_drop_index = [2,6]
    df.drop(columns=df.columns[columns_to_drop_index], axis=1, inplace=True)
    
    # Remove duplicate records
    df.drop_duplicates(inplace=True)
    
    # Remove rows with missing value
    df.dropna(inplace=True)
    
    # Convert Total Amount column to float and remove rows with invalid floats
    df['Total Amount'] = pd.to_numeric(df['Total Amount'], errors='coerce')
    df.dropna(subset=['Total Amount'], inplace=True)
    
    # Convert DataFrame into list of dictionaries
    list_of_dicts = df.to_dict(orient='records')
    
    
    return list_of_dicts
    
    
def format_time(list_of_dicts):
    
    for x in list_of_dicts:
        # Get the date and time string from the dictionary
        date_time_str = x['Date & Time']
        # Break the date and time string into a datetime object
        date_time_obj = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M')
        # Format the datetime object in desired format
        formatted_date_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
        # Update the dictionary with new date and time format
        x['Date & Time'] = formatted_date_time
        
    return list_of_dicts

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            # Extract bucket name and file name from S3 event
            source_bucket_name = 'brewtopia-raw-bucket'
            file_key = record['s3']['object']['key']
            
            # Read the CSV file from S3
            response = s3.get_object(Bucket=source_bucket_name, Key=file_key)
            
            # Process the CSV file
            list_of_dicts = remove_sensitive_data(response)  # Corrected typo here
            
            #format date and time correctly
            format_time(list_of_dicts)
            
            # Convert list of dictionaries back to CSV format
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=list_of_dicts[0].keys())
            writer.writeheader()
            writer.writerows(list_of_dicts)
            csv_buffer.seek(0)
            
            # Upload the modified CSV as a new file to another S3 bucket
            target_bucket_name = 'brewtopia-bucket-cleaned'
            new_file_name = 'cleaned_' + file_key  # Prefix 'changes_' to original file name
            s3.put_object(Bucket=target_bucket_name, Key=new_file_name, Body=csv_buffer.getvalue(), ContentType='text/csv')

        return {
            'statusCode': 200,
            'body': 'Processed uploaded CSV files successfully'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Error processing uploaded CSV files'
        }