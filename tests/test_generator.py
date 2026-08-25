from app.services import generator


def test_generate_response_reuses_loaded_model(monkeypatch):
    class FakeModel:
        instances = 0

        def __init__(self, model_path):
            self.model_path = model_path
            self.__class__.instances += 1

        def generate(self, **_):
            return "Generated text", 4

    monkeypatch.setattr(generator, "LlamaModel", FakeModel)
    monkeypatch.setattr(generator, "list_models", lambda: ["test.gguf"])
    monkeypatch.setattr(generator.settings, "model_name", "test.gguf")
    generator._models.clear()

    first = generator.generate_response("First prompt")
    second = generator.generate_response("Second prompt")

    assert first == ("Generated text", 4)
    assert second == ("Generated text", 4)
    assert FakeModel.instances == 1


def test_generate_response_rejects_unknown_model(monkeypatch):
    monkeypatch.setattr(generator, "list_models", lambda: ["approved.gguf"])

    try:
        generator.generate_response("Hello", "../unapproved.gguf")
    except ValueError as error:
        assert str(error) == "Unknown model"
    else:
        raise AssertionError("Expected an unknown model to be rejected")
