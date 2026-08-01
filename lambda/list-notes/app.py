# Import the json library - used to convert Python data into JSON text format,
# which is what our API needs to send back to the browser
import json

# Import os - lets us read environment variables (like our table's name)
# instead of hardcoding them directly in the code
import os

# Import boto3 - AWS's official Python library, used to talk to any AWS service
import boto3

# Create a connection to the DynamoDB service in general (not a specific table yet)
dynamodb = boto3.resource('dynamodb')

# Read the actual table name from the environment variable that CloudFormation
# automatically set for us when we connected this Lambda to NotesTable
table_name = os.environ['NOTESTABLE_TABLE_NAME']

# Now point specifically at our Notes table, using that name
table = dynamodb.Table(table_name)


# This is the main function AWS runs every time this Lambda is triggered.
# "event" holds details about the incoming request (not used here since
# List Notes doesn't need any input - it just reads everything).
# "context" holds info about the execution environment (rarely needed).
def lambda_handler(event, context):
    # try/except: if anything goes wrong inside "try", we catch the error
    # instead of letting the whole Lambda crash with an ugly, unclear failure
    try:
        # Ask DynamoDB to read every single item in the table
        response = table.scan()

        # The actual list of notes lives inside the 'Items' key of the response
        notes = response['Items']

        # Success! Return HTTP 200 (OK), along with the notes as JSON text
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"  # tells the browser "this is JSON data"
            },
            "body": json.dumps(notes)  # convert our Python list into a JSON string
        }

    # If anything inside "try" throws an error, this block runs instead
    except Exception as e:
        # Return HTTP 500 (Internal Server Error) with a simple error message
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Failed to retrieve notes"})
        }