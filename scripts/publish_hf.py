"""Publish the demo on Hugging Face: the saved MuRIL model as a model repo, and the demo page as a Space that loads it.

    uv run hf auth login                                  # once per machine: paste a token with write access
    uv run python -m scripts.publish_hf --dry-run         # list what would be uploaded; uploads nothing
    uv run python -m scripts.publish_hf --tag v1          # first time: the model repo, then the Space
    uv run python -m scripts.publish_hf --model-only --model-dir models/<new-folder> --tag v2 --message "<what changed>"
                                                          # a new model version; the Space restarts on it
    uv run python -m scripts.publish_hf --space-only      # new demo code; the Space rebuilds
    uv run python -m scripts.publish_hf --card-only --message "<what changed>"   # the model card alone, after editing it

Both repos are public. Every upload is a new commit, so older model versions stay in the model repo's history. The
Space loads the newest version when it starts; to pin one, set the Space variable MODEL_REVISION to its tag or commit.
The model card (deploy/huggingface/model/README.md) is uploaded with every model: update its results first.
A model repo is free. A Gradio Space needs a PRO account: on 16 Nov 2026 Hugging Face refused it on a free account
(402: only static Spaces are free).
"""
import argparse
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi
from huggingface_hub.errors import HfHubHTTPError

MODEL_FILES = ("config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json")
CARDS = Path("deploy/huggingface")


def space_files() -> list[tuple[str, Path]]:
    """(path in the Space, local file): the demo's code, the cleaned PIN directory and the Space's own files."""
    files = [(p.as_posix(), p) for p in sorted(Path("src").rglob("*.py"))]
    files += [("app/demo.py", Path("app/demo.py")), ("data/gazetteer/pincodes.csv", Path("data/gazetteer/pincodes.csv"))]
    return files + [(name, CARDS / "space" / name) for name in ("space_app.py", "requirements.txt")]


def card(path: Path, model_repo: str, space_repo: str) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("{{MODEL_REPO}}", model_repo).replace("{{SPACE_REPO}}", space_repo).encode("utf-8")


def show(title: str, ops: list[CommitOperationAdd]) -> None:
    print(f"{title}: {len(ops)} files, {sum(op.upload_info.size for op in ops) / 1e6:.1f} MB")
    for op in ops:
        print(f"  {op.path_in_repo} ({op.upload_info.size / 1e6:.2f} MB)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model-dir", type=Path, default=Path("models/muril-synfull-s42"))
    p.add_argument("--model-name", default="muril-indian-address-parser")
    p.add_argument("--space-name", default="indian-address-parser")
    only = p.add_mutually_exclusive_group()
    only.add_argument("--model-only", action="store_true", help="upload a new model version and restart the Space")
    only.add_argument("--space-only", action="store_true", help="upload the demo code only")
    only.add_argument("--card-only", action="store_true", help="upload the model card alone, after editing its text")
    p.add_argument("--tag", default=None, help="tag the model commit (e.g. v1) so the Space can pin it")
    p.add_argument("--message", default=None, help="commit message")
    p.add_argument("--dry-run", action="store_true", help="list what would be uploaded; needs no login")
    a = p.parse_args()

    api = HfApi()
    user = "<your-username>" if a.dry_run else api.whoami()["name"]
    model_repo, space_repo = f"{user}/{a.model_name}", f"{user}/{a.space_name}"
    model_ops: list[CommitOperationAdd] = []
    space_ops: list[CommitOperationAdd] = []
    if not a.space_only:
        if not a.card_only:
            missing = [name for name in MODEL_FILES if not (a.model_dir / name).exists()]
            if missing:
                raise SystemExit(f"{a.model_dir} lacks {missing}: unzip the model there, or save one with --save-dir")
            model_ops = [CommitOperationAdd(name, a.model_dir / name) for name in MODEL_FILES]
        model_ops.append(CommitOperationAdd("README.md", card(CARDS / "model" / "README.md", model_repo, space_repo)))
    if not (a.model_only or a.card_only):
        space_ops = [CommitOperationAdd(repo_path, local) for repo_path, local in space_files()]
        space_ops.append(CommitOperationAdd("README.md", card(CARDS / "space" / "README.md", model_repo, space_repo)))
    if a.dry_run:
        for title, ops in ((f"model repo {model_repo}", model_ops), (f"Space {space_repo}", space_ops)):
            if ops:
                show(title, ops)
        return

    if model_ops:
        api.create_repo(model_repo, repo_type="model", exist_ok=True)
        default = "Model card" if a.card_only else f"Model from {a.model_dir}"
        commit = api.create_commit(model_repo, model_ops, commit_message=a.message or default)
        if a.tag:
            api.create_tag(model_repo, tag=a.tag, revision=commit.oid)
        print(f"model: https://huggingface.co/{model_repo} (commit {commit.oid[:7]}{', tag ' + a.tag if a.tag else ''})")
    if space_ops:
        try:
            api.create_repo(space_repo, repo_type="space", space_sdk="gradio", exist_ok=True)
        except HfHubHTTPError as e:
            if getattr(e.response, "status_code", None) != 402:
                raise
            raise SystemExit(f"The Space was not created: {e.server_message or e}\nHugging Face hosts Gradio Spaces "
                             "only for PRO accounts. Anything uploaded above stands; after subscribing, run this again "
                             "with --space-only.") from None
        api.add_space_variable(space_repo, "MODEL_ID", model_repo, description="the model repo this Space loads")
        commit = api.create_commit(space_repo, space_ops, repo_type="space", commit_message=a.message or "Demo code")
        print(f"space: https://huggingface.co/spaces/{space_repo} (commit {commit.oid[:7]}); it builds in a few minutes")
    elif model_ops and not a.card_only:  # new weights alone: restart the Space so that it loads them
        try:
            api.restart_space(space_repo)
            print(f"restarted https://huggingface.co/spaces/{space_repo}; it loads the new model in a minute or two")
        except Exception as e:  # e.g. the Space does not exist yet: the model upload still stands
            print(f"the model is uploaded, but the Space was not restarted ({e}); restart it from its Settings page")


if __name__ == "__main__":
    main()
