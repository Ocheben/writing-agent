"""
LangGraph Studio compatible graph definition for the Writing Agent.
This file exposes the compiled graph for LangGraph Studio.
"""

import asyncio
import json
from typing import Dict, List, TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import os

# Import config for API key
from config import settings

# Initialize LangSmith tracing for Studio
if settings.langsmith_api_key and settings.langsmith_tracing:
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    
    try:
        import langsmith
        print(f"✅ LangSmith tracing initialized for LangGraph Studio: {settings.langsmith_project}")
    except ImportError:
        print("⚠️ LangSmith not installed. Install with: pip install langsmith")
else:
    print("⚠️ LangSmith tracing disabled in Studio. Set LANGSMITH_API_KEY and LANGSMITH_TRACING=true to enable.")

# Define the state structure
class WritingState(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation messages"]
    content: str
    context: Dict
    action: str
    iterations: int
    max_iterations: int

# Define writing tools (same as in agent.py)
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
    
    # Simple keyword extraction
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

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    streaming=True,
    api_key=settings.openai_api_key
) if settings.openai_api_key else None

def agent_node(state: WritingState) -> Dict:
    """The main agent reasoning node"""
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
    if llm:
        try:
            response = llm.invoke(messages)
            messages.append(response)
        except Exception as e:
            # Fallback to mock response if API call fails
            error_response = AIMessage(content=f"⚠️ **API Error:** {str(e)}\n\nFalling back to mock response:\n\n{_generate_mock_response(action, content, context)}")
            messages.append(error_response)
    else:
        # Enhanced mock response with proper markdown formatting
        mock_content = _generate_mock_response(action, content, context)
        response = AIMessage(content=mock_content)
        messages.append(response)
    
    return {
        "messages": messages,
        "iterations": iterations + 1
    }

