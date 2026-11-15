# Indian Address Parser

**Parsing and normalising messy Indian addresses**
Group 10 · DSL504 (Natural Language Processing) · IIT Bhilai · Oct–Nov 2026
Agastya Nath · Paritosh Lahre · Varun Rao · Y. Rahul Dev Reddy
Course instructor: Dr. Soumajit Pramanik

## About this project

People in India rarely write an address in a fixed format. They use landmarks ("behind SBI ATM"), short forms
("b'lore-68"), Hindi words written in English letters ("hanuman mandir ke paas"), any order, and often no commas.
Delivery, banking and emergency services need these addresses as clean, separate fields.

This project builds a tool that splits such an address into its parts and checks them against the India Post PIN
directory. It also asks a research question: **models trained on computer-generated (synthetic) addresses do very well
on more synthetic addresses, but how much worse are they on addresses that people actually write?**

## What it does

Give it an address, and it:

1. **tags every word** with one of nine fields: HOUSE, BUILDING, STREET, LANDMARK, LOCALITY, CITY, DISTRICT, STATE
   and PIN;
2. **cleans the fields**: it expands short forms (`apts` → `Apartments`, `b'lore` → `Bangalore`) and splits each
   landmark into a relation (`behind`) and a place (`SBI atm`);
3. **checks the PIN** against the India Post directory (157,126 post offices, 19,300 PINs): whether it exists, whether
   it matches the written state and district, and which district and state it belongs to when the address leaves
   them out.

