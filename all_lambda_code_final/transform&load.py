import json
import csv
import boto3
import psycopg2 as psy
import pandas as pd
from io import StringIO

def get_ssm_param(ssm_client, param_name):
    print(f'get_ssm_param: getting param_name={param_name}')
    parameter_details = ssm_client.get_parameter(Name=param_name)
    redshift_details = json.loads(parameter_details['Parameter']['Value'])

    host = redshift_details['host']
    user = redshift_details['user']
    db = redshift_details['database-name']
    port = redshift_details['port']
    password = redshift_details['password']
    print(f'get_ssm_param loaded for db={db}, user={user}, host={host}')
    return {
        'host': host,
        'user': user,
        'database-name': db,
        'port': port,
        'password': password
    }

def process_products(file_contents, cursor):
    try:
        # Define column names and read CSV file
        df = pd.read_csv(StringIO(file_contents), header=0)
        
        # Drop unnecessary columns
        columns_to_drop_index = [0, 1, 3, 4]
        df.drop(columns=df.columns[columns_to_drop_index], axis=1, inplace=True)
        
        # Split orders and explode them
        df['Orders'] = df['Orders'].str.split(',')
        df = df.explode('Orders')
        df.reset_index(drop=True, inplace=True)

        # Remove product prices from the text and extract product prices
        df['Product'] = df['Orders'].str.replace(r'\s*\d+\.\d+\s*$', '').str.strip()
        df['Product Price'] = df['Orders'].str.extract(r'(\d+\.\d+)')

        # Drop the original text column
        df.drop(columns=['Orders'], inplace=True)

        # Clean product names and convert prices to float
        df['Product'] = df['Product'].str.rstrip('-')
        df['Product Price'] = df['Product Price'].astype(float)

        # Stripping price from exploded products
        df['Product'] = df['Product'].str.rstrip('- 0123456789.')
        
        # Dropping duplicates from table
        df.drop_duplicates(inplace=True)
        
        # Add white spaces back to product names
        df['Product'] = df['Product'].str.replace(r'(?<=[a-z])(?=[A-Z])', ' ')

        # Convert DataFrame to list of dictionaries
        list_of_dicts = df.to_dict(orient='records')
        
        # Insert records into the Redshift table if they don't already exist
        for record in list_of_dicts:
            cursor.execute(
                "SELECT COUNT(*) FROM productstest WHERE product_name = %s AND product_price = %s",
                (record['Product'], record['Product Price'])
            )
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    "INSERT INTO productstest (product_name, product_price) VALUES (%s, %s)",
                    (record['Product'], record['Product Price'])
                )
        print("Product Loaded")
        
    except Exception as e:
        print("Products not loaded:", e)

def process_transactions(file_contents, cursor):
    try:
        # Define column names and read CSV file
        df = pd.read_csv(StringIO(file_contents), header=0)
        
        # Remove unnecessary and sensitive data columns
        columns_to_drop_index = [2]
        df.drop(columns=df.columns[columns_to_drop_index], axis=1, inplace=True)
        
        # Convert DataFrame into list of dictionaries
        list_of_dicts = df.to_dict(orient='records')
        
        # Insert records into the Redshift table
        for record in list_of_dicts:
            cursor.execute(
                "INSERT INTO transactionstest (date_time, location, total_amount, payment_method) VALUES (%s, %s, %s, %s)",
                (record['Date & Time'], record['Location'], record['Total Amount'], record['Payment Option'])
            )
        print("Transaction Loaded")
        
    except Exception as e:
        print("Transaction Failed:", e)

def process_orders(file_contents, conn):
    try:
        df = pd.read_csv(StringIO(file_contents))
        
        
        # Split orders and explode them
        df['Orders'] = df['Orders'].str.split(',')
        df = df.explode('Orders')
        df.reset_index(drop=True, inplace=True)

        # Remove product prices from the text and extract product prices
        df['Product'] = df['Orders'].str.replace(r'\s*\d+\.\d+\s*$', '').str.strip()
        df['Product Price'] = df['Orders'].str.extract(r'(\d+\.\d+)')

        # Drop the original text column
        df.drop(columns=['Orders'], inplace=True)

        # Clean product names and convert prices to float
        df['Product'] = df['Product'].str.rstrip('-')
        df['Product Price'] = df['Product Price'].astype(float)

        # Stripping price from exploded products
        df['Product'] = df['Product'].str.rstrip('- 0123456789.')
        # Dropping duplicates from table
        df.drop_duplicates(inplace=True)

        cursor = conn.cursor()

        for index, row in df.iterrows():
            cursor.execute("""
                SELECT product_id
                FROM productstest
                WHERE product_name = %s AND product_price = %s
            """, (row['Product'], row['Product Price']))

            product_result = cursor.fetchone()

            if product_result:
                product_id = product_result[0]
                cursor.execute("""
                    SELECT transaction_id
                    FROM  transactionstest
                    WHERE date_time = %s AND location = %s AND total_amount = %s AND payment_method = %s
                """, (row['Date & Time'], row['Location'], row['Total Amount'], row['Payment Option']))

                transaction_result = cursor.fetchone()

                if transaction_result:
                    transaction_id = transaction_result[0]
                    cursor.execute("""
                        INSERT INTO orderstest (transaction_id, product_id)
                        VALUES (%s, %s)
                    """, (transaction_id, product_id))
                    conn.commit()
                else:
                    print("No matching transaction found for row:", row)
            else:
                print("No matching product found for row:", row)
            
        print("Orders loaded")
    except Exception as e:
        print("Orders Failed:", e)

def lambda_handler(event, context):
    try:
        session = boto3.Session()
        ssm_client = session.client('ssm')
        s3 = boto3.client('s3')

        ssm_param_name = get_ssm_param(ssm_client, 'brewtopia_redshift_settings')
        print(ssm_param_name)

        conn = psy.connect(
            database=ssm_param_name['database-name'],
            host=ssm_param_name['host'],
            port=ssm_param_name['port'],
            password=ssm_param_name['password'],
            user=ssm_param_name['user']
        )

        source_bucket_name = 'brewtopia-bucket-cleaned'
        file_key = event['Records'][0]['s3']['object']['key']
        
        cursor = conn.cursor()

        response = s3.get_object(Bucket=source_bucket_name, Key=file_key)
        file_contents = response['Body'].read().decode('utf-8')
        
        process_products(file_contents, cursor)
        process_transactions(file_contents, cursor)
        process_orders(file_contents, conn)
        
        conn.commit()
        print("everything loaded successfully")
        cursor.close()
        conn.close()

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
