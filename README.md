<p align="center">
<h1><center> 🎯 Trackio</center></h1>
</p>

`trackio` is a lightweight alternative for `wandb` that uses Hugging Face Datasets for experiment logging and Gradio / Spaces for visualization.

## Features
- **API compatible** with `wandb.init`, `wandb.log`, and `wandb.finish` (drop-in replacement: just use `trackio` instead of `wandb`)
- Store logs in a Hugging Face Datasets-compatible format (Parquet)
- Visualize experiments with a Gradio dashboard
- *Local-first* design: dashboard runs locally by default. You can also host it on Spaces by changing a single parameter.
- Everything here, including hosting on Spaces, is **free**!

## Example Usage
```python
import random
import math
import trackio
import time

sleep_time = 0.5

# Launch 5 simulated experiments
total_runs = 5
for run in range(total_runs):
    
    trackio.init(
        project="basic-intro-4",
        name=f"experiment_{run}",
        config={
            "learning_rate": 0.02,
            "architecture": "CNN",
            "dataset": "CIFAR-100",
            "epochs": 10,
        },
    )
    time.sleep(sleep_time)

    epochs = 10
    offset = random.random() / 5
    for epoch in range(2, epochs):
        time.sleep(sleep_time)
        acc = 1 - 2**-epoch - random.random() / epoch - offset
        loss = 2**-epoch + random.random() / epoch + offset
        trackio.log({"acc": acc, "loss": loss})
```

Trackio is designed to be lightweight (<500 lines of code total), not fully-featured. It is designed in a modular way so that developers can easily fork the repository and add functionality that they care about.

## Data Storage
- Logs are saved in `./trackio/{project}/{run_name}/run.parquet`
- Config is saved as `config.json` in the same directory

## Visualization
- Run `trackio.ui()` to launch the Gradio dashboard and explore your experiments

## Installation

```bash
pip install trackio
```

or with `uv`:

```py
uv pip install trackio
```

## Usage

```python
import trackio as wandb
import random
import time

runs = 3
epochs = 8

def simulate_multiple_runs():
    for run in range(runs):
        wandb.init(project="minimal-train-loop2", config={
            "epochs": epochs,
            "learning_rate": 0.001,
            "batch_size": 64
        })
        
        for epoch in range(epochs):
            train_loss = random.uniform(0.2, 1.0)
            train_acc = random.uniform(0.6, 0.95)
    
            val_loss = train_loss - random.uniform(0.01, 0.1)
            val_acc = train_acc + random.uniform(0.01, 0.05)
    
            wandb.log({
                "epoch": epoch,
                "train_loss": train_loss,
                "train_accuracy": train_acc,
                "val_loss": val_loss,
                "val_accuracy": val_acc
            })
    
            time.sleep(0.2)

    wandb.finish()

simulate_multiple_runs()
```

![Uploading Screen Recording 2025-05-12 at 2.43.38 PM.gif…]()


## License

MIT License 
