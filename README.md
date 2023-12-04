# OpenAI Assistant Sync Tool

Tighten your feedback loop working with OpenAI Assistants

## Problem Statement

When working with the OpenAI Assistant API, managing configurations, syncing datafiles, and updating instructions can become a manual and error-prone process. This script aims to streamline these tasks, making it easier for users to interact with the OpenAI Assistant API and keep their configurations up to date.

## How to Run

### Prerequisites

- Python installed on your machine
- Required Python packages (install using `pip install -r requirements.txt`):

### Configuration

1. Either have `OPENAI_API_KEY` in your environment variables, or create a `.env` file in the same directory as the script with your OpenAI API key:

    ```ini
    OPENAI_API_KEY=your-api-key-here
    ```

2. Customize the assistant configuration and instructions in the `config.yaml` and `instructions.txt` files, respectively.

To initialize a directory locally (without interacting with the OpenAI server), use:

```bash
python your_script_name.py --dirpath /path/to/your/directory --init
```

### Running the Script

Use the following command to sync the directory with the OpenAI Assistant API:

```bash
python your_script_name.py --dirpath /path/to/your/directory --golive
```

- `--dirpath`: Path to the directory containing the assistant configuration and datafiles.
- `--golive`: Flag to perform the operation for real. Omitting this flag runs a dry run.

## Script Overview

### Assistant Configuration

The script uses a `config.yaml` file to define the OpenAI Assistant configuration. Customize the `name`, `tools`, `model`, and other parameters as needed.

### Datafiles

Place your datafiles in the `datafiles` directory. The script will automatically detect new, updated, and deleted files when syncing with the OpenAI Assistant API.

### Instructions

Define your assistant's instructions in the `instructions.txt` file.

### Sync Operations

- **New Files:** Files in the local directory but not in the OpenAI Assistant API will be uploaded.
- **Updated Files:** Files with differences in size between the local and remote versions will be deleted and then uploaded.
- **Deleted Files:** Files in the OpenAI Assistant API but not in the local directory will be deleted.


## Examples

```bash
# Sync the directory for real
python sync.py --dirpath /path/to/your/directory --golive

# Run a dry run (no changes will be applied)
python sync.py --dirpath /path/to/your/directory
```

## Docker

The entrypoint is `python sync.py`.

Run with docker on Windows

```powershell
docker run --rm --volume "${PWD}:/usr/src/app/" --env OPENAI_API_KEY=${OPENAI_API_KEY} open-ai-assistant-sync --dirpath myassistant --init
```

or a bash shell
```bash
docker run --rm --volume "$(pwd):/usr/src/app/" --env OPENAI_API_KEY=${OPENAI_API_KEY} open-ai-assistant-sync --dirpath myassistant --init
```

Note if you made the `.env` file you can omit the `--env` flag.