A small web page (`app/demo.py`) shows all three. The main model is
[MuRIL](https://huggingface.co/google/muril-base-cased), a BERT model made for Indian languages, which we fine-tuned on
our data. A rules baseline and a CRF can be used instead.

## How the model was trained

Everything below comes from `logs.md` and the files in `results/`.

- **Training data:** 20,000 synthetic addresses from our generator (`src/generate/`). It fills address templates with
  real places from the India Post PIN directory, then adds eight kinds of "noise" that people make: short forms (N1),
  landmark phrases including Hinglish (N2), dropped and reordered fields (N3), odd separators and letter case (N4),
  typos (N5), spelling variants (N6), PIN variants (N7) and Indian house-number formats (N8). The PINs are split
  90/5/5 between train, dev and test, so dev and test addresses use PINs the model never saw. Data seed 42.
- **Model:** `google/muril-base-cased`, fine-tuned for token classification. The first sub-word piece of each word
  carries the word's tag.
- **Settings:** 3 epochs, learning rate 1e-4, batch size 32, warm-up over the first 10 % of steps, weight decay 0.01,
  gradient clipping 1.0, bf16 mixed precision, at most 256 sub-words per address, seed 42.
- **How the settings were chosen (11 Nov):** five MuRIL runs, scored on synthetic dev. The rule, set before the runs,
  was "the cheapest setting within 0.002 F1 of the best" (0.9903 against 0.9910). Mixed precision gave the same score
  as full precision and trained 1.7 times faster (314 s against 532 s).
- **The saved model (16 Nov):** trained in 357 s on an RTX 4060 Laptop GPU (8 GB); average loss per epoch 1.476,
  0.138 and 0.053. It is on Hugging Face as
  [`sandstromPL/muril-indian-address-parser`](https://huggingface.co/sandstromPL/muril-indian-address-parser) (tag
  `v1`). Run on a second machine, it gives exactly the committed predictions, token for token.

The training command:

```bash
uv run python -m src.models.transformer --model muril --train data/synthetic/full/train.jsonl --seed 42 \
    --eval data/synthetic/full/dev.jsonl tests/fixtures/handlabelled20.jsonl \
    --run-id 20261116-muril-synfull-dev-s42 20261116-muril-synfull-hand20-s42 \
    --save-dir models/muril-synfull-s42
```

## Results

**F1** is a score from 0 to 1 that combines precision (how many of the parts the model tagged are right) and recall
(how many of the true parts it found). A part counts as right only if both its words and its label are exactly right
(span F1, computed with `seqeval`). The numbers in brackets are 95 % confidence intervals.

| System | Synthetic dev (2,000 addresses) | 20 hand-written addresses ("hand20") |
|---|---|---|
| Rules + PIN directory (no training) | – | 0.828 (0.745–0.897) |
| CRF | 0.992 (0.990–0.993) | 0.796 (0.708–0.889) |
| XLM-R, fine-tuned | 0.991 (0.989–0.993) | 0.759 (0.677–0.840) |
| **MuRIL, fine-tuned (the demo model)** | **0.991 (0.989–0.992)** | **0.741 (0.645–0.830)** |

Existing open-source Indian address parsers on the same 20 addresses, used as they are:

| System | Score on hand20 |
|---|---|
| Shiprocket IndicBERT | 0.588 span F1 |
| Shiprocket TinyBERT | 0.469 span F1 |
| mukuls9971 MuRIL NER | 0.418 span F1 |
| gagan1985 TinyBERT | 0.386 span F1 |
| abr-6024 parser (1.5B, answers in JSON) | 0.645 field F1 |
| Qwen2.5-1.5B with 5 examples in the prompt | 0.484 field F1 |
| Qwen2.5-1.5B with no examples | 0.288 field F1 |

What this shows:

- **The gap:** every trained model is almost perfect on synthetic addresses, but loses 0.20 to 0.25 F1 on hand-written
  ones. On those, the simple rules score best, though the intervals overlap.
- **Against existing parsers:** compared on the same labels, each of our four systems beats each existing parser, and
  all 28 paired-bootstrap intervals are above zero (`report/tables/shared.md`).
- **Hardest field:** among the fields that appear often, LOCALITY is the hardest (0.588 for MuRIL on hand20). The PIN
  is the easiest (1.000).
- **Big caveat:** hand20 has only 20 addresses, written by the team and used while building the system. A real test
  set of about 500 human-written addresses was planned (`initials.md` §5.3) but not collected before the deadline, so
  the research questions are still open.

The full results, with the run behind every number, are in `report/report.pdf`, `report/report.md` and
`report/tables/`.

## Examples

Real output of the MuRIL model and the PIN check, as the web page shows it.

**1. A flat near two landmarks**

    flat 3b, shanti apts, behind SBI atm nr hanuman mandir, supela bhilai 490023

Parts found: BUILDING `shanti apts` · LANDMARK `behind SBI atm` · LANDMARK `nr hanuman mandir` · LOCALITY
`supela bhilai` · PIN `490023`

```json
{"house": null, "building": "Shanti Apartments", "street": null,
 "landmarks": [{"relation": "behind", "anchor": "SBI atm"}, {"relation": "near", "anchor": "Hanuman Mandir"}],
 "locality": "Supela Bhilai", "city": null, "district": "Durg", "state": "Chhattisgarh",
 "pin": "490023", "pin_check": "valid", "filled": ["district", "state"], "locality_known": true}
```

PIN check: *District and state filled in from the PIN: Durg, Chhattisgarh.*
Mistakes: it misses the house `flat 3b`, and it reads `supela bhilai` as one locality, so the city is empty (it should
be locality Supela, city Bhilai).

**2. Bengaluru, with a short-form city and PIN**

    opp. ganesh temple, 2nd cross, hosur road, madivala, b'lore-68

Parts found: STREET `2nd cross` · STREET `hosur road` · LOCALITY `madivala` · CITY `b'lore` · PIN `68`

```json
{"house": null, "building": null, "street": "2nd Cross, Hosur Road", "landmarks": [],
 "locality": "Madivala", "city": "Bangalore", "district": null, "state": null,
 "pin": "68", "pin_check": "not_found", "filled": [], "locality_known": null}
```

PIN check: *PIN 68 is not in the India Post directory.*
`b'lore` is expanded to Bangalore. Mistake: it misses the landmark `opp. ganesh temple`. `68` is only the end of a PIN,
so the directory cannot check it.

**3. A PIN that does not exist**

    Shop 4, MG Road, Pune 999999

Parts found: STREET `MG Road` · CITY `Pune` · PIN `999999`

```json
{"house": null, "building": null, "street": "MG Road", "landmarks": [],
 "locality": null, "city": "Pune", "district": null, "state": null,
 "pin": "999999", "pin_check": "not_found", "filled": [], "locality_known": null}
```

PIN check: *PIN 999999 is not in the India Post directory.* The check catches the fake PIN. Mistake: it misses the
house `Shop 4`.

## Try it on your own addresses

You need Python 3.12 and [uv](https://docs.astral.sh/uv/). A GPU is not needed to run the model. Without uv,
`pip install -r requirements.txt` installs the same versions, and you can then drop `uv run` from the commands below.

```bash
git clone https://github.com/devreddy1015/NLP_GROUP_PROJECT.git
cd NLP_GROUP_PROJECT
uv sync --extra train --extra demo
```

**The web page.** Start it, open http://127.0.0.1:7860, and type an address or click an example:

```bash
uv run python -m app.demo --model sandstromPL/muril-indian-address-parser
```

The first start downloads the model from Hugging Face (about 950 MB). If you already have the model folder (for
example from the zip), pass the folder instead: `--model models/muril-synfull-s42`. Without the model,
`--model crf` trains a CRF at start-up (about a minute) and `--model rules` starts at once.

**From Python.** Save this as `my_test.py` in the repository folder and run `uv run python my_test.py`:

```python
from app.demo import parse, transformer_tagger
from src.normalize.gazetteer import Gazetteer

tagger = transformer_tagger("sandstromPL/muril-indian-address-parser")  # or "models/muril-synfull-s42"
gaz = Gazetteer.load()
out = parse("flat 3b, shanti apts, behind SBI atm nr hanuman mandir, supela bhilai 490023", tagger, gaz)
print([(piece, label) for piece, label in out["spans"] if label])  # the tagged parts
print(out["json"])   # the cleaned fields and the PIN check
print(out["notes"])  # what the PIN directory says
```

Use addresses of public places (shops, temples, schools, offices). Nothing you type is stored.

**The tests:** `uv run pytest` (245 tests).

## Other commands

```bash
uv run python -m src.generate --config full --seed 42      # make the synthetic data
scripts/run_experiments.sh --dry-run                       # list the planned experiment runs
uv run python -m scripts.make_tables                       # rebuild report/tables/ from results/
uv run python -m scripts.publish_hf --dry-run              # what would be uploaded to Hugging Face
```

## Where things are

| Path | Contents |
|---|---|
| `src/` | generator, models (rules, CRF, MuRIL / XLM-R, existing parsers, LLM), normaliser, evaluation |
| `app/demo.py` | the web page |
| `tests/` | tests, and the 20 hand-written addresses (`tests/fixtures/handlabelled20.jsonl`) |
| `results/`, `report/tables/` | one file per run, and the tables built from them |
| `report/` | the report: `report.pdf`, its LaTeX source `report.tex`, and `report.md` |
| `deploy/huggingface/`, `scripts/publish_hf.py` | the Hugging Face model card and upload script |
| `initials.md`, `build-plan.md`, `logs.md` | the plan, the build order, and the work log |
| `research.md`, `resources.md` | prior work, and every external link with its licence |

## Rules

1. **Privacy:** addresses of public places only. No home addresses, names or phone numbers.
2. **Frozen test set:** never train, tune or adjust prompts on the real test set.
3. **Real numbers only:** every reported number comes from a file in `results/`.

## Data and licences

Contains data from India Post: the All India Pincode Directory (data.gov.in), under the Government Open Data Licence –
India (GODL-India). MuRIL is Apache-2.0, and so is our fine-tuned model.
