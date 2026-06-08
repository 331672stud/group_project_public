import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict


df = pd.read_csv("vulnerability_fix_dataset.csv")

print("General statistics:\n")
print(df.describe())
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nVulnerability distribution:")
print(df["vulnerability_type"].value_counts())

# Check for nulls
print(f"\nNull values:\n{df.isnull().sum()}")

# Check code length distribution
df["code_length"] = df["vulnerable_code"].str.len()
print(f"\nCode length stats:\n{df['code_length'].describe()}")

negatives = df[["fixed_code"]].copy()
negatives.columns = ["code"]
negatives["label"] = "No Vulnerability"
negatives["is_vulnerable"] = False

positives = df[["vulnerable_code", "vulnerability_type"]].copy()
positives.columns = ["code", "label"]
positives["is_vulnerable"] = True

combined = pd.concat([positives, negatives], ignore_index=True)

combined = combined.sample(frac=1, random_state=4213).reset_index(drop=True)

print(f"Total examples: {len(combined)}")
print(f"Vulnerable: {combined['is_vulnerable'].sum()}")
print(f"Clean: {(~combined['is_vulnerable']).sum()}")


def format_example(row):
    instruction = (
        "Analyze the following code and determine whether it contains a security vulnerability. "
        "If a vulnerability is present, state its exact type from this list: "
        "SQL Injection, Cross-Site Scripting (XSS), Command Injection, Path Traversal, "
        "Buffer Overflow, Insecure Deserialization. "
        "If no vulnerability is present, respond with: No Vulnerability."
    )

    code = row["code"].strip()
    label = row["label"].strip()

    prompt = f"### Instruction:\n{instruction}\n\n### Code:\n{code}\n\n### Response:\n{label}"
    return prompt


combined["text"] = combined.apply(format_example, axis=1)

# Check a sample
print(combined["text"].iloc[0])
print("\n---\n")
print(f"Average formatted length: {combined['text'].str.len().mean():.0f} chars")


# First split: 85% train, 15% temp
train_df, temp_df = train_test_split(
    combined,
    test_size=0.15,
    stratify=combined["label"],
    random_state=42
)

# Second split: split the 15% into 10% val and 5% test
val_df, test_df = train_test_split(
    temp_df,
    test_size=0.33,
    stratify=temp_df["label"],
    random_state=42
)

print(f"Train:      {len(train_df):>6} examples")
print(f"Validation: {len(val_df):>6} examples")
print(f"Test:       {len(test_df):>6} examples")

# Save to disk
# train_df.to_csv("data/train.csv", index=False)
# val_df.to_csv("data/val.csv", index=False)
# test_df.to_csv("data/test.csv", index=False)

train_dataset = Dataset.from_pandas(train_df[["text"]])
val_dataset   = Dataset.from_pandas(val_df[["text"]])
test_dataset  = Dataset.from_pandas(test_df[["text"]])

dataset = DatasetDict({
    "train": train_dataset,
    "validation": val_dataset,
    "test": test_dataset
})

# Save to disk for reuse
dataset.save_to_disk("data/hf_dataset")
print(dataset)