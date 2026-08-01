# Import the json library - used to convert between Python dictionaries
# and JSON text, since that's the format our API sends/receives
import json

# Import os - lets us read environment variables (like our table's name)
# instead of hardcoding them directly in the code
import os

# Import boto3 - AWS's official Python library, used to talk to any AWS service
import boto3

# Import uuid - used to generate a random, unique ID for each new note
import uuid

# Import datetime/timezone - used to generate a timestamp for when
# the note was created
from datetime import datetime, timezone

# Create a connection to the DynamoDB service in general (not a specific table yet)
dynamodb = boto3.resource('dynamodb')

# Read the actual table name from the environment variable that CloudFormation
# automatically set for us when we connected this Lambda to NotesTable
table_name = os.environ['NOTESTABLE_TABLE_NAME']

# Now point specifically at our Notes table, using that name
table = dynamodb.Table(table_name)


# This is the main function AWS runs every time this Lambda is triggered.
# "event" holds details about the incoming request - for Create Note,
# this is where the note's text (sent from the browser) will be found.
# "context" holds info about the execution environment (rarely needed).
def lambda_handler(event, context):
    # try/except: if anything goes wrong inside "try", we catch the error
    # instead of letting the whole Lambda crash with an ugly, unclear failure
    try:
        # event['body'] arrives as a plain JSON text string, not yet usable
        # as a Python dictionary - json.loads() converts it into one
        body = json.loads(event['body'])

        # Generate a random, unique ID for this new note
        # (we never trust the client/browser to supply this - we create it ourselves)
        note_id = str(uuid.uuid4())

        # Generate the current timestamp in UTC, in a clean standard format
        # (again, generated server-side, not trusted from the client)
        timestamp = datetime.now(timezone.utc).isoformat()

        # Save the new note into DynamoDB.
        # Field names here (id, text, createdAt) must exactly match
        # the data shape agreed with Person B, since List/Update/Delete
        # and the frontend all expect these same field names
        response = table.put_item(
            Item={
                'id': note_id,
                'text': body['text'],
                'createdAt': timestamp
            }
        )

        # Success! Return HTTP 201 (Created) - the standard status code
        # meaning "a new resource was successfully created"
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json"  # tells the browser "this is JSON data"
            },
            "body": json.dumps({"message": "Note created successfully", "note_id": note_id})
        }

    # If anything inside "try" throws an error (e.g. missing 'text' field,
    # DynamoDB failure, bad JSON), this block runs instead
    except Exception as e:
        # Return HTTP 500 (Internal Server Error) with a simple error message
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Failed to create note"})
        }