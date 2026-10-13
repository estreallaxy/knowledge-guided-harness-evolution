import json

import pytest

from llm_discussion import cli
from llm_discussion.storage import read_manifest, read_results
from llm_discussion.types import Completion, ModelError


@pytest.fixture(autouse=True)
def isolate_credentials(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(cli, "load_dotenv", lambda *args, **kwargs: None)


@pytest.fixture
def dataset(tmp_path):
    path = tmp_path / "tasks.jsonl"
    path.write_text("\n".join(json.dumps({
        "id": f"task-{i}", "question": f"Test question {i}?", "reference": "991837",
    }) for i in range(2)) + "\n")
    return path


@pytest.fixture
def model_config(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "discussion": {"rounds": 3, "concurrency": 2},
        "model": {"model": "vendor/default", "temperature": 0.25},
        "agent_models": {"B": {"model": "vendor/alternate"}, "E": {"model": "vendor/alternate"}},
        "secretary_model": {"model": "vendor/secretary"},
    }))
    return path


@pytest.fixture
def fake_openrouter(monkeypatch):
    class FakeOpenRouter:
        created = []
        calls = []
        dotenv_reads = []
        fail = False

        def __init__(self, config, *, client=None):
            self.config = config
            self.name = config.model
            self.client = client
            self.created.append(self)

        async def generate(self, request):
            self.calls.append((self.config.model, request))
            if self.fail and request.agent_id == "B":
                raise ModelError("test provider failure")
            value = "2" if request.agent_id in "DEF" else "1"
            return Completion(json.dumps({"reasons": "test response", "answer": value}),
                              model=self.config.model, provider="test-provider",
                              usage={"prompt_tokens": 10}, generation_id="test-generation")

    monkeypatch.setattr(cli, "OpenRouterModel", FakeOpenRouter)
    monkeypatch.setattr(cli, "load_dotenv", lambda *args, **kwargs: FakeOpenRouter.dotenv_reads.append((args, kwargs)))
    return FakeOpenRouter


def test_default_run_needs_no_key_and_synthetic_score_hidden(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(cli, "load_dotenv", lambda *args, **kwargs: pytest.fail("dry run read .env"))
    output = tmp_path / "run"
    assert cli.main(["run", "--output", str(output)]) == 0
    result = read_results(output)["question-0"]
    assert result["status"] == "completed"
    assert result["reference"] is None
    assert len(result["calls"]) == 18
    capsys.readouterr()
    assert cli.main(["evaluate", str(output)]) == 0
    score = json.loads(capsys.readouterr().out)
    assert score["synthetic"] is True
    assert score["accuracy"] is None


def test_dry_override_never_creates_provider(model_config, dataset, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("dry run created a provider")

    monkeypatch.setattr(cli, "OpenRouterModel", forbidden)
    monkeypatch.setattr(cli, "load_dotenv", forbidden)
    output = tmp_path / "run"
    assert cli.main(["run", "--config", str(model_config), "--dataset", str(dataset),
                     "--dry-run", "--scenario", "tie", "--output", str(output)]) == 0
    result = read_results(output)["task-0"]
    assert result["votes"] == {"1": 3, "2": 3}
    assert result["used_secretary"]
    assert len(result["calls"]) == 19
    assert "991837" not in json.dumps([c["request"] for c in result["calls"]])


def test_live_routes_all_agents_and_secretary(model_config, dataset, fake_openrouter, tmp_path, monkeypatch):
    secret = "fixture-secret-must-not-be-serialized"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)
    output = tmp_path / "run"
    args = ["run", "--config", str(model_config), "--dataset", str(dataset), "--output", str(output)]
    assert cli.main(args) == 0
    assert len(fake_openrouter.created) == 3
    assert fake_openrouter.dotenv_reads == [((".env",), {"override": False})]
    assert len({id(model.client) for model in fake_openrouter.created}) == 1
    assert fake_openrouter.created[0].client.is_closed
    routes = {request.agent_id: model for model, request in fake_openrouter.calls}
    assert routes == {"A": "vendor/default", "B": "vendor/alternate", "C": "vendor/default",
                      "D": "vendor/default", "E": "vendor/alternate", "F": "vendor/default",
                      "G": "vendor/secretary"}
    result = read_results(output)["task-0"]
    assert result["calls"][-1]["completion"]["model"] == "vendor/secretary"
    assert result["calls"][-1]["completion"]["usage"] == {"prompt_tokens": 10}
    manifest = read_manifest(output)
    assert not manifest["synthetic"]
    assert len(manifest["config_sha256"]) == len(manifest["prompts_sha256"]) == 64
    assert secret not in "".join(p.read_text() for p in output.iterdir())
    fake_openrouter.calls.clear()
    assert cli.main(args + ["--resume"]) == 0
    assert not fake_openrouter.calls


def test_missing_key_fails_before_output(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    output = tmp_path / "run"
    assert cli.main(["run", "--model", "vendor/default", "--output", str(output)]) == 2
    assert "OPENROUTER_API_KEY" in capsys.readouterr().err
    assert not output.exists()


def test_shortcut_model_and_explicit_discussion_override(model_config, fake_openrouter, tmp_path):
    output = tmp_path / "run"
    assert cli.main(["run", "--config", str(model_config), "--model", "vendor/new-default",
                     "--question", "A question", "--rounds", "1", "--output", str(output)]) == 0
    manifest = read_manifest(output)
    assert manifest["config"]["discussion"]["rounds"] == 1
    assert manifest["config"]["discussion"]["concurrency"] == 2
    assert manifest["config"]["model"]["model"] == "vendor/new-default"
    assert len(read_results(output)["question-0"]["calls"]) == 7


def test_failed_tasks_can_resume_and_completed_tasks_are_not_repeated(dataset, fake_openrouter, tmp_path):
    output = tmp_path / "run"
    args = ["run", "--model", "vendor/default", "--dataset", str(dataset), "--output", str(output)]
    fake_openrouter.fail = True
    assert cli.main(args) == 1
    assert read_results(output)["task-0"]["status"] == "failed"
    fake_openrouter.fail = False
    assert cli.main(args + ["--resume"]) == 0
    records = (output / "results.jsonl").read_text().splitlines()
    assert [json.loads(r)["status"] for r in records] == ["failed", "completed"]
    fake_openrouter.calls.clear()
    assert cli.main(args + ["--resume"]) == 0
    assert not fake_openrouter.calls


def test_resume_rejects_config_data_and_prompt_changes(dataset, tmp_path):
    output = tmp_path / "run"
    args = ["run", "--dataset", str(dataset), "--output", str(output)]
    assert cli.main(args) == 0
    initial = (output / "results.jsonl").read_bytes()
    assert cli.main(args + ["--resume", "--rounds", "2"]) == 2
    original = dataset.read_text()
    dataset.write_text(original.replace("991837", "991838"))
    assert cli.main(args + ["--resume"]) == 2
    dataset.write_text(original)
    manifest = read_manifest(output)
    manifest["prompts_sha256"] = "old prompts"
    (output / "manifest.json").write_text(json.dumps(manifest))
    assert cli.main(args + ["--resume"]) == 2
    assert (output / "results.jsonl").read_bytes() == initial


def test_live_scenario_and_existing_output_are_rejected(tmp_path, fake_openrouter):
    output = tmp_path / "run"
    assert cli.main(["run", "--model", "vendor/default", "--scenario", "tie", "--output", str(output)]) == 2
    assert not output.exists()
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("keep")
    assert cli.main(["run", "--output", str(output)]) == 2
    assert marker.read_text() == "keep"
