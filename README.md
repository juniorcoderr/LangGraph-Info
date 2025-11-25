# 🚀 LangGraph + Groq Agentic AI System

### **A Complete Workflow: Tools, Memory, Conditional Logic & Human-in-the-Loop Interrupts**

This repository showcases a fully working **Agentic AI system** built using **LangGraph** and **Groq Llama-3.3-70B**, demonstrating how modern AI agents can reason, call tools, store memory, route logic, and pause for human approval.

The project evolves step-by-step—from simple graph execution to a production-like multi-turn agent with tools and interrupt handling.

---

## 🔥 Features Implemented

### ✅ **1. LangGraph Basics**

* Custom `State` with typed message history
* Single and multi-node graph execution
* START → Node → END execution flow

### ✅ **2. Conditional Routing**

* Automatic branching using `add_conditional_edges`
* Dynamic selection between multiple nodes
* Perfect for multi-tool or multi-agent workflows

### ✅ **3. Tool Calling with LLM**

Integrated real tools such as:

* `get_stock_price` → returns live-like stock prices
* `buy_stocks` → performs a buy action with confirmation

LLM automatically decides when to call a tool using LangGraph’s `tools_condition`.

### ✅ **4. Memory Support**

* Added persistent memory using `MemorySaver`
* Multi-turn conversations linked by `thread_id`
* Enables follow-up questions like *“Add 10 RIL stocks to the previous total.”*

### ✅ **5. Human-in-the-Loop Interrupts**

A production-grade feature:

* Agent pauses using `interrupt()`
* Asks user for approval (Yes/No)
* Resumes exactly where it left off using `Command(resume=...)`

Perfect for real-world workflows involving approvals, verifications, or transactions.

---

## 🧠 Workflow Summary

1. **User sends a message**
2. **Groq LLM processes it** using the chatbot node
3. If needed, LLM calls a **tool** (e.g., price lookup)
4. If buying is requested, graph **pauses using interrupt**
5. User approves/denies
6. Graph **resumes** and completes the task
7. Memory ensures context stays alive across multiple queries

---

## 🚀 Why This Project Matters

This repo is a perfect reference for anyone building:

* AI agents
* Financial assistants
* Multi-tool orchestrators
* Approval-based workflows
* LangGraph projects with memory and Groq speed

It demonstrates **real enterprise patterns**: persistent state, tool orchestration, decision branching, and human control.
