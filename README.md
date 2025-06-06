<p align="center">
<h1><center> 🎯 Trackio</center></h1>
</p>

`trackio` is a lightweight alternative for `wandb` that uses Hugging Face Datasets for experiment logging and Gradio / Spaces for visualization.

<img width="1371" alt="image" src="https://github.com/user-attachments/assets/5a42054d-8b01-49cb-acb3-d8884413904e" />


## Features
- **API compatible** with `wandb.init`, `wandb.log`, and `wandb.finish` (drop-in replacement: just use `trackio` instead of `wandb`)
- Persists logs in a private Hugging Face Dataset
- Visualize experiments with a Gradio dashboard locally or on Hugging Face Spaces
- *Local-first* design: dashboard runs locally by default. You can also host it on Spaces by specifying a `space_id`.
- Everything here, including hosting on Spaces, is **free**!

Trackio is designed to be lightweight (<1000 lines of Python code total), not fully-featured. It is designed in an extensible way and written entirely in Python so that developers can easily fork the repository and add functionality that they care about.


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
        wandb.init(project="fake-training", config={
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

## Deploying to Hugging Face Spaces

When calling `trackio.init()`, by default the service will run locally and collect data on the local machine. 

If instead you pass a `space_id` to `init`, like:

```py
trackio.init(space_id="org_name/space_name")
``` 
or 
```py
trackio.init(space_id="user_name/space_name")
``` 

it will use an existing or automatically deploy a new Hugging Face Space as needed. The current version of trackio is deployed to the specified space if it does not yet exist.

## Embedding a Trackio Dashboard

One of the reasons we created `trackio` was to make it easy to embed live dashboards on websites, blog posts, or anywhere else you can embed a website.

If you are hosting your Trackio dashboard on Spaces, then you can embed the url of that Space as an IFrame. You can even use query parameters to only specific projects and/or metrics, e.g.

```html
<iframe src="https://abidlabs-trackio-1234.hf.space/?project=fake-training&metrics=train_loss,train_accuracy" width=1600 height=500 frameBorder="0">
```

Supported query parameters:

- `project`: (string) Filter the dashboard to show only a specific project
- `metrics`: (comma-separated list) Filter the dashboard to show only specific metrics, e.g. `train_loss,train_accuracy`

# License

MIT License 
