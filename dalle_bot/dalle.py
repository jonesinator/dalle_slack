"""Generate Dalle images for slack. Designed to run as either a command-line
application or as an AWS Lambda pair."""

import json
import os
import sys
import traceback

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

def validate_prompt(prompt):
    """Validate's a prompt using OpenAI's Moderation API"""
    openai.organization = os.environ['OPENAI_ORGANIZATION']
    openai.api_key = os.environ['OPENAI_API_KEY']
    response = openai.Moderation.create(input=prompt)
    results = response['results'][0]
    return results


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

        # Don't actually validate the prompt because it gives different results than when dalle
        # actually flags.
        # Leave the code in for now in case this changes in the future.
        #
        # print('VALIDATE PROMPT: ' + prompt)
        # validation = validate_prompt(prompt)
        # if validation['flagged']:
        #     requests.post(response_url, data=json.dumps({'text': validation}), timeout=10000)
        #     print('VALIDATION FAILED')
        #     return

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

def main():
    """Process the command given on the command line."""
    prompt = ' '.join(sys.argv[1:])
    # validation = validate_prompt(prompt)
    # print(validation)
    # if validation['flagged']:
    #     print('VALIDATION FAILED')
    #     return
    image = generate_image(prompt)
    print(image)
    uploaded = upload_to_imgur(image)
    print(uploaded)

if __name__ == '__main__':
    main()
