from typing import List

from typing_extensions import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from ..config import Settings
from ..prompts import build_coordinator_instructions
from .tools import generate_axis_unit_context, generate_ideal_roles


class DeepAgentState(TypedDict):
    """Shared state for the coordinator agent.

    - messages: the ReAct message history
    - remaining_steps: how many tool/LLM steps the agent is allowed to take
    """

    messages: Annotated[List[AnyMessage], add_messages]
    remaining_steps: int


def build_react_agent(model: ChatOpenAI, settings: Settings):
    """Create the ReAct coordinator agent with tools and instructions."""
    tools = [generate_axis_unit_context, generate_ideal_roles]
    instructions = build_coordinator_instructions(settings)

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=instructions,
        state_schema=DeepAgentState,
    )
    return agent
