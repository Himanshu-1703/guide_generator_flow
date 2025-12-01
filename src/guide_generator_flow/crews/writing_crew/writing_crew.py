from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class WritingCrew():
    """WritingCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # define the path of config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    # ======================== Agents ========================
    # define agents
    @agent
    def technical_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_writer"]
        )
    
    @agent
    def content_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["content_editor"]
        )

    # ======================== Tasks ===========================
    # define the tasks
    @task
    def write_getting_started_guide(self) -> Task:
        return Task(
            config=self.tasks_config["write_getting_started_guide"]
        )
        
    @task
    def review_and_polish_guide(self) -> Task:
        return Task(
            config=self.tasks_config["review_and_polish_guide"]        
            )
    
    # ======================== Crew ==============================
    # define the crew
    @crew
    def crew(self) -> Crew:
        """Creates the WritingCrew crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
        )
