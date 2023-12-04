import yaml
from pydantic import BaseModel
from typing import List, Literal, Optional, Union, Dict
from pathlib import Path
from openai import OpenAI
from logging import getLogger
from dotenv import load_dotenv
load_dotenv()

logger = getLogger()

client = OpenAI()
    
def get_assistant(assistant_id):
    return client.beta.assistants.retrieve(assistant_id)

def get_remote_files(assistant_id) -> dict:
    assistant = get_assistant(assistant_id=assistant_id)
    file_ids = assistant.file_ids
    remote_files = {}
    for fid in file_ids:
        fobj = client.files.retrieve(fid)
        remote_files[fobj.filename]=fobj
    return remote_files

def delete_file(file_id):
    client.files.delete(file_id)

HERE = Path(__file__).parent

def instructions_path(dirpath):
    return Path(dirpath)/'instructions.txt'
def config_path(dirpath):
    return Path(dirpath)/'config.yaml'
def datafile_path(dirpath):
    return Path(dirpath)/'datafiles'

def load_instructions(dirpath):
    with open(instructions_path(dirpath=dirpath)) as f:
        return f.read()



class AssistantTool(BaseModel):
    type: Union[Literal['retrieval'], Literal['code_interpreter'], Literal['function']]
    function: Optional[Dict]=None

class OpenAIAssistantConfig(BaseModel):
    name: str
    tools: List[AssistantTool]
    model: str
    assistant_id: str
    instructions: Optional[str]=None
    @classmethod
    def from_directory(cls, dirpath):
        with open(config_path) as f:
            rawconfig = yaml.safe_load(f)

        instructions = load_instructions(dirpath)
        return cls(instructions=instructions, **rawconfig)

    def get_from_remote(self):
        return get_assistant(self.assistant_id)
    def sync_to_remote(self, file_ids=None):
        assert self.instructions is not None
        assistant = self.get_from_remote()
        updated_assistant = client.beta.assistants.update(assistant_id=self.assistant_id,
                                    instructions=self.instructions,
                                    name=self.name,
                                    tools=self.tools,
                                    model=self.model,
                                    file_ids=assistant.file_ids)

    def upload_new_file(self, filepath):
        assistant_id = self.assistant_id
        assistant = self.get_from_remote()
        with open(filepath, 'rb') as f:
            new_file_obj = client.files.create(file=f, purpose='assistants')
        updated_assistant = client.beta.assistants.update(assistant_id=assistant_id,
                                    file_ids=assistant.file_ids+[new_file_obj.id])
        return updated_assistant
    
    def create_new(self):
        assert self.instructions is not None        
        return client.beta.assistants.create(
                    instructions=self.instructions,
                    name=self.name,
                    tools=self.tools,
                    model=self.model,
                    )
    
    def delete_file(self, file_id):
        delete_file(file_id=file_id)
        assistant = self.get_from_remote()
        file_ids = [fid for fid in assistant.file_ids if fid != file_id]
        updated_assistant = client.beta.assistants.update(assistant_id=self.assistant_id,
                                    file_ids=file_ids)

class FileWrangler:
    def __init__(self, dirpath:Union[str, Path]):
        self.dirpath = Path(dirpath)
        self.configs = OpenAIAssistantConfig.from_directory(self.dirpath)
        self.datafile_path = datafile_path(self.dirpath)

    def local_files_not_in_remote(self):
        returnme = []
        remote_files = get_remote_files(self.configs.assistant_id)
        for datafile in Path(self.datafile_path).glob('*'): 
            fobj = remote_files.get(datafile.name)
            if not fobj:  #this file is in the folder but not in the server
                returnme.append(datafile.name)
        return returnme
    def local_files_different_from_remote(self):
        returnme = []
        remote_files = get_remote_files(self.configs.assistant_id)
        for datafile in Path(self.datafile_path).glob('*'): 
            fobj = remote_files.get(datafile.name)
            if fobj:
                local_size = datafile.stat().st_size
                remote_size = fobj.bytes
                logger.debug(f'Remote file is {remote_size}, and the local version is {local_size}' )
                if local_size==remote_size:
                    logger.debug(f"They're the same size, so I'll assume they are the same file.")
                else:
                    logger.debug(f"They're different.  Need to delete and sync.")
                    returnme.append(datafile.name)
        return returnme
    def remote_files_not_in_local(self):
        returnme = []
        remote_files = get_remote_files(self.configs.assistant_id)
        for fname, fobj in remote_files.items():
            local_file = self.datafile_path/fname
            if not local_file.exists():
                returnme.append(local_file.name)
        return returnme 
    
    def files_to_sync(self):
        new_files = self.local_files_not_in_remote() #upload
        updated_files = self.local_files_different_from_remote()  #delete then upload
        delete_these_files = self.remote_files_not_in_local()  #delete
        return {"new": new_files, 'update': updated_files, 'delete': delete_these_files}
    
    def sync(self, dry_run=True):
        affected_files = self.files_to_sync()
        if not dry_run:
            for fname in affected_files['new']:
                logger.info(f"Uploading {self.datafile_path/fname}")
                self.configs.upload_new_file(self.datafile_path/fname)
            
            for fname in affected_files['update']:
                remote_files = get_remote_files(self.configs.assistant_id)
                remote_file_obj = remote_files[fname]
                logger.info(f'Updating {fname}')
                self.configs.delete_file(file_id=remote_file_obj.id)
                self.configs.upload_new_file(self.datafile_path/fname)

            for fname in affected_files['delete']:
                remote_files = get_remote_files(self.configs.assistant_id)                
                remote_file_obj = remote_files[fname]
                logger.info(f'Deleting {fname} which is remote file {remote_file_obj.id}')
                self.configs.delete_file(file_id=remote_file_obj.id)
        return affected_files

def init_directory(dirpath):
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    datafile_path(dirpath=dirpath).mkdir(parents=True, exist_ok=True)

    instruction_file = instructions_path(dirpath)
    if not instruction_file.exists():
        with open(instruction_file, 'w') as f:
            f.write("You are an AI assistant.")

    config_file = config_path(dirpath)
    if not config_file.exists():
        dummy = OpenAIAssistantConfig(assistant_id="!!Replace me with the real assistant id!!",
                                      name='My Assistant', 
                                      tools=[AssistantTool(type='retrieval')], 
                                      model='gpt-4-1106-preview')
        with open(config_file, 'w') as f:
            yaml.dump(dummy.model_dump(exclude_none=True), stream=f)
    logger.info("Directory set-up.  Next you'll want to adjust the config and instructions and add some datafiles.")

if __name__ == '__main__':
    from loguru import logger    
    import click

    @click.command()
    @click.option('--dirpath', help='Sync the config and datafiles in this directory')
    @click.option('--golive', is_flag=True, default=False, help='Run the operation for real (dry run by default)')
    @click.option('--init', is_flag=True, default=False, help='Initialize the directory locally.  No interaction with the OpenAI server.')
    def sync_directory(dirpath, golive=False, init=False):
        if init:
            return init_directory(dirpath=dirpath)
        dry_run = not golive
        fw = FileWrangler(dirpath=dirpath)
        if not dry_run:
            fw.configs.sync_to_remote()
        affected_files = fw.sync(dry_run=dry_run)
        click.echo(affected_files)

    sync_directory()