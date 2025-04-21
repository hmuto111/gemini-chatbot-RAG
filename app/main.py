import os
from dotenv import load_dotenv
from llama_index.multi_modal_llms.gemini import GeminiMultiModal
from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.schema import TextNode
from llama_index.core import SimpleDirectoryReader

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)

