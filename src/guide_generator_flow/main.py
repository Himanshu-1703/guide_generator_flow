from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from guide_generator_flow.crews.research_crew.research_crew import ResearchCrew
from guide_generator_flow.crews.writing_crew.writing_crew import WritingCrew
from typing import Optional


# define a structured state for our flow
class ResearchFlowState(BaseModel):
    
    # user inputs (sources)
    youtube_links: Optional[str] = ""
    document_paths: Optional[str] = ""
    webpage_links: Optional[str] = ""
    research_paper_links: Optional[str] = ""
    
    # outputs from nodes
    research_report: str | None = None
    final_guide: str | None = None


# defining our flow
class GuideGeneratorFlow(Flow[ResearchFlowState]):
    """
    Main flow that orchestrates the complete guide generation process.
    
    Flow Steps:
    1. receive_user_inputs - Accept and Validate user inputs
    2. run_research_crew - Execute Crew 1 (hierarchical research)
    3. run_writing_crew - Execute Crew 2 (sequential writing)
    """
    
    # define the start node
    @start()
    def receive_user_inputs(self) -> str:
        print("=" * 70)
        print("🚀 GUIDE GENERATOR FLOW STARTED")
        print("=" * 70)
        
        # log which sources were provided
        sources_provided = []
        
        if self.state.youtube_links:
            sources_provided.append("YouTube")
        if self.state.webpage_links:
            sources_provided.append("Web Pages")
        if self.state.document_paths:
            sources_provided.append("Documents")
        if self.state.research_paper_links:
            sources_provided.append("Research Papers")
            
        if not sources_provided:
            print("\n⚠️  WARNING: No sources provided!")
            print("Please provide at least one source type.")
            return "no_sources"
        
        print(f"\n✅ Sources provided: {', '.join(sources_provided)}")
        print("\n" + "=" * 70)
        
        return "inputs_received"
    
    # define the node to run crew 1
    @listen(receive_user_inputs)
    def run_research_crew(self, prev_output) -> str:
        """
        Executes Crew 1: Research Crew
        
        The research crew uses a manager agent to coordinate 4 specialists
        who gather information from different source types. The manager then
        compiles everything into a comprehensive research report
        """
        
        if prev_output == "no_sources":
            print("\n❌ Skipping research crew - no sources provided")
            return "research_skipped"
        
        elif prev_output == "inputs_received":
            print("\n" + "=" * 70)
            print("📚 CREW 1: RESEARCH CREW (Hierarchical)")
            print("=" * 70)
            print("\nInitializing research crew with manager + 4 specialists...")
            print("- YouTube Specialist")
            print("- Web Content Specialist")
            print("- Academic Paper Specialist")
            print("- Document Specialist")
            
            try:
                # initialize my research crew
                research_crew = ResearchCrew().crew()
                print("\n🔄 Delegating research tasks to specialists...\n")
                
                # execute the crew with provided sources
                result = research_crew.kickoff(inputs={
                    "youtube_links": self.state.youtube_links or "Not provided",
                    "webpage_links": self.state.webpage_links or "Not provided",
                    "research_paper_links": self.state.research_paper_links or "Not provided",
                    "document_paths": self.state.document_paths or "Not provided"
                })
                
                # store the research report into state
                self.state.research_report = result.raw
                
                print("\n" + "=" * 70)
                print("✅ RESEARCH CREW COMPLETED")
                print("=" * 70)
                print(f"📊 Research Report Generated:")
                
                return "research_complete"

            except Exception as e:
                print(f"\n❌ ERROR in Research Crew: {str(e)}")
                return "research_failed"
                
    # define the node to run crew 2            
    @listen(run_research_crew)
    def run_writing_crew(self, prev_output) -> str:
        """
        Execute Crew 2: Writing Crew (Sequential Process)
        
        The writing crew uses a sequential process where:
        1. Technical Writer transforms research into beginner-friendly guide
        2. Content Editor reviews and polishes the guide
        """
        
        if prev_output == "research_skipped":
            print("\n❌ Skipping writing crew - research was skipped")
            return "writing_skipped"
        
        if prev_output == "research_failed":
            print("\n❌ Skipping writing crew - research failed")
            return "writing_skipped"
        
        print("\n" + "=" * 70)
        print("✍️  CREW 2: WRITING CREW (Sequential)")
        print("=" * 70)
        print("\nInitializing writing crew...")
        print("- Technical Writer (Step 1)")
        print("- Content Editor (Step 2)")
        print("\n" + "=" * 70)
         
        try:
            # Initialize the writing crew
            writing_crew = WritingCrew().crew()
            
            print("\n🔄 Transforming research into beginner-friendly guide...\n")
            
            # execute the writing crew with research report generated in previous node
            result = writing_crew.kickoff(inputs={
                "research_report": self.state.research_report
            })
            
            # store the generated guide into state
            self.state.final_guide = result.raw
            
            print("\n" + "=" * 70)
            print("✅ WRITING CREW COMPLETED")
            print("=" * 70)
            print(f"📝 Getting Started Guide Generated:")
            print("\n" + "=" * 70)
            
            return "guide_complete"
        
        except Exception as e:
            print(f"\n❌ ERROR in Writing Crew: {str(e)}")
            return "writing_failed"
        

