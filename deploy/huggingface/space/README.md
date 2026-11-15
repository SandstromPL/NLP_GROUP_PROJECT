---
title: Indian Address Parser
emoji: 📮
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 6.31.0
python_version: "3.12"
app_file: space_app.py
pinned: false
models:
  - {{MODEL_REPO}}
short_description: Tag and normalise messy Indian addresses
---

# Indian address parser

Type an Indian address and get its parts (house, building, street, landmark, locality, city, district, state, PIN),
a cleaned JSON version, and what the India Post PIN directory says about it: a missing or unknown PIN, a PIN that
contradicts the written state or district, and the fields filled in from the PIN.

- **Model:** [{{MODEL_REPO}}](https://huggingface.co/{{MODEL_REPO}}), MuRIL fine-tuned on 20,000 synthetic addresses.
  It was trained on synthetic data only and makes mistakes on real, hand-written addresses; the model card lists them.
- **Use addresses of public places** (shops, temples, schools, hospitals, offices). Nothing typed here is stored.

A course project for DSL504 / DS504 Natural Language Processing, IIT Bhilai, 2026.
Code: https://github.com/devreddy1015/NLP_GROUP_PROJECT

Contains data from India Post: the All India Pincode Directory (data.gov.in), under the Government Open Data
Licence – India (GODL-India).
