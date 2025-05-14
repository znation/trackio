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

Trackio is designed to be lightweight (<500 lines of code total), not fully-featured. It is designed in a modular way so that developers can easily fork the repository and add functionality that they care about.


## Installation

```bash
pip install trackio
```

or with `uv`:

```py
uv pip install trackio
```

## Usage

The usage of `trackio` is designed to be a drop-in replacement for `wandb` in most cases:

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

Running the above will print to the terminal instructions on launching the dashboard.

# Dashboard

You can launch the dashboard by running in your terminal:

```bash
$ trackio show
```

or, in Python:

```py
trackio.show()
```

You can also provide an optional `project` name as the argument to load a specific project directly:

```bash
$ trackio show --project "my project"
```

or, in Python:

```py
trackio.show(project="my project")
```


![Screen Recording 2025-05-12 at 2 43 38 PM](https://github.com/user-attachments/assets/d627c9c3-7365-4250-839c-db67dde34a02)


## License

MIT License 
