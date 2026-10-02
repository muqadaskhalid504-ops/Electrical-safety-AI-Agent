# ⚡ Electrical Safety AI Agent

An AI-powered electrical safety assistant that analyzes user-reported electrical problems, identifies potential hazards, classifies the risk level, and provides safe safety guidance.

## 🎯 Problem Statement

Electrical problems such as overheating sockets, repeated circuit breaker trips, sparks, damaged cables, and electric shocks can create serious safety hazards.

Many users do not know whether an electrical problem is minor or requires immediate professional attention.

## 💡 Proposed Solution

The **Electrical Safety AI Agent** uses Artificial Intelligence and Retrieval-Augmented Generation (RAG) to analyze electrical problems and provide safety-focused guidance.

The system:

1. Accepts the user's electrical problem.
2. Identifies the problem category.
3. Retrieves relevant electrical safety information.
4. Uses an AI model to analyze the situation.
5. Determines a risk level.
6. Provides safety precautions.
7. Recommends professional help when required.
8. Allows the user to download the analysis as a report.

## 🤖 AI Agent

The AI agent is designed specifically for electrical safety analysis.

It considers hazards such as:

- ⚡ Electric shock
- 🔥 Electrical fire
- ✨ Sparks and arcing
- 🌡️ Overheating
- 🔌 Electrical overloading
- 🔧 Damaged equipment
- 🔴 Circuit breaker problems
- ⚠️ Exposed electrical parts

The agent classifies situations into four risk levels:

- 🟢 Low
- 🟡 Medium
- 🔴 High
- 🚨 Emergency

## 📚 RAG-Based Knowledge

The application uses a local electrical safety knowledge base.

The system retrieves relevant information from:

- OSHA electrical safety guidance
- HSE electrical safety guidance
- General electrical safety and hazard-prevention practices

### RAG Workflow

```text
User Problem
     ↓
Problem Category
     ↓
Knowledge Retrieval
     ↓
Relevant Safety Information
     ↓
AI Agent Analysis
     ↓
Risk Detection
     ↓
Safety Guidance
     ↓
Safety Decision
