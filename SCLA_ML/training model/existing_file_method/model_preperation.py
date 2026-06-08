from transformers import AutoTokenizer
from datasets import load_from_disk

MAX_SEQ_LEN  = 1024
TOKENIZER_ID = "unsloth/Meta-Llama-3.1-8B-Instruct"

def tokenize(batch):
    # Reconstructed inside the worker — no closure over __main__ variables
    tok = AutoTokenizer.from_pretrained(TOKENIZER_ID)
    tok.pad_token    = tok.eos_token
    tok.padding_side = "right"
    encoded = tok(
        batch["text"],
        truncation     = True,
        max_length     = MAX_SEQ_LEN,
        padding        = False,
        return_tensors = None,
    )
    return {
        "input_ids":      encoded["input_ids"],
        "attention_mask": encoded["attention_mask"],
    }

if __name__ == "__main__":

    print("Loading dataset...")
    dataset = load_from_disk("data/hf_dataset")

    print("Tokenising with multiple CPU workers...")
    dataset = dataset.map(
        tokenize,
        batched  = True,
        num_proc = 4,
        desc     = "Tokenising",
    )

    dataset.save_to_disk("data/hf_dataset_tokenised")
    print("Done. Saved to data/hf_dataset_tokenised")
















# from unsloth import FastLanguageModel
# import torch
# from datasets import load_from_disk
# from trl import SFTTrainer
# from transformers import TrainingArguments, DataCollatorForSeq2Seq
# import time

# # ── Configuration ──────────────────────────────────────────────────────────────
# MODEL_NAME    = "unsloth/Meta-Llama-3.1-8B-Instruct"
# MAX_SEQ_LEN   = 2048   # Max token length; reduce to 1024 if VRAM is tight
# DTYPE         = None   # Auto-detect: Float16 on older GPUs, BFloat16 on Ampere+
# LOAD_IN_4BIT  = True   # Enables QLoRA; halves VRAM usage
# # ───────────────────────────────────────────────────────────────────────────────

# if __name__ == "__main__":

#     model, tokenizer = FastLanguageModel.from_pretrained(
#         model_name      = MODEL_NAME,
#         max_seq_length  = MAX_SEQ_LEN,
#         dtype           = DTYPE,
#         load_in_4bit    = LOAD_IN_4BIT,
#     )

#     print(f"Model loaded: {MODEL_NAME}")
#     print(f"Parameters: {model.num_parameters() / 1e9:.2f}B")


#     model = FastLanguageModel.get_peft_model(
#         model,
#         r                   = 16,        # LoRA rank — higher = more capacity but more VRAM
#         target_modules      = [          # Which attention/MLP layers to adapt
#             "q_proj", "k_proj", "v_proj", "o_proj",
#             "gate_proj", "up_proj", "down_proj"
#         ],
#         lora_alpha          = 16,        # Scaling factor — typically equal to r
#         lora_dropout        = 0.05,      # Regularisation
#         bias                = "none",    # Don't train bias terms
#         use_gradient_checkpointing = "unsloth",  # Unsloth's memory-efficient checkpointing
#         random_state        = 42,
#         use_rslora          = False,     # Rank-stabilised LoRA — set True for r > 16
#         loftq_config        = None,
#     )

#     print(model.print_trainable_parameters())

#     dataset.save_to_disk("data/hf_dataset_tokenised")
#     # FINE-TUNING
