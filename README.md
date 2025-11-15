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
Sisodia, A. (2024). Scenario-Based Mental Health Screening.
GitHub: https://github.com/aayush1893/mbot
Related paper:

## Validated Instruments

Original instruments:
- PHQ-9: Kroenke et al. (2001). J Gen Intern Med, 16(9):606-613
- GAD-7: Spitzer et al. (2006). Arch Intern Med, 166(10):1092-1097

## License

MIT License

## Author

Aayush Sisodia, MSHI, BDS  
Business Analytics Advisor, Cigna/Evernorth Health Services

## Disclaimer

This tool is for research purposes only. For clinical screening, use the standard validated PHQ-9 and GAD-7 instruments.
