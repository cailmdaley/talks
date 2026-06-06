# CNRS generated illustration prompts

These prompts are for conceptual slide illustrations only. Do not use generated images for
scientific data plots, maps, contours, or measured quantities.

Run from the repository root:

```bash
uv run 26_CNRS_RisingTalents/scripts/generate_cnrs_image.py \
  26_CNRS_RisingTalents/image_prompts/standard_model_probe_hero.md \
  26_CNRS_RisingTalents/images/standard_model_probe_hero.png
```

The script defaults to `gpt-image-1.5`, which is the current GPT image model ID visible in the
OpenAI image-generation docs from this worker environment. Override it when Cail confirms a
different accessible model:

```bash
OPENAI_IMAGE_MODEL=gpt-image-2 uv run 26_CNRS_RisingTalents/scripts/generate_cnrs_image.py \
  26_CNRS_RisingTalents/image_prompts/shear_pipeline_flowchart.md \
  26_CNRS_RisingTalents/images/shear_pipeline_flowchart.png
```

Required environment:

- `OPENAI_API_KEY`
- Optional `OPENAI_IMAGE_MODEL`

