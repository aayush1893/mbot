# Scenario-Based Mental Health Screening

Transforms PHQ-9 and GAD-7 questions into scenario-based formats to reduce response bias while maintaining clinical validity.

## Overview

This tool uses AI to convert standard mental health screening questions into concrete, situational formats. For example:
- Standard: "Feeling nervous, anxious, or on edge?"
- Scenario: "At work or school, do small hassles set you on edge?"

## Key Features

- AI-powered question generation (OpenAI API)
- Maintains standard PHQ-9/GAD-7 scoring (0-21 for GAD-7, 0-27 for PHQ-9)
- Fallback to pre-validated questions if AI fails
- Built with Streamlit for easy deployment

## Installation
```bash
pip install -r requirements.txt
export OPENAI_API_KEY='your-key-here'
streamlit run gamified_mental_health_bot.py
```

## Research Purpose

**IMPORTANT:** This is a research tool, not validated for clinical use.

The scenario-based approach aims to:
- Reduce response bias in digital screening
- Prevent pattern recognition in repeat assessments
- Improve accuracy through concrete questions

## Citation

If you use this in research:
