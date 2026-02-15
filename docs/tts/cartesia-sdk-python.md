> ## Documentation Index
> Fetch the complete documentation index at: https://docs.cartesia.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Python

> The official Python library for the Cartesia API.

# Installation

Install the Cartesia Python SDK:

```sh  theme={null}
pip install cartesia
```

# Quickstart: run text-to-speech, save audio, and play it back

```py main.py theme={null}
from cartesia import Cartesia
import os

client = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))

chunk_iter = client.tts.bytes(
	model_id="sonic-3",
	transcript="I can't wait to see what you'll create!",
	voice={
			"mode": "id",
			"id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b",
	},
	output_format={
			"container": "wav",
			"sample_rate": 44100,
			"encoding": "pcm_f32le",
	},
)

with open("sonic.wav", "wb") as f:
	for chunk in chunk_iter:
		f.write(chunk)
```

Then, at the command line, run this script and play the saved audio:

```sh  theme={null}
python main.py
afplay sonic.wav  # macOS ships with afplay
ffplay sonic.wav  # ffplay is ffmpeg's command-line audio player
```

# Github

<Card title="Cartesia Python" icon="github" href="https://github.com/cartesia-ai/cartesia-python">
  The official Python library for the Cartesia API.
</Card>
