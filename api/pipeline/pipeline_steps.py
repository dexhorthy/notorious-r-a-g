import asyncio
import json
import random

from socketio import AsyncServer
from baml_client.async_client import b
from baml_client.types import FinalAnswer


def parse_question():
    # Logic for parsing question
    pass


async def formulate_response(sio: AsyncServer, question: str) -> str:
    await sio.emit(
        "message", {"state": "agent: formulating response", "icon": "pencil"}
    )

    context = []
    for i in range(5):
        resp = await b.FormulateAnswer(question, context)
        if isinstance(resp, FinalAnswer):
            await sio.emit(
                "message", {"state": "draft answer: " + resp.answer, "icon": "pencil"}
            )
            return resp.answer

        await sio.emit(
            "message",
            {
                "state": f"querying pinecone docs index: {resp.question}",
                "icon": "github",
            },
        )
        await asyncio.sleep(random.randint(1, 3))
        context.append(
            json.dumps(
                [
                    """---
title: Concurrent function calls
slug: docs/calling-baml/concurrent-calls
---


We’ll use `function ClassifyMessage(input: string) -> Category` for our example:

<Accordion title="classify-message.baml">
```baml
enum Category {
    Refund
    CancelOrder
    TechnicalSupport
    AccountIssue
    Question
}

function ClassifyMessage(input: string) -> Category {
  client GPT4o
  prompt #"
    Classify the following INPUT into ONE
    of the following categories:

    INPUT: {{ input }}

    {{ ctx.output_format }}

    Response:
  "#
}
```
</Accordion>

<Tabs>
<Tab title="Python">

You can make concurrent `b.ClassifyMessage()` calls like so:

```python main.py
import asyncio

from baml_client import b
from baml_client.types import Category

async def main():
    await asyncio.gather(
        b.ClassifyMessage("I want to cancel my order"),
        b.ClassifyMessage("I want a refund")
    )

if __name__ == '__main__':
    asyncio.run(main())
```
</Tab>

<Tab title="TypeScript">

You can make concurrent `b.ClassifyMessage()` calls like so:

```ts main.ts
import { b } from './baml_client'
import { Category } from './baml_client/types'
import assert from 'assert'

const main = async () => {
  const category = await Promise.all(
    b.ClassifyMessage('I want to cancel my order'),
    b.ClassifyMessage('I want a refund'),
  )
}

if (require.main === module) {
  main()
}

```
</Tab>

<Tab title="Ruby (beta)">

BAML Ruby (beta) does not currently support async/concurrent calls.

Please [contact us](/contact) if this is something you need.

</Tab>
</Tabs>""",
                    """
---
slug: docs/calling-baml/multi-modal
---


## Multi-modal input

### Images 
Calling a BAML function with an `image` input argument type (see [image types](../snippets/supported-types.mdx)).

The `from_url` and `from_base64` methods create an `Image` object based on input type.
<CodeBlocks>
```python Python
from baml_py import Image
from baml_client import b

async def test_image_input():
  # from URL
  res = await b.TestImageInput(
      img=Image.from_url(
          "https://upload.wikimedia.org/wikipedia/en/4/4d/Shrek_%28character%29.png"
      )
  )

  # Base64 image
  image_b64 = "iVBORw0K...."
  res = await b.TestImageInput(
    img=Image.from_base64("image/png", image_b64)
  )
```

```typescript TypeScript
import { b } from '../baml_client'
import { Image } from "@boundaryml/baml"
...

  // URL
  let res = await b.TestImageInput(
    Image.fromUrl('https://upload.wikimedia.org/wikipedia/en/4/4d/Shrek_%28character%29.png'),
  )

  // Base64
  const image_b64 = "iVB0R..."
  let res = await b.TestImageInput(
    Image.fromBase64('image/png', image_b64),
  )
  
```

```ruby Ruby (beta)
we're working on it!
```

</CodeBlocks>
 
### Audio
Calling functions that have `audio` types. See [audio types](../snippets/supported-types.mdx)

<CodeBlocks>
```python Python
from baml_py import Audio
from baml_client import b

async def run():
  # from URL
  res = await b.TestAudioInput(
      img=Audio.from_url(
          "https://actions.google.com/sounds/v1/emergency/beeper_emergency_call.ogg"
      )
  )

  # Base64
  b64 = "iVBORw0K...."
  res = await b.TestAudioInput(
    audio=Audio.from_base64("audio/ogg", b64)
  )
```

```typescript TypeScript
import { b } from '../baml_client'
import { Audio } from "@boundaryml/baml"
...

  // URL
  let res = await b.TestAudioInput(
    Audio.fromUrl('https://actions.google.com/sounds/v1/emergency/beeper_emergency_call.ogg'),
  )

  // Base64
  const audio_base64 = ".."
  let res = await b.TestAudioInput(
    Audio.fromBase64('audio/ogg', audio_base64),
  )
  
```

```ruby Ruby (beta)
we're working on it!
```
</CodeBlocks>
""",
                ]
            )
        )
        await sio.emit(
            "message",
            {
                "state": "querying pinecode - previous discord messages",
                "icon": "discord",
            },
        )
        await asyncio.sleep(random.randint(1, 3))
        context.append(
            json.dumps(
                [
                    {
                        "text": "Hey what's up 👋, <@740363257814057004>  timelines are a little hard to estimate since I'm still new to the codebase but I think it should take roughly 3 weeks to get a basic working implementation of literals (strings, ints and bools). Rest of the data types remains to be seen.",
                        "metadata": {
                            "message_id": 1290729057520193576,
                            "username": "antoniosarosi",
                            "created_at": "2024-10-01T17:36:27.899000+00:00",
                            "edited_at": None,
                        },
                    },
                    {
                        "text": "understood, i'll follow the thread here",
                        "metadata": {
                            "message_id": 1290736713706242068,
                            "username": "faizansattar",
                            "created_at": "2024-10-01T18:06:53.276000+00:00",
                            "edited_at": None,
                        },
                    },
                    {
                        "text": "<@99252724855496704> maybe it would be helpful for you to share the Sherlock use case with <@622036251863679006> so I can better understand what release will unlock strucutured UI outputs for us",
                        "metadata": {
                            "message_id": 1290736894203662387,
                            "username": "faizansattar",
                            "created_at": "2024-10-01T18:07:36.310000+00:00",
                            "edited_at": None,
                        },
                    },
                    {
                        "text": "FYI as an update, we may be able to get an initial version of this out next week thanks to some great work by <@622036251863679006>",
                        "metadata": {
                            "message_id": 1291795341598785606,
                            "username": "hellovai",
                            "created_at": "2024-10-04T16:13:29.834000+00:00",
                            "edited_at": None,
                        },
                    },
                ]
            )
        )

    return "giving up, no answer found"


def attach_docs_and_sources():
    # Logic for attaching docs and sources
    pass


def review_answer():
    # Logic for reviewing answer
    pass


def get_human_feedback():
    # Logic for getting human feedback
    pass


def mark_as_done():
    # Logic for marking the process as done
    pass


states = [
    attach_docs_and_sources,
    review_answer,
    get_human_feedback,
    mark_as_done,
]


async def run_pipeline(sio, question: str):
    initial_draft = await formulate_response(sio, question)

    for state in states:
        await sio.emit("message", {"state": state.__name__})
        await asyncio.sleep(random.randint(1, 3))

    await sio.emit(
        "final_answer",
        {
            "answer": "The answer to your question '"
            + question
            + "' is: "
            + initial_draft,
        },
    )
    return question
