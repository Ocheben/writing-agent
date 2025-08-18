import asyncio
import json
from typing import Dict, List, TypedDict, Annotated, AsyncGenerator, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging
import os

from config import settings

# Initialize LangSmith tracing
if settings.langsmith_api_key and settings.langsmith_tracing:
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint

logger = logging.getLogger(__name__)

# Define the state structure
class WritingState(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation messages"]
    content: str
    context: Dict
    action: str
    iterations: int
    max_iterations: int

# Define writing tools
@tool
def analyze_text_structure(text: str) -> str:
    """Analyze the structure and organization of text content."""
    if not text.strip():
        return "Empty text provided"
    
    lines = text.split('\n')
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    words = len(text.split())
    chars = len(text)
    
    analysis = {
        "word_count": words,
        "character_count": chars,
        "line_count": len(lines),
        "paragraph_count": len(paragraphs),
        "structure": "multi-paragraph" if len(paragraphs) > 1 else "single-block"
    }
    
    return f"Text Analysis: {json.dumps(analysis, indent=2)}"

@tool
def suggest_improvements(text: str, focus: str = "general") -> str:
    """Suggest specific improvements for the given text based on focus area."""
    suggestions = []
    
    if focus == "clarity":
        suggestions.extend([
            "Consider breaking long sentences into shorter ones",
            "Use active voice where possible",
            "Replace complex words with simpler alternatives"
        ])
    elif focus == "structure":
        suggestions.extend([
            "Add clear topic sentences to paragraphs",
            "Use transitional phrases between ideas",
            "Consider reorganizing for logical flow"
        ])
    elif focus == "engagement":
        suggestions.extend([
            "Add compelling examples or anecdotes",
            "Use questions to engage readers",
            "Vary sentence length and structure"
        ])
    else:
        suggestions.extend([
            "Check for grammar and spelling errors",
            "Ensure consistent tone throughout",
            "Remove unnecessary words and phrases"
        ])
    
    return f"Improvement suggestions for {focus}: " + "; ".join(suggestions)

@tool
def extract_key_themes(text: str) -> str:
    """Extract and identify key themes and topics from the text."""
    if not text.strip():
        return "No themes found in empty text"
    
    # Simple keyword extraction (in production, you'd use more sophisticated NLP)
    words = text.lower().split()
    word_freq = {}
    
    # Count word frequency (excluding common words)
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    for word in words:
        clean_word = ''.join(c for c in word if c.isalnum())
        if len(clean_word) > 3 and clean_word not in common_words:
            word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
    
    # Get top themes
    top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return f"Key themes identified: {[theme[0] for theme in top_themes]}"

# Create tools list
tools = [analyze_text_structure, suggest_improvements, extract_key_themes]

class WritingAgent:
    def __init__(self):
        self.llm = None
        self.graph = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangGraph agent with proper configuration"""
        try:
            # Initialize the LLM
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not provided - agent will use mock responses")
                self.llm = None
            else:
                self.llm = ChatOpenAI(
                    model="gpt-4-turbo-preview",
                    temperature=0.7,
                    streaming=True,
                    api_key=settings.openai_api_key
                )
            
            # Create the state graph
            workflow = StateGraph(WritingState)
            
            # Add nodes
            workflow.add_node("agent", self.agent_node)
            workflow.add_node("tools", ToolNode(tools))
            
            # Set entry point
            workflow.set_entry_point("agent")
            
            # Add conditional edges
            workflow.add_conditional_edges(
                "agent",
                self.should_continue,
                {
                    "continue": "tools",
                    "end": END
                }
            )
            
            # Add edge from tools back to agent
            workflow.add_edge("tools", "agent")
            
            # Compile the graph
            self.graph = workflow.compile()
            
            logger.info("Writing agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize writing agent: {str(e)}")
            self.graph = None

    def is_ready(self) -> bool:
        """Check if the agent is ready to process requests"""
        return self.graph is not None

    async def agent_node(self, state: WritingState) -> Dict:
        """The main agent reasoning node"""
        try:
            # Get the latest messages
            messages = state.get("messages", [])
            content = state.get("content", "")
            context = state.get("context", {})
            action = state.get("action", "generate")
            iterations = state.get("iterations", 0)
            
            # Create system message based on action
            system_prompts = {
                "generate": """You are an expert writing assistant. When asked to generate text, provide ONLY the clean, well-written content that should be inserted directly into the document. 

DO NOT include:
- Explanatory text like "Here's a draft" or "Based on your prompt"
- Meta-commentary about the writing process
- Markdown headers or formatting (the editor will handle formatting)
- References to the prompt or instructions

DO provide:
- Clean, polished prose that directly fulfills the request
- Natural paragraph breaks using double line breaks
- Content that flows seamlessly as if written by the user

Available tools:
- analyze_text_structure: Analyze text structure and organization
- suggest_improvements: Get specific improvement suggestions  
- extract_key_themes: Identify key themes and topics

Focus on producing clean, insertable content only.""",
                
                "edit": """You are an expert editor. Help users improve and refine their existing text.
                
Available tools:
- analyze_text_structure: Analyze current text structure
- suggest_improvements: Get targeted improvement suggestions
- extract_key_themes: Understand content themes

Focus on clarity, coherence, and effective communication. Format your responses using markdown for better readability.""",
                
                "improve": """You are an expert writing improvement specialist. When asked to improve text, provide ONLY the improved version of the content that should replace the original text in the document.

DO NOT include:
- Explanatory text about what you changed or why
- Meta-commentary about the improvement process
- Markdown headers or formatting (the editor will handle formatting)
- Analysis or suggestions - just the improved content

DO provide:
- Clean, polished prose that improves upon the original
- Natural paragraph breaks using double line breaks
- Content that flows seamlessly as if written by the user
- Enhanced clarity, engagement, and readability

Available tools:
- analyze_text_structure: Analyze text structure and organization
- suggest_improvements: Get specific improvement suggestions  
- extract_key_themes: Identify key themes and topics

Focus on producing clean, improved content only."""
            }
            
            system_prompt = system_prompts.get(action, system_prompts["generate"])
            
            # Create the conversation messages if not already present
            if not messages:
                if action == "generate":
                    user_message = f"Please help me generate text based on this prompt: {content}"
                    if context.get("style"):
                        user_message += f"\n\n**Style:** {context['style']}"
                    if context.get("length"):
                        user_message += f"\n**Length:** {context['length']}"
                elif action == "edit":
                    user_message = f"Please help me edit and improve this text:\n\n{content}"
                    if context.get("focus"):
                        user_message += f"\n\n**Focus on:** {context['focus']}"
                else:  # improve
                    user_message = f"Please help me improve this text:\n\n{content}"
                    if context.get("aspect"):
                        user_message += f"\n\n**Specific aspect:** {context['aspect']}"
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ]
            
            # Generate response
            if self.llm:
                response = await self.llm.ainvoke(messages)
                messages.append(response)
            else:
                # Mock response for development without API key
                if action == "generate":
                    # Clean content suitable for direct insertion into editor
                    mock_response = """This is a well-crafted piece of writing that demonstrates the capabilities of the AI writing assistant. The content flows naturally and provides valuable information while maintaining an engaging tone throughout.

The writing assistant can adapt to various styles and requirements, ensuring that the generated content meets your specific needs. Whether you're looking for formal academic writing, casual blog posts, or creative storytelling, the system can produce high-quality content.

This example showcases clean, insertable text that integrates seamlessly into your document without requiring additional formatting or editing."""
                elif action == "improve":
                    # Clean improved content suitable for direct insertion into editor
                    mock_response = """This represents a significantly enhanced version of your original text, featuring improved clarity, better flow, and more engaging language throughout. The content has been carefully refined to maintain your core message while elevating the overall quality and readability.

The enhanced writing demonstrates stronger transitions between ideas, more precise word choices, and a more compelling narrative structure. Each sentence contributes meaningfully to the overall piece while maintaining consistency in tone and style.

This improved version showcases the writing assistant's ability to transform good content into exceptional prose that resonates more effectively with readers and achieves your communication objectives."""
                else:
                    # Formatted response for edit actions
                    mock_response = f"**Mock Response for {action}**\n\nThis is a simulated writing assistant response with *proper markdown formatting* for development purposes.\n\n### Key Features\n- ✅ Proper message structure\n- ✅ Markdown formatting\n- ✅ SystemMessage usage\n\n> This demonstrates how responses will be formatted when the API is configured."
                
                response = AIMessage(content=mock_response)
                messages.append(response)
            
            return {
                "messages": messages,
                "iterations": iterations + 1
            }
            
        except Exception as e:
            logger.error(f"Agent node error: {str(e)}")
            error_message = AIMessage(content=f"I encountered an error: {str(e)}")
            return {
                "messages": messages + [error_message],
                "iterations": iterations + 1
            }

    def should_continue(self, state: WritingState) -> str:
        """Determine whether to continue with tools or end"""
        messages = state.get("messages", [])
        iterations = state.get("iterations", 0)
        max_iterations = state.get("max_iterations", 3)
        
        # Check if we've hit max iterations
        if iterations >= max_iterations:
            return "end"
        
        # Check if the last message has tool calls
        if messages and hasattr(messages[-1], 'tool_calls') and messages[-1].tool_calls:
            return "continue"
        
        return "end"

    async def generate_text(self, prompt: str, context: Dict = None) -> AsyncGenerator[str, None]:
        """Generate text based on prompt with streaming"""
        try:
            if context is None:
                context = {}
                
            initial_state = WritingState(
                messages=[],
                content=prompt,
                context=context,
                action="generate",
                iterations=0,
                max_iterations=3
            )
            
            # Stream the results
            async for output in self.graph.astream(initial_state):
                for node_name, node_output in output.items():
                    if node_name == "agent" and "messages" in node_output:
                        messages = node_output["messages"]
                        if messages and isinstance(messages[-1], AIMessage):
                            content = messages[-1].content
                            if content:
                                # Simulate streaming by yielding chunks
                                words = content.split()
                                for word in words:
                                    yield word + " "
                                    await asyncio.sleep(0.05)  # Small delay for streaming effect
                                    
        except Exception as e:
            logger.error(f"Generate text error: {str(e)}")
            yield f"Error generating text: {str(e)}"

    async def edit_text(self, content: str, context: Dict = None) -> AsyncGenerator[str, None]:
        """Edit existing text with streaming"""
        try:
            if context is None:
                context = {}
                
            initial_state = WritingState(
                messages=[],
                content=content,
                context=context,
                action="edit",
                iterations=0,
                max_iterations=3
            )
            
            async for output in self.graph.astream(initial_state):
                for node_name, node_output in output.items():
                    if node_name == "agent" and "messages" in node_output:
                        messages = node_output["messages"]
                        if messages and isinstance(messages[-1], AIMessage):
                            content = messages[-1].content
                            if content:
                                words = content.split()
                                for word in words:
                                    yield word + " "
                                    await asyncio.sleep(0.05)
                                    
        except Exception as e:
            logger.error(f"Edit text error: {str(e)}")
            yield f"Error editing text: {str(e)}"

    async def improve_text(self, content: str, context: Dict = None) -> AsyncGenerator[str, None]:
        """Improve existing text with streaming"""
        try:
            if context is None:
                context = {}
                
            initial_state = WritingState(
                messages=[],
                content=content,
                context=context,
                action="improve",
                iterations=0,
                max_iterations=3
            )
            
            async for output in self.graph.astream(initial_state):
                for node_name, node_output in output.items():
                    if node_name == "agent" and "messages" in node_output:
                        messages = node_output["messages"]
                        if messages and isinstance(messages[-1], AIMessage):
                            content = messages[-1].content
                            if content:
                                words = content.split()
                                for word in words:
                                    yield word + " "
                                    await asyncio.sleep(0.05)
                                    
        except Exception as e:
            logger.error(f"Improve text error: {str(e)}")
            yield f"Error improving text: {str(e)}" 