def get_inputs():
    """
    Interactive terminal interface to collect user inputs.
    All inputs are optional.
    """
    print("\n" + "=" * 70)
    print("🎯 GUIDE GENERATOR - INPUT COLLECTION")
    print("=" * 70)
    print("\nWelcome! Let's create a getting-started guide for your framework/tool.")
    print("\nℹ️  All source inputs are OPTIONAL. You can skip any by pressing Enter.")
    print("=" * 70)
    
    # YouTube Links (Optional)
    print("\n" + "─" * 70)
    print("\n📺 YOUTUBE VIDEOS/CHANNELS")
    print("   You can provide:")
    print("   - Individual video URLs (e.g., https://youtube.com/watch?v=abc123)")
    print("   - Channel URLs (e.g., https://youtube.com/@channelname)")
    print("   - Multiple links separated by commas")
    youtube_links = input("\n   Enter YouTube links (or press Enter to skip): ").strip()
    
    # Web Page Links (Optional)
    print("\n" + "─" * 70)
    print("\n🌐 WEB PAGES/ARTICLES")
    print("   You can provide:")
    print("   - Documentation URLs")
    print("   - Blog posts or tutorials")
    print("   - Multiple links separated by commas")
    webpage_links = input("\n   Enter web page URLs (or press Enter to skip): ").strip()
    
    # Research Papers (Optional)
    print("\n" + "─" * 70)
    print("\n📄 RESEARCH PAPERS (arXiv)")
    print("   You can provide:")
    print("   - arXiv URLs (e.g., https://arxiv.org/abs/2103.xxxxx)")
    print("   - Paper titles or arXiv IDs")
    print("   - Multiple entries separated by commas")
    research_paper_links = input("\n   Enter research paper links/queries (or press Enter to skip): ").strip()
    
    # Documents (Optional)
    print("\n" + "─" * 70)
    print("\n📁 DOCUMENTS (PDF/Text/Markdown)")
    print("   You can provide:")
    print("   - Local file paths to PDFs")
    print("   - Text file paths (.txt)")
    print("   - Markdown file paths (.md, .mdx)")
    print("   - Multiple paths separated by commas")
    document_paths = input("\n   Enter document paths (or press Enter to skip): ").strip()
    
    return {
        'youtube_links': youtube_links,
        'webpage_links': webpage_links,
        'research_paper_links': research_paper_links,
        'document_paths': document_paths
    }
    
    
    
def kickoff():
    """Execute the flow"""
    
    # get the inputs
    inputs = get_inputs()
    
    # define the flow
    flow = GuideGeneratorFlow()
    
    # run the flow with inputs
    flow_result = flow.kickoff(inputs=inputs)
    
    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    print(f"\n{flow_result}")
    
if __name__ == "__main__":
    kickoff()