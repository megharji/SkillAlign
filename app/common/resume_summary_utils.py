from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Global variables to avoid multiple loads
_MODEL = None
_TOKENIZER = None

def load_model():
    global _MODEL, _TOKENIZER
    if _MODEL is None:
        # Small or Base version for low RAM
        model_name = "google/flan-t5-small"  # base is heavier
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def get_summary(resume_text: str, jd_text: str) -> str:
    """
    Returns a human-readable summary of matches, missing skills, and improvement suggestions.
    """
    load_model()

    prompt = f"""
Compare resume with job description.

1. Matching skills
2. Missing skills
3. Improvement suggestion

Resume:
{resume_text}

Job Description:
{jd_text}
"""
    inputs = _TOKENIZER(prompt, return_tensors="pt", truncation=True)

    # Check if GPU available, otherwise CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    _MODEL.to(device)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    outputs = _MODEL.generate(**inputs, max_new_tokens=200)
    summary = _TOKENIZER.decode(outputs[0], skip_special_tokens=True)

    return summary
