---
license: apache-2.0
base_model: google/muril-base-cased
pipeline_tag: token-classification
language:
  - en
tags:
  - address-parsing
  - india
  - token-classification
---

# MuRIL Indian address tagger

Tags each token of a messy Indian address with one of nine fields: HOUSE, BUILDING, STREET, LANDMARK, LOCALITY, CITY,
DISTRICT, STATE and PIN, in BIO (IOB2) form (19 tags). `google/muril-base-cased` fine-tuned for token classification.

    flat 3b, shanti apts, behind SBI atm nr hanuman mandir, supela bhilai 490023

A course project for DSL504 / DS504 Natural Language Processing, IIT Bhilai, 2026.
Code, report and a demo you run locally (`app/demo.py`): https://github.com/devreddy1015/NLP_GROUP_PROJECT

## Training
- **Base model:** `google/muril-base-cased` at commit `afd9f36`.
- **Data:** 20,000 synthetic addresses from the project's generator (config `full`: all eight noise families, i.e.
  abbreviations, landmark phrases, reordering and dropped fields, delimiters and case, typos, spelling variants, PIN
  variants and Indian number formats), built on real geography from the India Post PIN directory. Data seed 42.
- **Settings:** 3 epochs, learning rate 1e-4, batch 32, linear warm-up over 10 % of steps, weight decay 0.01, gradient
  clipping 1.0, bf16 mixed precision, maximum length 256, seed 42. The first subword of each token carries its tag.
  357 s on an RTX 4060 Laptop GPU.

## Results
Span micro F1 (`seqeval`, strict IOB2) with a 95 % bootstrap interval over addresses:

| Scored on | Span micro F1 | Exact match |
|---|---|---|
| Synthetic dev (2,000 addresses with held-out PINs) | 0.991 (0.989–0.992) | 0.946 |
| 20 hand-written public-place addresses (a smoke set written by the team, not a held-out test set) | 0.741 (0.645–0.830) | 0.350 |

A human-written test set was designed but not collected, so there is no score on real data yet. On the 20
hand-written addresses a rules baseline scores 0.828 and a CRF 0.796.

## Use
Split the address the way the model was trained (whitespace, and every punctuation or symbol character on its own),
then read the tag of each word's first subword:

```python
import unicodedata

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

repo = "{{MODEL_REPO}}"
tok = AutoTokenizer.from_pretrained(repo)
net = AutoModelForTokenClassification.from_pretrained(repo).eval()


def words(text):
    """Split on whitespace; every punctuation or symbol character is its own token."""
    out, cur = [], ""
    for ch in text:
        if ch.isspace() or unicodedata.category(ch)[0] in "PS":
            if cur:
                out.append(cur)
                cur = ""
            if not ch.isspace():
                out.append(ch)
        else:
            cur += ch
    return out + ([cur] if cur else [])


text = "flat 3b, shanti apts, behind SBI atm nr hanuman mandir, supela bhilai 490023"
tokens = words(text)
enc = tok(tokens, is_split_into_words=True, return_tensors="pt")
with torch.no_grad():
    best = net(**enc).logits.argmax(-1)[0].tolist()
tags, seen = ["O"] * len(tokens), set()
for pos, w in enumerate(enc.word_ids()):
    if w is not None and w not in seen:  # the first subword of each word carries its tag
        seen.add(w)
        tags[w] = net.config.id2label[best[pos]]
print(list(zip(tokens, tags)))
```

## Limitations
- Trained on synthetic addresses only. On hand-written text it confuses city and locality (`Bhilai` tagged as a
  locality), reads floors (`Ground Floor`) as streets, and misses landmarks without an English relation word
  (`hanuman mandir ke paas`).
- Roman script and Hinglish; no Devanagari in training.
- The place's own name (`Shree Sweets`) is tagged `O` by design.
- Meant for addresses of public places. Do not use it on personal data without checking it on your own data first.

## Licence and data
Apache-2.0, the licence of the base model. The training addresses are synthetic, built from the India Post All India
Pincode Directory (data.gov.in), under the Government Open Data Licence – India (GODL-India): contains data from
India Post.
