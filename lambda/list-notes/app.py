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
# "event" holds details about the incoming request. We now use it to check
# whether this call is GET /notes (list everything) or GET /notes/{id}
# (fetch just one note), since this same function handles both routes.
# "context" holds info about the execution environment (rarely needed).
def lambda_handler(event, context):
    # try/except: if anything goes wrong inside "try", we catch the error
    # instead of letting the whole Lambda crash with an ugly, unclear failure
    try:
        # Check if this request came in with an {id} in the URL, e.g. /notes/123
        # API Gateway puts path parameters here when the route has {id} in it
        path_params = event.get('pathParameters')

        # Case 1: GET /notes/{id} -> the caller wants just one specific note
        if path_params and path_params.get('id'):
            note_id = path_params['id']

            # Ask DynamoDB for the single item matching this id
            response = table.get_item(Key={'id': note_id})
            item = response.get('Item')

            # If no item came back, that id doesn't exist in the table
            if not item:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({"error": "Note not found"})
                }

            # Found it - return the single note as JSON
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(item)
            }

        # Case 2: GET /notes -> the caller wants every note (original behavior)
        # Ask DynamoDB to read every single item in the table
        response = table.scan()

        # The actual list of notes lives inside the 'Items' key of the response
        notes = response['Items']

        # Success! Return HTTP 200 (OK), along with the notes as JSON text
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",  # tells the browser "this is JSON data"
                "Access-Control-Allow-Origin": "*"   # allows any website to call this API
            },
            "body": json.dumps(notes)  # convert our Python list into a JSON string
        }

    # If anything inside "try" throws an error, this block runs instead
    except Exception as e:
        # Return HTTP 500 (Internal Server Error) with a simple error message
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Failed to retrieve notes"})
        }
