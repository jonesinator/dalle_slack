"""Generate Dalle images for slack. Designed to run as either a command-line
application or as an AWS Lambda pair."""

import base64
import json
import os
import sys
import traceback
import urllib.parse
import urllib.request

import boto3
import openai
import requests
from imgurpython import ImgurClient


def generate_image(prompt):
    """Generate the dalle image"""
    openai.organization = os.environ['OPENAI_ORGANIZATION']
    openai.api_key = os.environ['OPENAI_API_KEY']
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url

def upload_to_imgur(url):
    """Upload image to imgur"""
    client_id = os.environ['IMGUR_CLIENT_ID']
    client_secret = os.environ['IMGUR_CLIENT_SECRET']
    client = ImgurClient(client_id, client_secret)
    upload_result = client.upload_from_url(url, anon=True)
    upload_url = upload_result['link']
    return upload_url


def dalle(event, _):
    """Entry point for the lambda that actually generates the image."""
    try:
    # pylint: disable=broad-except
        # Process the SNS message.
        print(f"SNS MESSAGE: {event['Records'][0]['Sns']['Message']}")
        message = json.loads(event['Records'][0]['Sns']['Message'])
        response_url = message['response_url']
        prompt = message['prompt']
        user = message['user']

        # Process the command.
        print('GENERATE IMAGE: ' + prompt)

        image = generate_image(prompt)

        print('GENERATE IMAGE COMPLETE' + image)

        print('UPLOADING TO IMGUR')

        uploaded = upload_to_imgur(image)

        print('UPLOAD URL ' + uploaded)

        requests.post(response_url,
                      data=json.dumps({"response_type": "in_channel", "attachments": [
            {
                "fallback": prompt,
                "text": f'{user} generated: "{prompt}"',
                "image_url": uploaded,
            }
            ]}), timeout=10000)

    except Exception as exc:
        print('COMMAND ERROR: ' + str(exc))
        traceback.print_exc()
        requests.post(response_url, data=json.dumps({'text': str(exc)}), timeout=10000)
    # pylint: enable=broad-except

def dispatch(event, _):
    """Entry point for the initial lambda. Just posts so an SNS topic to invoke
    the lambda that actually does the work. This is annoying, but the
    processing can take more than 3 seconds, which is the response time limit
    for slack."""

    def generate_response(message):
        """Generate a full HTTP JSON response."""
        return {
            'statusCode': str(200),
            'body': json.dumps({'text': message}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    try:
        print(event)
        params = dict(urllib.parse.parse_qsl(base64.b64decode(str(event['body'])).decode('ascii')))
        print(params)
        if 'text' not in params or not params['text']:
            return generate_response('Usage:\n' +
                                     '/dalle prompt')
        prompt = params['text']
        user = params['user_name']
        print('DISPATCH COMMAND: ' + prompt + ' ' + user)

        # Publish an SNS notification to invoke the second-state lambda.
        message = {
            "response_url": params['response_url'],
            "prompt": prompt,
            "user": user
        }
        response = boto3.client('sns').publish(
            TopicArn=os.environ['DALLE_SNS_TOPIC'],
            Message=json.dumps({'default': json.dumps(message)}),
            MessageStructure='json'
        )
        print('SNS PUBLISH: ' + str(response))

        return generate_response(f'Processing prompt "{prompt}"...')
    # pylint: disable=broad-except
    except Exception as exc:
        print('DISPATCH ERROR: ' + str(exc))
        traceback.print_exc()
        return generate_response(str(exc))
    # pylint: enable=broad-except

def main():
    """Process the command given on the command line."""
    image = generate_image(' '.join(sys.argv[1:]))
    print(image)
    uploaded = upload_to_imgur(image)
    print(uploaded)

if __name__ == '__main__':
    main()
