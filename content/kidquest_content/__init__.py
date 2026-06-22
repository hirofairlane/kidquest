"""KidQuest content-generation pipeline.

Runs on demand on the GPU box (not the 24/7 server). Importable without side
effects; network calls to Ollama/ComfyUI live in dedicated, mockable clients.
"""

__all__: list[str] = []
