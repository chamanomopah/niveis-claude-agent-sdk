> ## Documentation Index
> Fetch the complete documentation index at: https://docs.cartesia.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Sonic 3

`sonic-3` is our latest streaming TTS model, with high naturalness, accurate transcript following, and industry-leading latency. It provides fine-grained control on volume, speed, and emotion.

Key Features:

* **42 languages** supported
* **Volume, speed, and emotion** controls, supported through API parameters and SSML tags
* **Laughter** through `[laughter]` tags

For more information, see [Volume, Speed, and Emotion](/build-with-cartesia/sonic-3/volume-speed-emotion).

### Voice selection

Choosing voices that work best for your use case is key to getting the best performance out of Sonic 3.

* **For voice agents**: We've found stable, realistic voices work better for voice agents than studio, emotive voices. Example American English voices include Katie (ID: `f786b574-daa5-4673-aa0c-cbe3e8534c02`) and Kiefer (ID: `228fca29-3a0a-435c-8728-5cb483251068`).
* **For expressive characters**: We've tagged our most expressive and emotive voices with the `Emotive` tag.  Example American English voices include Tessa (ID: `6ccbfb76-1fc6-48f7-b71d-91ac6298247b`) and Kyle (ID: `c961b81c-a935-4c17-bfb3-ba2239de8c2f`).

For more information and recommendations, see [Choosing a Voice](/build-with-cartesia/capability-guides/choosing-a-voice).

### Language support

Sonic-3 supports the following languages:

| English (`en`)    | French (`fr`)    | German (`de`)     | Spanish (`es`)    |
| ----------------- | ---------------- | ----------------- | ----------------- |
| Portuguese (`pt`) | Chinese (`zh`)   | Japanese (`ja`)   | Hindi (`hi`)      |
| Italian (`it`)    | Korean (`ko`)    | Dutch (`nl`)      | Polish (`pl`)     |
| Russian (`ru`)    | Swedish (`sv`)   | Turkish (`tr`)    | Tagalog (`tl`)    |
| Bulgarian (`bg`)  | Romanian (`ro`)  | Arabic (`ar`)     | Czech (`cs`)      |
| Greek (`el`)      | Finnish (`fi`)   | Croatian (`hr`)   | Malay (`ms`)      |
| Slovak (`sk`)     | Danish (`da`)    | Tamil (`ta`)      | Ukrainian (`uk`)  |
| Hungarian (`hu`)  | Norwegian (`no`) | Vietnamese (`vi`) | Bengali (`bn`)    |
| Thai (`th`)       | Hebrew (`he`)    | Georgian (`ka`)   | Indonesian (`id`) |
| Telugu (`te`)     | Gujarati (`gu`)  | Kannada (`kn`)    | Malayalam (`ml`)  |
| Marathi (`mr`)    | Punjabi (`pa`)   |                   |                   |

## Selecting a Model

| Snapshot                                                                                 | Release Date     | Languages                                                                                                                                                              | Status |
| ---------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| <Icon icon="circle" iconType="solid" color="#008000" size="10px" /> `sonic-3-2026-01-12` | January 12, 2026 | en, de, es, fr, ja, pt, zh, hi, ko, it, nl, pl, ru, sv, tr, tl, bg, ro, ar, cs, el, fi, hr, ms, sk, da, ta, uk, hu, no, vi, bn, th, he, ka, id, te, gu, kn, ml, mr, pa | Stable |
| <Icon icon="circle" iconType="solid" color="#008000" size="10px" /> `sonic-3-2025-10-27` | October 27, 2025 | en, de, es, fr, ja, pt, zh, hi, ko, it, nl, pl, ru, sv, tr, tl, bg, ro, ar, cs, el, fi, hr, ms, sk, da, ta, uk, hu, no, vi, bn, th, he, ka, id, te, gu, kn, ml, mr, pa | Stable |

When making API calls, you can specify either:

```javascript lines theme={null}
// Use the base model (automatically routes to the latest snapshot)
const modelId = "sonic-3";

// Or specify a particular snapshot for consistency
const modelId = "sonic-3-2026-01-12";

// Use the latest (beta) model (can be 'hot swapped')
const modelId = "sonic-3-latest";
```

### Continuous updates and model snapshots

All models have a base model name (e.g. `sonic-3`) and a dated snapshot (e.g. `sonic-3-2025-10-27`). Using the base model will automatically keep you up to date with the most recent stable snapshot of that model. If pinning a specific version is important for your use case, we recommend using the dated version.

For testing our latest capabilities, we recommend using `sonic-3-latest`, which is a non-snapshotted version. `sonic-3-latest` can be updated with no notice, and not recommended for production.

To summarize:

| **Model ID**         | Model update behavior                                       | Recommended for                                                                            |
| -------------------- | :---------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `sonic-3-YYYY-MM-DD` | Snapshotted, will never change                              | Customers who want to run internal evals before any updates                                |
| `sonic-3`            | Will be updated to point to the most recent stable snapshot | Customers who want stable releases, but want to be up-to-date with the recent capabilities |
| `sonic-3-latest`     | Will always be updated to our latest beta releases          | Testing purposes                                                                           |

## Older Models

For information on `sonic-2`, `sonic-turbo`, `sonic-multilingual`, and `sonic`, see our page on [Older Models](/build-with-cartesia/tts-models/older-models).
