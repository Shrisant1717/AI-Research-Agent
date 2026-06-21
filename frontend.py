import streamlit as st
from ai_researcher_2 import INITIAL_PROMPT, graph, config
import logging
from langchain_core.messages import AIMessage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(page_title="Research AI Agent", page_icon="📄")
st.title("📄 Research AI Agent")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    logger.info("Initialized chat history")

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

# Display previous chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("What research topic would you like to explore?")

if user_input:

    # Log user input
    logger.info(f"User input: {user_input}")

    # Save user message
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare agent input
    chat_input = {
        "messages": [
            {"role": "system", "content": INITIAL_PROMPT}
        ] + st.session_state.chat_history
    }

    logger.info("Starting agent processing...")

    # Assistant message placeholder for streaming
    assistant_placeholder = st.chat_message("assistant").empty()

    full_response = ""

    # Stream response from LangGraph
    for s in graph.stream(chat_input, config, stream_mode="values"):

        message = s["messages"][-1]

        # Log tool calls
        if getattr(message, "tool_calls", None):
            for tool_call in message.tool_calls:
                logger.info(f"Tool call: {tool_call['name']}")

        # Handle AI response
        if isinstance(message, AIMessage) and message.content:

            text_content = ""

            # Case 1: plain string
            if isinstance(message.content, str):
                text_content = message.content

            # Case 2: structured content (list)
            elif isinstance(message.content, list):
                for item in message.content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content += item.get("text", "")

            # Case 3: fallback
            else:
                text_content = str(message.content)

            # Update streaming response
            full_response += text_content
            assistant_placeholder.markdown(full_response)

    # Save assistant response to chat history
    if full_response:
        st.session_state.chat_history.append(
            {"role": "assistant", "content": full_response}
        )