from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import (
    YoutubeVideoSearchTool,
    YoutubeChannelSearchTool,
    ScrapeWebsiteTool,
    SeleniumScrapingTool,
    ArxivPaperTool,
    FileReadTool,
    PDFSearchTool,
    TXTSearchTool,
    MDXSearchTool,
    CodeDocsSearchTool,
    DirectoryReadTool
)
from typing import List

# define the tools
# youtube agent tools
yt_video_search_tool = YoutubeVideoSearchTool()
yt_channel_search_tool = YoutubeChannelSearchTool()

# web scraping tools
web_scraping_tool = ScrapeWebsiteTool()
selenium_scraping_tool = SeleniumScrapingTool()
code_docs_search_tool = CodeDocsSearchTool()

# arxiv research paper tool
arxiv_tool = ArxivPaperTool(download_pdfs=True,
                            use_title_as_filename=True)

# document related tools
file_reader_tool = FileReadTool()
pdf_search_tool = PDFSearchTool()
text_search_tool = TXTSearchTool()
md_search_tool = MDXSearchTool()
directory_read_tool = DirectoryReadTool()


@CrewBase
class ResearchCrew():
    """ResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # define the paths for config related files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    # ====================== Agents ==========================================
    
    # define the agents
    @agent
    def research_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["research_manager"]
        )
        
    @agent
    def youtube_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_specialist"],
            tools=[yt_video_search_tool, 
                   yt_channel_search_tool]
        )
        
    @agent
    def web_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["web_specialist"],
            tools=[web_scraping_tool, 
                   selenium_scraping_tool,
                   code_docs_search_tool]
        )
        
        
    @agent
    def arxiv_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["arxiv_specialist"],
            tools=[arxiv_tool]
        )
        
    @agent
    def document_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["document_specialist"],
            tools=[file_reader_tool,
                  pdf_search_tool,
                  text_search_tool,
                  md_search_tool,
                  directory_read_tool]
        )

    # ======================== Tasks ==================================
    # define the task
    @task
    def research_compilation(self) -> Task:
        return Task(
            config=self.tasks_config["research_compilation"]
        )
        
    # ======================== Crew ===================================
    
    # define the crew
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.youtube_specialist(), 
                    self.arxiv_specialist(),
                    self.web_specialist(),
                    self.document_specialist()],
            tasks=[self.research_compilation()],
            verbose=True,
            process=Process.hierarchical,
            planning=True,
            manager_agent=self.research_manager()
        )


def run(inputs: dict[str, str]) -> str:
    """Test Run our crew"""
    research_crew = ResearchCrew().crew()
    result = research_crew.kickoff(inputs)
    return result.raw


if __name__ == "__main__":
    inputs = {
        "youtube_links": "",
        "webpage_links": "",
        "research_paper_links": "",
        "document_paths": "docs/document-export-24-09-2025-11_58_50.txt",
    }
    
    result = run(inputs)
    print(result)