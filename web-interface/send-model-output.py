"""
Example script to send model output to the web application.

This script demonstrates how to send text output from your model to the web app.
The web app will automatically receive it and trigger translation.

Usage:
    python send-model-output.py "Hello, this is a test message"
    
Or use it in your model script:
    import requests
    import subprocess
    
    # Your model generates output
    model_output = "Hello world"
    
    # Send to web app
    response = requests.post('http://localhost:3000/api/model-output', 
                            json={'text': model_output})
    print(response.json())
"""

import requests
import sys
import json

def send_model_output(text, base_url='http://localhost:3000'):
    """
    Send model output to the web application.
    
    Args:
        text: The text output from your model
        base_url: The base URL of your Next.js application (default: http://localhost:3000)
    """
    url = f'{base_url}/api/model-output'
    payload = {'text': text}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✓ Successfully sent: {text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"✗ Error sending output: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python send-model-output.py <text>")
        print("Example: python send-model-output.py 'Hello, this is a test message'")
        sys.exit(1)
    
    text = ' '.join(sys.argv[1:])
    send_model_output(text)


