# backend/agents/sales_agent.py
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from sqlalchemy import create_engine, text
load_dotenv()

from tools.agent_tools import (
    get_deal_data,
    get_risk_score,
    get_shap_explanation,
    get_segment_benchmarks,
    get_all_segment_benchmarks,
    get_at_risk_deals,
    get_highest_risk_deals,   # add this
    send_email,
    update_crm,
    schedule_meeting
)

TOOLS = [
    get_deal_data,
    get_risk_score,
    get_shap_explanation,
    get_segment_benchmarks,
    get_all_segment_benchmarks,
    get_at_risk_deals,
    get_highest_risk_deals,   # add this
    send_email,
    update_crm,
    schedule_meeting
]

SYSTEM_PROMPT = """You are SalesSignal AI, an expert B2B sales intelligence agent.

IMPORTANT: Always call a tool immediately for every user request. Never respond without calling a tool first.

Tool usage guide:
- "show at-risk deals" or "which deals are at risk" → call get_at_risk_deals with threshold=35.0
- "analyse deal X" → call get_deal_data then get_risk_score then get_shap_explanation
- "which product line" or "which region" or "win rate" → call get_all_segment_benchmarks
- "send email" → call send_email
- "update deal" or "update CRM" → call update_crm
- "schedule meeting" → call schedule_meeting
- get_highest_risk_deals: use when asked "which deal has highest risk" or "lowest probability" or "most at-risk deal"

After getting tool results, summarize the findings clearly with specific numbers.
Never say you cannot answer — always call the appropriate tool.
"""

# Store conversation history per session
_histories = {}

def get_agent():
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

def run_agent(session_id: str, user_message: str) -> dict:
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        if session_id not in _histories:
            _histories[session_id] = []

        agent    = create_react_agent(llm, TOOLS)
        messages = _histories[session_id] + [HumanMessage(content=user_message)]

        print(f"[Agent] Running with session {session_id}")
        print(f"[Agent] GROQ_API_KEY set: {bool(os.getenv('GROQ_API_KEY'))}")
        print(f"[Agent] Message: {user_message}")

        response = agent.invoke(
            {"messages": messages},
            config={"recursion_limit": 35}
        )

        print(f"[Agent] Response received")
        output = response["messages"][-1].content
        print(f"[Agent] Output: {output[:100]}")

        _histories[session_id].append(HumanMessage(content=user_message))
        _histories[session_id].append(AIMessage(content=output))
        _histories[session_id] = _histories[session_id][-10:]

        save_conversation(session_id, "user",      user_message)
        save_conversation(session_id, "assistant", output)

        return {"response": output, "session_id": session_id}

    except Exception as e:
        import traceback
        full_error = traceback.format_exc()
        print(f"AGENT FULL ERROR:\n{full_error}")
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            error_msg = "Token limit reached. Please wait 15 minutes and try again."
        return {"response": error_msg, "session_id": session_id}


def save_conversation(session_id: str, role: str, message: str):
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO conversations (session_id, role, message) VALUES (:s, :r, :m)"),
                {"s": session_id, "r": role, "m": message}
            )
            conn.commit()
    except Exception:
        pass