def _generate_mock_response(action: str, content: str, context: Dict) -> str:
    """Generate a well-formatted mock response with markdown"""
    if action == "generate":
        # For generate actions, return clean content suitable for direct insertion
        style = context.get("style", "general")
        length = context.get("length", "medium")
        
        if "history" in content.lower():
            return """The study of history reveals the intricate tapestry of human civilization, woven through countless decisions, conflicts, and innovations that have shaped our world. From the rise and fall of ancient empires to the technological revolutions that continue to transform society, history provides essential context for understanding contemporary challenges and opportunities.

Historical analysis offers valuable insights into patterns of human behavior, the consequences of political decisions, and the forces that drive social change. By examining past events, we can better appreciate the complexity of modern issues and make more informed choices about our collective future.

The preservation and study of historical records ensures that future generations can learn from both the triumphs and mistakes of those who came before them, fostering a deeper appreciation for the ongoing human experience."""
        
        elif "technology" in content.lower():
            return """Technology has fundamentally transformed the way we live, work, and communicate in the modern era. From smartphones that connect us instantly across vast distances to artificial intelligence systems that assist with complex problem-solving, technological innovation continues to accelerate at an unprecedented pace.

The digital revolution has created new opportunities for creativity, collaboration, and learning while also presenting challenges related to privacy, security, and the future of work. As we navigate this rapidly evolving landscape, it becomes increasingly important to thoughtfully consider both the benefits and implications of emerging technologies.

Understanding and adapting to technological change remains essential for individuals and organizations seeking to thrive in an interconnected, digitally-driven world."""
        
        else:
            # Generic content based on prompt
            return f"""This is a thoughtfully composed piece of writing that addresses your specific request. The content has been crafted to meet your requirements while maintaining clarity and engagement throughout.

The writing flows naturally from one idea to the next, building upon key concepts and providing readers with valuable insights. Each paragraph contributes meaningfully to the overall message while maintaining a consistent tone and style.

This approach ensures that the final piece serves its intended purpose effectively, whether for informational, persuasive, or creative objectives. The content can be easily integrated into your broader work or stand alone as a complete piece."""
    
    elif action == "edit":
        return f"""# Editorial Suggestions

## Original Text Analysis

I've reviewed your text and identified several areas for improvement.

### Structure Improvements

- **Paragraph organization:** Consider reorganizing for better flow
- **Transitions:** Add connecting phrases between ideas
- **Clarity:** Some sentences could be simplified

### Content Suggestions

1. **Opening:** Strengthen the introduction with a hook
2. **Body:** Expand on key points with examples
3. **Conclusion:** Summarize main takeaways

### Revised Version

Here's a sample of how your text might be improved:

> [Original text would be shown here with suggested edits highlighted]

### Next Steps

- Review the suggested changes
- Consider the overall message clarity
- Ensure consistent tone throughout

---
*Analysis by Writing Agent (Mock Mode)*"""
    
    else:  # improve
        # For improve actions, return clean improved content suitable for direct insertion
        if "art" in content.lower() and "describe" in content.lower():
            return """Describing art involves delving into its myriad aspects: the visual elements, the emotional response it evokes, its historical context, and the artist's intentions, among others. To craft a comprehensive piece on this topic, we can structure our text around several key themes.

Introduction to Art - Definition and Scope: Begin by defining art in broad terms, acknowledging its diverse forms—painting, sculpture, literature, music, and more. Emphasize art's role in human expression and cultural identity.

Purpose of Art: Discuss why art is created, touching on themes of expression, communication, societal reflection, and aesthetic pleasure.

Visual Elements of Art - Color, Form, Line, Shape, Space, Texture, and Value: Explore these foundational elements that artists use to create their pieces. Describe how these elements interact and how they contribute to the overall impression of the artwork.

Emotional and Intellectual Responses - Personal Interpretation: Discuss how art is subjective and can evoke different emotions and thoughts in each viewer. Mention the role of personal experiences and cultural background in interpretation.

Historical Context and Evolution - Art Movements and Styles: Briefly chart the evolution of art, mentioning key movements such as Renaissance, Impressionism, and Modernism, and how they reflected or influenced societal changes.

The Role of the Critic and the Audience - Art Criticism: Introduce the concept of art criticism and its role in shaping public perception and understanding of art.

Audience Engagement: Discuss how different audiences engage with art and the importance of accessibility in art appreciation."""
        
        elif "technology" in content.lower():
            return """Technology has fundamentally transformed how we live, work, and communicate in the modern era. From smartphones that connect us instantly across vast distances to artificial intelligence systems that assist with complex problem-solving, technological innovation continues to accelerate at an unprecedented pace.

The digital revolution has created unprecedented opportunities for creativity, collaboration, and learning while simultaneously presenting significant challenges related to privacy, security, and the future of employment. As we navigate this rapidly evolving technological landscape, it becomes increasingly crucial to thoughtfully consider both the remarkable benefits and potential implications of emerging technologies.

Understanding and effectively adapting to technological change remains absolutely essential for individuals and organizations seeking to thrive in our interconnected, digitally-driven world. Those who embrace technological literacy and maintain adaptability will be best positioned for success in the coming decades."""
        
        else:
            # Generic improved content
            return """This thoughtfully composed piece of writing effectively addresses your specific request while demonstrating enhanced clarity and engagement throughout. The content has been carefully refined to meet your requirements while maintaining superior readability and flow.

The writing progresses naturally from one compelling idea to the next, building upon key concepts and providing readers with valuable, actionable insights. Each paragraph contributes meaningfully to the overall message while maintaining consistent tone and elevated style.

This refined approach ensures that the final piece serves its intended purpose with maximum effectiveness, whether for informational, persuasive, or creative objectives. The improved content integrates seamlessly into your broader work while standing confidently as a complete, polished piece."""

def should_continue(state: WritingState) -> str:
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

# Create the state graph
workflow = StateGraph(WritingState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# Set entry point
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

# Add edge from tools back to agent
workflow.add_edge("tools", "agent")

# Compile the graph (without custom checkpointer for Studio compatibility)
graph = workflow.compile() 