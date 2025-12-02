"""
Seinfeld Script Generator Crew

This module defines the CrewAI crew that orchestrates multiple agents to generate
authentic Seinfeld episode scripts using RAG from a Couchbase database.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from .tools.couchbase_rag import SeinfeldRAGTool

# Load environment variables before anything else
load_dotenv()

def get_llm():
    """Create and return the LLM instance."""
    model_name = os.getenv("LLM_MODEL_NAME")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("CAPELLA_AI_ENDPOINT")

    if model_name and not model_name.startswith("openai/"):
        model_name = f"openai/{model_name}"

    return LLM(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
    )



@CrewBase
class SeinfeldScriptCrew:
    """
    Seinfeld Script Generator Crew

    This crew orchestrates multiple specialized agents to create authentic
    Seinfeld episode scripts. Each agent has access to a Couchbase database
    containing actual Seinfeld scripts for RAG-enhanced generation.
    """

    # Path to configuration files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        """Initialize the crew with the RAG tool."""
        self.seinfeld_rag_tool = SeinfeldRAGTool() 
        self._tools = [self.seinfeld_rag_tool]

    @agent
    def theme_analyzer(self) -> Agent:
        """Create the Theme Analyzer agent."""
        return Agent(
            config=self.agents_config["theme_analyzer"],
            tools=self._tools,
            llm=get_llm(),
            verbose=True,
        )

    @agent
    def plot_architect(self) -> Agent:
        """Create the Plot Architect agent."""
        return Agent(
            config=self.agents_config["plot_architect"],
            tools=self._tools,
            llm=get_llm(),
            verbose=True,
        )

    @agent
    def character_voice_specialist(self) -> Agent:
        """Create the Character Voice Specialist agent."""
        return Agent(
            config=self.agents_config["character_voice_specialist"],
            tools=self._tools,
            llm=get_llm(),
            verbose=True,
        )

    @agent
    def dialogue_writer(self) -> Agent:
        """Create the Dialogue Writer agent."""
        return Agent(
            config=self.agents_config["dialogue_writer"],
            tools=self._tools,
            llm=get_llm(),
            verbose=True,
        )

    @agent
    def quality_reviewer(self) -> Agent:
        """Create the Quality Reviewer agent."""
        return Agent(
            config=self.agents_config["quality_reviewer"],
            tools=self._tools,
            llm=get_llm(),
            verbose=True,
        )

    @task
    def analyze_theme(self) -> Task:
        """Create the theme analysis task."""
        return Task(
            config=self.tasks_config["analyze_theme"],
        )

    @task
    def design_plot_structure(self) -> Task:
        """Create the plot structure design task."""
        return Task(
            config=self.tasks_config["design_plot_structure"],
        )

    @task
    def develop_character_voices(self) -> Task:
        """Create the character voice development task."""
        return Task(
            config=self.tasks_config["develop_character_voices"],
        )

    @task
    def write_script_scenes(self) -> Task:
        """Create the script writing task."""
        return Task(
            config=self.tasks_config["write_script_scenes"],
        )

    @task
    def review_and_polish(self) -> Task:
        """Create the review and polish task."""
        return Task(
            config=self.tasks_config["review_and_polish"],
            output_file="output/seinfeld_script.md",
        )

    @crew
    def crew(self) -> Crew:
        """Create the Seinfeld Script Generator crew."""
        return Crew(
            agents=self.agents,  # Automatically populated by @agent decorators
            tasks=self.tasks,  # Automatically populated by @task decorators
            process=Process.sequential,  # Tasks run in sequence
            verbose=True,
            memory=False,  # Disable memory to avoid embedder issues with custom endpoint
            llm=get_llm(),
        )


def run_crew(theme: str) -> str:
    """
    Run the Seinfeld Script Generator crew with the given theme.

    Args:
        theme: The theme for the Seinfeld episode (e.g., "Jerry gets a smart speaker")

    Returns:
        The generated Seinfeld episode script
    """
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Create and run the crew
    crew_instance = SeinfeldScriptCrew()
    result = crew_instance.crew().kickoff(inputs={"theme": theme})

    return result.raw


def run_crew_async(theme: str):
    """
    Run the Seinfeld Script Generator crew asynchronously.

    Args:
        theme: The theme for the Seinfeld episode

    Returns:
        Async result that can be awaited
    """
    crew_instance = SeinfeldScriptCrew()
    return crew_instance.crew().kickoff_async(inputs={"theme": theme})

