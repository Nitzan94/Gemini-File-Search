# Setup & Installation

Get started with Gemini File Search in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- A Google API key ([Get one here](https://aistudio.google.com/apikey))

## Installation

### Option 1: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
uv init gemini-search
cd gemini-search

# Add dependencies
uv add fastapi uvicorn google-genai python-multipart python-dotenv jinja2
```

### Option 2: Using pip

```bash
pip install fastapi uvicorn google-genai python-multipart python-dotenv jinja2
```

## Get Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **"Get API Key"**
3. Create or select a project
4. Copy your API key

:::warning Security
Never commit your API key to version control. Always use environment variables.
:::

## Configure Environment

Create a `.env` file in your project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

## Test Your Connection

Create a simple test script:

```python
# test_connection.py
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Test: List stores
try:
    stores = client.file_search_stores.list(config={'page_size': 5})
    print('[OK] Connected successfully!')
    print(f'Found {len(list(stores))} stores')
except Exception as e:
    print(f'[ERROR] Connection failed: {e}')
```

Run the test:

```bash
python test_connection.py
```

Expected output:
```
[OK] Connected successfully!
Found 0 stores
```

## Common Setup Issues

### Issue: "GEMINI_API_KEY not found"

**Solution**: Make sure your `.env` file is in the correct directory and you're calling `load_dotenv()` before accessing the client.

### Issue: "Invalid API key"

**Solutions**:
1. Check for typos in your API key
2. Ensure the key is active in [AI Studio](https://aistudio.google.com/apikey)
3. Try generating a new key

### Issue: "Module 'google.genai' not found"

**Solution**: Install the SDK:
```bash
pip install google-genai
```

## Next Steps

Now that you're set up, let's create your first file search store:

- [Create Your First Store →](/en/getting-started/first-store)
- [Run Your First Query →](/en/getting-started/first-query)
- [Understand the Architecture →](/en/concepts/architecture)

## Full Example

Here's a complete working example you can copy and run:

```python
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Setup
load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Create store
store = client.file_search_stores.create(
    config={'display_name': 'Test Store'}
)
print(f'Created store: {store.name}')

# Upload file (you'll need to create test.txt)
with open('test.txt', 'w') as f:
    f.write('The company revenue for Q2 2024 was $50 million.')

operation = client.file_search_stores.upload_to_file_search_store(
    file='test.txt',
    file_search_store_name=store.name,
    config={'display_name': 'Test Document'}
)

# Wait for processing
import time
while not operation.done:
    operation = client.operations.get(name=operation.name)
    print('Processing...')
    time.sleep(2)

print('Upload complete!')

# Query
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What was the Q2 revenue?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        )]
    )
)

print(f'Answer: {response.text}')

# Cleanup
client.file_search_stores.delete(
    name=store.name,
    config={'force': True}
)
print('Cleaned up!')
```

Copy this script, save it, and run it to see the complete workflow in action!
