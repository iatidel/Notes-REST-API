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
# "event" holds details about the incoming request - for Delete Notes,
# the important part is the note's id, which comes from the URL itself
# (e.g. DELETE /notes/abc123 -> event['pathParameters']['id'] = 'abc123')
def lambda_handler(event, context):
    # try/except: if anything goes wrong inside "try", we catch the error
    # instead of letting the whole Lambda crash with an ugly, unclear failure
    try:
        # Pull the note id out of the URL path
        note_id = event['pathParameters']['id']

        # Before deleting, check the note actually exists.
        # Without this check, DynamoDB would happily "succeed" even if the
        # id doesn't exist, and we'd never know to return a 404.
        existing_item = table.get_item(Key={'id': note_id})

        # If 'Item' isn't in the response, DynamoDB found nothing with that id
        if 'Item' not in existing_item:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": f"Note {note_id} not found"})
            }

        # The note exists, so now we actually delete it
        table.delete_item(Key={'id': note_id})

        # Success! Return HTTP 200 (OK), confirming the delete
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": f"Note {note_id} deleted"})
        }

    # If anything inside "try" throws an error, this block runs instead
    except Exception as e:
        # Return HTTP 500 (Internal Server Error) with a simple error message
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Failed to delete note"})
        }