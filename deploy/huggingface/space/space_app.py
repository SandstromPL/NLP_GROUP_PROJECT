"""Hugging Face Space entry point: the page of app/demo.py, with the fine-tuned MuRIL tagger loaded from the Hub.

The Space runs this file from the root of its repository, where scripts/publish_hf.py puts it next to `app/` and
`src/`, so the imports below work as they do locally. The model comes from the Space variable MODEL_ID (set by the
publish script); MODEL_REVISION pins a commit or tag of it, and an empty value means the newest version.

Run it locally against the saved model:
    MODEL_ID=models/muril-synfull-s42 PYTHONPATH=. uv run --extra train --extra demo \
        python deploy/huggingface/space/space_app.py
"""
import os

import gradio as gr
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

from app.demo import EXAMPLE, EXAMPLES, _tokens, parse
from src.models.transformer import predict
from src.normalize.gazetteer import Gazetteer

MODEL_ID = os.environ.get("MODEL_ID", "").strip()
REVISION = os.environ.get("MODEL_REVISION", "").strip() or None
if not MODEL_ID:
    raise SystemExit("Set the Space variable MODEL_ID to the model repo, e.g. <user>/muril-indian-address-parser")

tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
net = AutoModelForTokenClassification.from_pretrained(MODEL_ID, revision=REVISION, use_safetensors=True)
net = net.to("cuda" if torch.cuda.is_available() else "cpu")
gaz = Gazetteer.load()


def tagger(text: str) -> list[str]:
    return predict(net, tok, [{"tokens": _tokens(text)}])[0]


def respond(text: str):
    """The same three outputs as app/demo.py: the highlighted parts, the cleaned JSON and the PIN notes."""
    out = parse(text, tagger, gaz)
    notes = "\n".join(f"- {note}" for note in out["notes"])
    return out["spans"], out["json"], notes or "The PIN is in the directory and nothing contradicts it."


gr.Interface(
    fn=respond, inputs=gr.Textbox(label="Address", lines=2, placeholder=EXAMPLE),
    outputs=[gr.HighlightedText(label="Parts"), gr.JSON(label="Cleaned"), gr.Markdown(label="PIN check")],
    examples=EXAMPLES, title="Indian address parser",
    description=("Tags the parts of a messy Indian address and checks it against the India Post PIN directory. "
                 f"Model: {MODEL_ID}. Use addresses of public places; nothing typed here is stored."),
    flagging_mode="never", analytics_enabled=False,  # nothing a visitor types is kept or reported
).launch()
