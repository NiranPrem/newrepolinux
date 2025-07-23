import json
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['resource']
    path_params = event.get('pathParameters') or {}
    task_id = path_params.get('id')
    body = json.loads(event.get('body') or '{}')

    # Extract Cognito user ID from the event (via API Gateway + Cognito Authorizer)
    user_id = event['requestContext']['authorizer']['claims']['sub']

    try:
        if method == 'GET':
            return get_tasks(user_id)
        elif method == 'POST':
            return add_task(user_id, body)
        elif method == 'PUT' and task_id:
            return update_task(user_id, task_id, body)
        elif method == 'DELETE' and task_id:
            return delete_task(user_id, task_id)
        else:
            return respond(400, {'message': 'Unsupported operation or missing ID'})
    except Exception as e:
        print('Error:', str(e))
        return respond(500, {'message': 'Internal server error', 'error': str(e)})

def decimal_to_float(obj):
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def get_tasks(user_id):
    response = table.query(
        IndexName='UserIdIndex',
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id}
    )
    items = response.get('Items', [])
    items = decimal_to_float(items)
    return respond(200, items)

def add_task(user_id, data):
    item = {
        'id': str(uuid.uuid4()),
        'userId': user_id,
        'text': data.get('text', ''),
        'date': data.get('date', 'No due date'),
        'prio': data.get('prio', 'Low'),
        'note': data.get('note', 'No notes'),
        'remindTime': data.get('remindTime', None),
        'prog': Decimal(str(data.get('prog', 0)))
    }
    table.put_item(Item=item)
    return respond(200, {'id': item['id']})

def update_task(user_id, task_id, data):
    # Verify the task belongs to the user
    task = table.get_item(Key={'id': task_id}).get('Item')
    if not task or task.get('userId') != user_id:
        return respond(403, {'message': 'Unauthorized access to task'})

    update_expression = 'SET #t = :t, #d = :d, #p = :p, #n = :n, #r = :r, #g = :g'
    expression_attribute_names = {
        '#t': 'text',
        '#d': 'date',
        '#p': 'prio',
        '#n': 'note',
        '#r': 'remindTime',
        '#g': 'prog'
    }
    expression_attribute_values = {
        ':t': data.get('text', ''),
        ':d': data.get('date', 'No due date'),
        ':p': data.get('prio', 'Low'),
        ':n': data.get('note', 'No notes'),
        ':r': data.get('remindTime', None),
        ':g': Decimal(str(data.get('prog', 0)))
    }
    table.update_item(
        Key={'id': task_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )
    return respond(200, {'message': 'Task updated'})

def delete_task(user_id, task_id):
    # Verify the task belongs to the user
    task = table.get_item(Key={'id': task_id}).get('Item')
    if not task or task.get('userId') != user_id:
        return respond(403, {'message': 'Unauthorized access to task'})

    table.delete_item(Key={'id': task_id})
    return respond(200, {'message': 'Task deleted'})

def respond(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
