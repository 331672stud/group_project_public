from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = "./lora_adapters",
    max_seq_length = 1024,
    dtype          = None,
    load_in_4bit   = True,
)

# Export directly to GGUF — skips the broken merged_16bit save entirely
model.save_pretrained_gguf(
    "vuln_detector",          # Output folder name
    tokenizer,
    quantization_method = "q4_k_m",   # Same as Q4_K_M in llama.cpp
)

print("GGUF saved to ./vuln_detector")








# # In a separate script: merge_and_export.py
# from unsloth import FastLanguageModel
# import torch

# model, tokenizer = FastLanguageModel.from_pretrained(
#     model_name   = "./lora_adapters",
#     max_seq_length = 2048,
#     dtype        = None,
#     load_in_4bit = True,
# )

# # Merge LoRA weights into base model (this undoes the adapter separation)
# model = model.merge_and_unload()

# # Save as full 16-bit model (needed for GGUF conversion)
# model.save_pretrained_merged(
#     "./merged_model",
#     tokenizer,
#     save_method = "merged_16bit",  # Options: "merged_16bit", "merged_4bit", "lora"
# )

# print("Merged model saved to ./merged_model")