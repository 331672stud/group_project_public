from unsloth import FastLanguageModel
from datasets import load_from_disk
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score
)
import seaborn as sns
import matplotlib.pyplot as plt
import torch

MODEL_PATH  = "./lora_adapters"
MAX_SEQ_LEN = 1024 



model, tokenizer = FastLanguageModel.from_pretrained(
    model_name      = MODEL_PATH,
    max_seq_length  = MAX_SEQ_LEN,
    dtype           = None,
    load_in_4bit    = True,
)

# Enable fast inference mode (Unsloth-specific)
FastLanguageModel.for_inference(model)

dataset = load_from_disk("data/hf_dataset")
test_df = dataset["test"].to_pandas()

VALID_LABELS = [
    "SQL Injection",
    "Cross-Site Scripting (XSS)",
    "Command Injection",
    "Path Traversal",
    "Buffer Overflow",
    "Insecure Deserialization",
    "No Vulnerability",
]

def predict(code_snippet: str) -> str:
    instruction = (
        "Analyze the following code and determine whether it contains a security vulnerability. "
        "If a vulnerability is present, state its exact type from this list: "
        "SQL Injection, Cross-Site Scripting (XSS), Command Injection, Path Traversal, "
        "Buffer Overflow, Insecure Deserialization. "
        "If no vulnerability is present, respond with: No Vulnerability."
    )

    prompt = f"### Instruction:\n{instruction}\n\n### Code:\n{code_snippet}\n\n### Response:\n"

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens = 30,    # Labels are short — no need for more
            temperature    = 0.1,   # Low temperature = more deterministic
            do_sample      = True,
            pad_token_id   = tokenizer.eos_token_id,
        )

    # Decode only the newly generated tokens
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    # Snap to nearest valid label
    for label in VALID_LABELS:
        if label.lower() in response.lower():
            return label

    return "Unknown"  # Fallback — should be rare after training




print("Running inference on test set...")
predictions = []
ground_truth = []

print("Size of test_df:", test_df.shape)

for _, row in test_df.iterrows():
    # Extract just the code from the formatted text
    code = row["text"].split("### Code:\n")[1].split("\n\n### Response:")[0]
    true_label = row["text"].split("### Response:\n")[1].strip()

    pred_label = predict(code)
    predictions.append(pred_label)
    ground_truth.append(true_label)

# Overall accuracy
acc = accuracy_score(ground_truth, predictions)
macro_f1 = f1_score(ground_truth, predictions, average="macro")

print(f"\nOverall Accuracy: {acc:.4f}")
print(f"Macro F1 Score:   {macro_f1:.4f}")

# Per-class breakdown
print("\nClassification Report:")
print(classification_report(ground_truth, predictions, target_names=VALID_LABELS))

# Confusion matrix
cm = confusion_matrix(ground_truth, predictions, labels=VALID_LABELS)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=VALID_LABELS,
            yticklabels=VALID_LABELS, cmap="Blues")
plt.title("Confusion Matrix — Vulnerability Detector")
plt.ylabel("True Label")
plt.xlabel("Predicted Label")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
print("\nConfusion matrix saved to confusion_matrix.png")