# Trackio

Trackio is a drop-in replacement for `wandb` that uses Hugging Face Datasets for experiment logging and Gradio for visualization.

## Features
- **API compatible** with `wandb.init`, `wandb.log`, and `wandb.finish` (use `trackio` instead)
- Stores logs in a Hugging Face Datasets-compatible format (Parquet)
- Visualize experiments with a Gradio dashboard

## Example Usage
```python
import random
import math
import trackio

# Launch 5 simulated experiments
total_runs = 5
for run in range(total_runs):
    trackio.init(
        project="basic-intro",
        name=f"experiment_{run}",
        config={
            "learning_rate": 0.02,
            "architecture": "CNN",
            "dataset": "CIFAR-100",
            "epochs": 10,
        },
    )

    epochs = 10
    offset = random.random() / 5
    for epoch in range(2, epochs):
        acc = 1 - 2 ** -epoch - random.random() / epoch - offset
        loss = 2 ** -epoch + random.random() / epoch + offset
        trackio.log({"acc": acc, "loss": loss})

    trackio.finish()

# To launch the Gradio UI:
trackio.ui()
```

## Data Storage
- Logs are saved in `./trackio/{project}/{run_name}/run.parquet`
- Config is saved as `config.json` in the same directory

## Visualization
- Run `trackio.ui()` to launch the Gradio dashboard and explore your experiments

## Installation

```bash
pip install trackio
```

## Usage

```python
import trackio

print(trackio.__version__)
```

## License

MIT License 