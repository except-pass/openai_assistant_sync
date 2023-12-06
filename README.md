# OpenAI Assistant Sync Tool

Tighten your OpenAI Assistant feedback loop.  Simplify datafile, instruction, and config updates. 

## What problem is this solving

When working with the OpenAI Assistant API, managing configurations, syncing datafiles, and updating instructions can become a manual and error-prone process. This script simplifies these tasks, making it easier to interact with the OpenAI Assistant API and keep configurations up to date.

## What does it do?

Keep your OpenAI Assistant config, instructions, and datafiles in a local directory.  This tool then inspects your directory and makes the required OpenAI API calls to get your assistant looking exactly like the local directory.
 - Uploads new instructions as found in `instructions.txt`
 - Changes the model, tools, or assistant name.
 - Ensures the datafiles the live assistant uses are the same ones as in your directory

### Datafile Sync Operations

- **New Files:** Files in the local directory but not in the OpenAI Assistant API will be uploaded.
- **Updated Files:** Files with differences in size between the local and remote versions will be deleted and then uploaded.
- **Deleted Files:** Files in the OpenAI Assistant API but not in the local directory will be deleted.


## Installation

- Python installed on your machine
- Set-up and activate a virtual environment
- Required Python packages (install using `pip install -r requirements.txt`):

Or you can use docker: `docker pull exceptpass/openai_assistant_sync`.  If you do then you can substitute `python sync.py` with the docker run command everywhere in the rest of this guide.  

Docker run: 
```bash
docker run --rm --volume "$(pwd):/usr/src/app/" --env OPENAI_API_KEY=${OPENAI_API_KEY} exceptpass/openai_assistant_sync
```

Or in Windows
```powershell
docker run --rm --volume "${PWD}:/usr/src/app/" --env OPENAI_API_KEY=${OPENAI_API_KEY} exceptpass/openai_assistant_sync
```

## API Key Management

Either have `OPENAI_API_KEY` in your environment variables, or create a `.env` file in the same directory as the script with your OpenAI API key:

    ```ini
    OPENAI_API_KEY=your-api-key-here
    ```

If you set-up the `.env` file, you can omit the `--env` part of the docker run command.  The docker volume will automatically pick up your `.env` file.


## How to Use 

To initialize a directory locally (without interacting with the OpenAI server), use:

```bash
python sync.py --dirpath /path/to/your/directory --init
```

Edit the configs and instructions in the new directory.  Add datafiles to the `datafiles` directory.

You can perform a dry run to see what changes will be made, without actually modifying or deleting anything.

```bash
python sync.py --dirpath /path/to/your/directory
```

Once you're happy with the results you can go live.

```bash
python sync.py --dirpath /path/to/your/directory --golive
```


## Assistant Configuration

The script uses a `config.yaml` file to define the OpenAI Assistant configuration. Customize the `name`, `tools`, `model`, and other parameters as needed.

### Datafiles

Place your datafiles in the `datafiles` directory. The script will automatically detect new, updated, and deleted files when syncing with the OpenAI Assistant API.

### Instructions

Define your assistant's instructions in the `instructions.txt` file.