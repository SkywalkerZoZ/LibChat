import os
import configparser
from pathlib import Path
from langchain.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi
from prompt_template import LIB_PROMPT_TEMPLATE
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache

class LibChatBot:
    def __init__(self) -> None:
        self.load_config()
        self.set_environment_variables()
        set_llm_cache(InMemoryCache())
        self.llm = Tongyi(cache=True, streaming=True, verbose=True)
        self.prompt_template = PromptTemplate(
            input_variables=["question", "lib_rules_string"],
            template=LIB_PROMPT_TEMPLATE,
        )
        self.schema = self.load_schema(self.config.get('directory', 'SCHEMA_FILE_PATH'))
        self.chain = self.prompt_template | self.llm
    
    def load_config(self):
        self.config = configparser.ConfigParser(interpolation=None)
        try:
            self.config.read("config.ini")
        except configparser.Error as e:
            raise RuntimeError(f"Error reading config file: {e}")
    
    def set_environment_variables(self):
        try:
            os.environ["OPENAI_API_KEY"] = self.config.get('api', 'OPENAI_API_KEY')
            os.environ["OPENAI_API_BASE"] = self.config.get('api', 'OPENAI_API_BASE')
            os.environ["DASHSCOPE_API_KEY"] = self.config.get('api', 'DASHSCOPE_API_KEY')
        except KeyError as e:
            raise RuntimeError(f"Missing required environment configuration: {e}")
    
    def load_schema(self, schema_file_path):
        try:
            schema_path = Path(schema_file_path)
            with schema_path.open('r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file not found: {e}")
        except IOError as e:
            raise RuntimeError(f"Error reading schema file: {e}")

    def ask(self, question):
        res_stream = self.chain.stream({"question": question, "lib_rules_string": self.schema})
        for item in res_stream:
            print(item, end="")
    
    def ask_api(self,question):
        return self.chain.stream({"question": question, "lib_rules_string": self.schema})

if __name__ == '__main__':
    try:
        chat = LibChatBot()
        chat.ask("怎么借书")
    except RuntimeError as e:
        print(f"Initialization failed: {e}")
