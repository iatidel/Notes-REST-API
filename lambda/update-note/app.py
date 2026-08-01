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
# "event" holds details about the incoming request - for Update Notes,
# we need the note's id from the URL, and the new text from the request body
# (e.g. PUT /notes/abc123 with body {"text": "new note text"})
def lambda_handler(event, context):
    # try/except: if anything goes wrong inside "try", we catch the error
    # instead of letting the whole Lambda crash with an ugly, unclear failure
    try:
        # Pull the note id out of the URL path
        note_id = event['pathParameters']['id']

        # The request body arrives as a JSON string, so we need to parse it
        # into an actual Python dictionary before we can read values from it
        body = json.loads(event['body'])

        # Pull out the new text the user wants to save
        new_text = body.get('text')

        # If text is missing or empty, this is a bad request - don't even
        # bother checking the database, just reject it immediately
        if not new_text or not new_text.strip():
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": "Note text is required"})
            }

        # Before updating, check the note actually exists.
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

        # The note exists, so now we update its text field.
        # ReturnValues="ALL_NEW" tells DynamoDB to hand back the full,
        # updated item so we can send it straight back to the browser
        updated_item = table.update_item(
            Key={'id': note_id},
            UpdateExpression='SET #text_field = :new_text',
            ExpressionAttributeNames={'#text_field': 'text'},
            ExpressionAttributeValues={':new_text': new_text},
            ReturnValues='ALL_NEW'
        )

        # Success! Return HTTP 200 (OK), along with the updated note as JSON
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(updated_item['Attributes'])
        }

    # If anything inside "try" throws an error, this block runs instead
    except Exception as e:
        # Return HTTP 500 (Internal Server Error) with a simple error message
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Failed to update note"})
        }