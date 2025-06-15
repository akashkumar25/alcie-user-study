# ALCIE User Study: Catastrophic Forgetting in Fashion Caption Generation

This repository contains the human evaluation study for analyzing catastrophic forgetting effects in fashion image captioning models trained with different sampling strategies.

## 🎯 Study Overview

- **Research Question**: How do different training data sampling methods (random, diversity, uncertainty) affect caption quality and catastrophic forgetting?
- **Dataset**: 24 carefully selected fashion images across 6 categories
- **Methods**: Random, Diversity, and Uncertainty sampling
- **Evaluation**: Human preference ratings and quality assessments

## 📊 Study Design

### Categories & Catastrophic Forgetting Risk
- **Phase 1 - Accessories** (6 samples): Highest CF risk
- **Phase 2 - Bottoms** (5 samples): Very high CF risk  
- **Phase 3 - Dresses** (4 samples): High CF risk
- **Phase 4 - Outerwear** (3 samples): Medium CF risk
- **Phase 5 - Shoes** (3 samples): Low CF risk
- **Phase 6 - Tops** (3 samples): Lowest CF risk

## 🚀 Running the Study

### Local Development
```bash
pip install -r requirements.txt
streamlit run src/alcie_study_app.py
```

### Streamlit Cloud Deployment
This app is deployed at: [Your Streamlit URL will appear here]

## 📁 Repository Structure

```
alcie-user-study/
├── data/
│   └── alcie_diverse_dataset.json    # Study dataset
├── src/
│   └── alcie_study_app.py           # Streamlit application
├── docs/
│   └── study_protocol.md            # Detailed study protocol
├── results/
│   └── (study results will be saved here)
├── requirements.txt                  # Python dependencies
└── README.md                        # This file
```

## 🔬 Research Context

This study is part of research on catastrophic forgetting in continual learning for fashion image captioning. The goal is to understand how different training data sampling strategies affect model performance across sequential learning phases.

## 📈 Expected Outcomes

- Quantitative analysis of caption quality across categories
- Detection of catastrophic forgetting patterns
- Comparison of sampling method effectiveness
- Insights for improving continual learning in fashion AI

## 📞 Contact

For questions about this study, please contact: [Your email]

## 📄 Citation

If you use this dataset or findings from this study, please cite:
```bibtex
[Your citation will go here]
```
