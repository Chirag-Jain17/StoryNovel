from click import prompt
from sqlalchemy.orm import Session

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

from core.config import settings
from core.models import StoryLLMResponse, StoryNodeLLM
from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode

# ensure environment variables from .env are loaded; ChatGoogleGenerativeAI
# reads GOOGLE_API_KEY by default, so we pass the configured key explicitly.
load_dotenv()

class StoryGenerator:

    @classmethod #class method as it is a general method, not particular to each instance
    def _get_llm(cls): # _functionname means that it is a private method, works internally
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=settings.GEMINI_API_KEY
        )

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "dystopia") -> Story:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        #gives the exact prompt structure to the LLM and gives it details and response structure
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                STORY_PROMPT
            ),
            (
                "human",
                f"Create the story with this theme: {theme}"
            )
        ]).partial(format_instructions=story_parser.get_format_instructions())

        raw_response = llm.invoke(prompt.invoke({})) #calling the LLM which automatically creates the structure for the prompt to be sent to the LLM
        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        story_structure = story_parser.parse(response_text)#confirmation of correct format and parsing to the python object, output of StoryLLMResponse in models.py
        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush() #updates the db with all populated objects so that they can be used later

        root_node_data = story_structure.rootNode #creating the root node and validating it
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        #todo: process data
        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        return story_db

    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data = StoryNodeLLM, is_root: bool = False) -> StoryNode:
        node = StoryNode(
            story_id = story_id,
            content =node_data.content if hasattr(node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data["isWinningEnding"],
            options=[]
        )
        db.add(node)
        db.flush()

        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode
                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node) #checking validity of next node

                child_node = cls._process_story_node(db, story_id, next_node, False) #sending it for processing
                options_list.append({ #structure of the options, to prevent storing of all options at once, space and speed enhancing
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()   #it is a recursive function for all functions
        return node

