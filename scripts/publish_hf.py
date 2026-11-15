"""Publish the saved MuRIL model on Hugging Face as a model repo, with its card.

    uv run hf auth login                                  # once per machine: paste a token with write access
    uv run python -m scripts.publish_hf --dry-run         # list what would be uploaded; uploads nothing
    uv run python -m scripts.publish_hf --tag v1          # the model and its card
    uv run python -m scripts.publish_hf --model-dir models/<new-folder> --tag v2 --message "<what changed>"
                                                          # a new model version
    uv run python -m scripts.publish_hf --card-only --message "<what changed>"   # the card alone, after editing it

The repo is public. Every upload is a new commit, so older versions stay in its history; a tag (v1, v2, ...) names a
version, and `from_pretrained(<repo>, revision="v1")` loads that one. The card (deploy/huggingface/model/README.md) is
uploaded with every model: update its results first.
"""
import argparse
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi

MODEL_FILES = ("config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json")
CARD = Path("deploy/huggingface/model/README.md")


def card(repo: str) -> bytes:
    return CARD.read_text(encoding="utf-8").replace("{{MODEL_REPO}}", repo).encode("utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model-dir", type=Path, default=Path("models/muril-synfull-s42"))
    p.add_argument("--model-name", default="muril-indian-address-parser")
    p.add_argument("--card-only", action="store_true", help="upload the card alone, after editing its text")
    p.add_argument("--tag", default=None, help="tag this upload (e.g. v2) so it can be loaded by name")
    p.add_argument("--message", default=None, help="commit message")
    p.add_argument("--dry-run", action="store_true", help="list what would be uploaded; needs no login")
    a = p.parse_args()

    api = HfApi()
    repo = f"{'<your-username>' if a.dry_run else api.whoami()['name']}/{a.model_name}"
    ops: list[CommitOperationAdd] = []
    if not a.card_only:
        missing = [name for name in MODEL_FILES if not (a.model_dir / name).exists()]
        if missing:
            raise SystemExit(f"{a.model_dir} lacks {missing}: unzip the model there, or save one with --save-dir")
        ops = [CommitOperationAdd(name, a.model_dir / name) for name in MODEL_FILES]
    ops.append(CommitOperationAdd("README.md", card(repo)))
    if a.dry_run:
        print(f"model repo {repo}: {len(ops)} files, {sum(op.upload_info.size for op in ops) / 1e6:.1f} MB")
        for op in ops:
            print(f"  {op.path_in_repo} ({op.upload_info.size / 1e6:.2f} MB)")
        return

    api.create_repo(repo, repo_type="model", exist_ok=True)
    default = "Model card" if a.card_only else f"Model from {a.model_dir}"
    commit = api.create_commit(repo, ops, commit_message=a.message or default)
    if a.tag:
        api.create_tag(repo, tag=a.tag, revision=commit.oid)
    print(f"model: https://huggingface.co/{repo} (commit {commit.oid[:7]}{', tag ' + a.tag if a.tag else ''})")


if __name__ == "__main__":
    main()
