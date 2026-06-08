import os
os.environ["UNSLOTH_USE_FUSED_CE_LOSS"] = "0"
os.environ["UNSLOTH_DISABLE_FUSED_CE"]  = "0"

from unsloth import FastLanguageModel
import torch
from datasets import load_from_disk
from trl import SFTTrainer
from transformers import TrainingArguments
import time

MODEL_NAME   = "unsloth/Meta-Llama-3.1-8B-Instruct"
MAX_SEQ_LEN  = 1024   # Reduced from 2048 — biggest single VRAM saving
LOAD_IN_4BIT = True

if __name__ == "__main__":

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name     = MODEL_NAME,
        max_seq_length = MAX_SEQ_LEN,
        dtype          = None,
        load_in_4bit   = LOAD_IN_4BIT,
    )
    print(f"Model loaded: {MODEL_NAME}")

    model = FastLanguageModel.get_peft_model(
        model,
        r                          = 8,    # Reduced from 16
        target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"],
        lora_alpha                 = 8,    # Keep equal to r
        lora_dropout               = 0.0,  # 0.0 enables Unsloth's fast path
        bias                       = "none",
        use_gradient_checkpointing = "unsloth",
        random_state               = 42,
        use_rslora                 = False,
        loftq_config               = None,
    )
    print(model.print_trainable_parameters())

    tokenizer.pad_token    = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Load pre-tokenised dataset
    dataset = load_from_disk("data/hf_dataset_tokenised")

    # Remove all non-model columns
    cols_to_remove = ["text", "__index_level_0__"]
    for split in dataset:
        existing = [c for c in cols_to_remove if c in dataset[split].column_names]
        if existing:
            dataset[split] = dataset[split].remove_columns(existing)

    print(f"Train: {len(dataset['train'])} | Val: {len(dataset['validation'])}")
    print(f"Columns: {dataset['train'].column_names}")
    # Must show: ['input_ids', 'attention_mask']

    training_args = TrainingArguments(
        output_dir                  = "./checkpoints",
        num_train_epochs            = 3,
        per_device_train_batch_size = 2,   # Reduced from 4
        per_device_eval_batch_size  = 2,   # Reduced from 4
        gradient_accumulation_steps = 8,   # Keeps effective batch = 16
        learning_rate               = 2e-4,
        lr_scheduler_type           = "cosine",
        warmup_ratio                = 0.05,
        fp16                        = not torch.cuda.is_bf16_supported(),
        bf16                        = torch.cuda.is_bf16_supported(),
        optim                       = "adamw_8bit",
        dataloader_num_workers      = 0,
        logging_steps               = 25,
        eval_strategy               = "steps",
        eval_steps                  = 500,
        save_strategy               = "steps",
        save_steps                  = 500,
        save_total_limit            = 3,
        load_best_model_at_end      = True,
        metric_for_best_model       = "eval_loss",
        greater_is_better           = False,
        seed                        = 42,
        report_to                   = "none",
        remove_unused_columns       = False,
    )

    trainer = SFTTrainer(
        model              = model,
        tokenizer          = tokenizer,
        train_dataset      = dataset["train"],
        eval_dataset       = dataset["validation"],
        dataset_text_field = "text",
        max_seq_length     = MAX_SEQ_LEN,
        dataset_num_proc   = 1,
        packing            = True,
        args               = training_args,
    )

    print("Starting fine-tuning...")
    start = time.time()
#    trainer_stats = trainer.train()
    trainer_stats = trainer.train(resume_from_checkpoint='./checkpoints/checkpoint-2200')

    elapsed = time.time() - start
    print(f"\nTraining complete in {elapsed / 60:.1f} minutes")
    print(f"Final training loss: {trainer_stats.training_loss:.4f}")

    model.save_pretrained("./lora_adapters")
    tokenizer.save_pretrained("./lora_adapters")
    print("LoRA adapters saved to ./lora_adapters")










# WORKING VERSION


# import os
# os.environ["UNSLOTH_USE_FUSED_CE_LOSS"] = "0"
# os.environ["UNSLOTH_DISABLE_FUSED_CE"]  = "0"

# from unsloth import FastLanguageModel
# import torch
# from datasets import load_from_disk
# from trl import SFTTrainer
# from transformers import TrainingArguments
# import time

# MODEL_NAME   = "unsloth/Meta-Llama-3.1-8B-Instruct"
# MAX_SEQ_LEN  = 1024   # Reduced from 2048 — biggest single VRAM saving
# LOAD_IN_4BIT = True

# if __name__ == "__main__":

#     model, tokenizer = FastLanguageModel.from_pretrained(
#         model_name     = MODEL_NAME,
#         max_seq_length = MAX_SEQ_LEN,
#         dtype          = None,
#         load_in_4bit   = LOAD_IN_4BIT,
#     )
#     print(f"Model loaded: {MODEL_NAME}")

#     model = FastLanguageModel.get_peft_model(
#         model,
#         r                          = 8,    # Reduced from 16
#         target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj",
#                                       "gate_proj", "up_proj", "down_proj"],
#         lora_alpha                 = 8,    # Keep equal to r
#         lora_dropout               = 0.0,  # 0.0 enables Unsloth's fast path
#         bias                       = "none",
#         use_gradient_checkpointing = "unsloth",
#         random_state               = 42,
#         use_rslora                 = False,
#         loftq_config               = None,
#     )
#     print(model.print_trainable_parameters())

#     tokenizer.pad_token    = tokenizer.eos_token
#     tokenizer.padding_side = "right"

#     # Load pre-tokenised dataset
#     dataset = load_from_disk("data/hf_dataset_tokenised")

#     # Remove all non-model columns
#     cols_to_remove = ["text", "__index_level_0__"]
#     for split in dataset:
#         existing = [c for c in cols_to_remove if c in dataset[split].column_names]
#         if existing:
#             dataset[split] = dataset[split].remove_columns(existing)

#     print(f"Train: {len(dataset['train'])} | Val: {len(dataset['validation'])}")
#     print(f"Columns: {dataset['train'].column_names}")
#     # Must show: ['input_ids', 'attention_mask']

#     training_args = TrainingArguments(
#         output_dir                  = "./checkpoints",
#         num_train_epochs            = 3,
#         per_device_train_batch_size = 2,   # Reduced from 4
#         per_device_eval_batch_size  = 2,   # Reduced from 4
#         gradient_accumulation_steps = 8,   # Keeps effective batch = 16
#         learning_rate               = 2e-4,
#         lr_scheduler_type           = "cosine",
#         warmup_ratio                = 0.05,
#         fp16                        = not torch.cuda.is_bf16_supported(),
#         bf16                        = torch.cuda.is_bf16_supported(),
#         optim                       = "adamw_8bit",
#         dataloader_num_workers      = 0,
#         logging_steps               = 25,
#         eval_strategy               = "steps",
#         eval_steps                  = 200,
#         save_strategy               = "steps",
#         save_steps                  = 200,
#         save_total_limit            = 3,
#         load_best_model_at_end      = True,
#         metric_for_best_model       = "eval_loss",
#         greater_is_better           = False,
#         seed                        = 42,
#         report_to                   = "none",
#         remove_unused_columns       = False,
#     )

#     trainer = SFTTrainer(
#         model              = model,
#         tokenizer          = tokenizer,
#         train_dataset      = dataset["train"],
#         eval_dataset       = dataset["validation"],
#         dataset_text_field = "text",
#         max_seq_length     = MAX_SEQ_LEN,
#         dataset_num_proc   = 1,
#         packing            = False,
#         args               = training_args,
#     )

#     print("Starting fine-tuning...")
#     start = time.time()
#     trainer_stats = trainer.train()

#     elapsed = time.time() - start
#     print(f"\nTraining complete in {elapsed / 60:.1f} minutes")
#     print(f"Final training loss: {trainer_stats.training_loss:.4f}")

#     model.save_pretrained("./lora_adapters")
#     tokenizer.save_pretrained("./lora_adapters")
#     print("LoRA adapters saved to ./lora_adapters")










# import os
# os.environ["UNSLOTH_USE_FUSED_CE_LOSS"] = "0"
# os.environ["UNSLOTH_DISABLE_FUSED_CE_LOSS"] = "1"  # add this too — some versions use this key


# from unsloth import FastLanguageModel
# import torch
# from datasets import load_from_disk
# from trl import SFTTrainer
# from transformers import TrainingArguments
# import time
# from transformers import DataCollatorForSeq2Seq
    

# MODEL_NAME   = "unsloth/llama-3-8b-Instruct-bnb-4bit"
# MAX_SEQ_LEN  = 1024
# LOAD_IN_4BIT = True

# if __name__ == "__main__":

#     model, tokenizer = FastLanguageModel.from_pretrained(
#         model_name     = MODEL_NAME,
#         max_seq_length = MAX_SEQ_LEN,
#         dtype          = None,
#         load_in_4bit   = LOAD_IN_4BIT,
#     )
#     print(f"Model loaded: {MODEL_NAME}")

#     model = FastLanguageModel.get_peft_model(
#         model,
#         r                          = 16,
#         target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
#         lora_alpha                 = 16,
#         lora_dropout               = 0.05,
#         bias                       = "none",
#         use_gradient_checkpointing = "unsloth",
#         random_state               = 42,
#         use_rslora                 = False,
#         loftq_config               = None,
#     )
#     print(model.print_trainable_parameters())

#     tokenizer.pad_token    = tokenizer.eos_token
#     tokenizer.padding_side = "right"

#     # Load pre-tokenised dataset and drop the raw text column
#     dataset = load_from_disk("data/hf_dataset_tokenised")
#     dataset = dataset.remove_columns(["text", "__index_level_0__"])

#     dataset["train"].set_format("torch")
#     dataset["validation"].set_format("torch")

#     data_collator = DataCollatorForSeq2Seq(
#         tokenizer,
#         model              = model,
#         padding            = True,
#         pad_to_multiple_of = 8,
#     )
#     # dataset.set_format("torch")                         # ← Ensures tensors, not lists
#     print(f"Train: {len(dataset['train'])} | Val: {len(dataset['validation'])}")
#     print(f"Columns: {dataset['train'].column_names}")  # Should show only input_ids, attention_mask

#     training_args = TrainingArguments(
#         output_dir                  = "./checkpoints",
#         num_train_epochs            = 3,
#         per_device_train_batch_size = 2,
#         per_device_eval_batch_size  = 2,
#         gradient_accumulation_steps = 8,
#         learning_rate               = 2e-4,
#         lr_scheduler_type           = "cosine",
#         warmup_ratio                = 0.05,
#         fp16                        = not torch.cuda.is_bf16_supported(),
#         bf16                        = torch.cuda.is_bf16_supported(),
#         optim                       = "adamw_8bit",
#         dataloader_num_workers      = 0,
#         logging_steps               = 25,
#         eval_strategy               = "steps",
#         eval_steps                  = 100,
#         save_strategy               = "steps",
#         save_steps                  = 100,
#         save_total_limit            = 3,
#         load_best_model_at_end      = True,
#         metric_for_best_model       = "eval_loss",
#         greater_is_better           = False,
#         seed                        = 42,
#         report_to                   = "none",
#         remove_unused_columns       = False,
#     )

#     # No DataCollatorForSeq2Seq — SFTTrainer handles collation internally
#     trainer = SFTTrainer(
#         model              = model,
#         tokenizer          = tokenizer,
#         train_dataset      = dataset["train"],
#         eval_dataset       = dataset["validation"],
#         # dataset_text_field = "text",
#         max_seq_length     = MAX_SEQ_LEN,
#         dataset_num_proc   = 1,
#         packing            = False,
#         args               = training_args,
#     )

#     print("Starting fine-tuning...")
#     start = time.time()
#     trainer_stats = trainer.train()

#     elapsed = time.time() - start
#     print(f"\nTraining complete in {elapsed / 60:.1f} minutes")
#     print(f"Final training loss: {trainer_stats.training_loss:.4f}")

#     model.save_pretrained("./lora_adapters")
#     tokenizer.save_pretrained("./lora_adapters")
#     print("LoRA adapters saved to ./lora_adapters")









# # # train.py
# # import os
# # os.environ["UNSLOTH_USE_FUSED_CE_LOSS"] = "0"

# # from unsloth import FastLanguageModel
# # import torch
# # from datasets import load_from_disk
# # from trl import SFTTrainer
# # from transformers import TrainingArguments, DataCollatorForSeq2Seq
# # import time

# # MODEL_NAME   = "unsloth/Meta-Llama-3.1-8B-Instruct"
# # MAX_SEQ_LEN  = 2048
# # LOAD_IN_4BIT = True

# # if __name__ == "__main__":

# #     # ── Load model ─────────────────────────────────────────────────────────────
# #     model, tokenizer = FastLanguageModel.from_pretrained(
# #         model_name     = MODEL_NAME,
# #         max_seq_length = MAX_SEQ_LEN,
# #         dtype          = None,
# #         load_in_4bit   = LOAD_IN_4BIT,
# #     )
# #     print(f"Model loaded: {MODEL_NAME}")

# #     model = FastLanguageModel.get_peft_model(
# #         model,
# #         r                          = 16,
# #         target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj",
# #                                       "gate_proj", "up_proj", "down_proj"],
# #         lora_alpha                 = 16,
# #         lora_dropout               = 0.05,
# #         bias                       = "none",
# #         use_gradient_checkpointing = "unsloth",
# #         random_state               = 42,
# #         use_rslora                 = False,
# #         loftq_config               = None,
# #     )
# #     print(model.print_trainable_parameters())

# #     # ── Load pre-tokenised dataset (no workers needed) ─────────────────────────
# #     dataset = load_from_disk("data/hf_dataset_tokenised")
# #     print(f"Train: {len(dataset['train'])} | Val: {len(dataset['validation'])}")

# #     tokenizer.pad_token    = tokenizer.eos_token
# #     tokenizer.padding_side = "right"

# #     data_collator = DataCollatorForSeq2Seq(
# #         tokenizer,
# #         model              = model,
# #         padding            = True,
# #         pad_to_multiple_of = 8,
# #     )

# #     # ── Training args ──────────────────────────────────────────────────────────
# #     training_args = TrainingArguments(
# #         output_dir                  = "./checkpoints",
# #         num_train_epochs            = 3,
# #         per_device_train_batch_size = 4,
# #         per_device_eval_batch_size  = 4,
# #         gradient_accumulation_steps = 4,
# #         learning_rate               = 2e-4,
# #         lr_scheduler_type           = "cosine",
# #         warmup_ratio                = 0.05,
# #         fp16                        = not torch.cuda.is_bf16_supported(),
# #         bf16                        = torch.cuda.is_bf16_supported(),
# #         optim                       = "adamw_8bit",
# #         dataloader_num_workers      = 0,    # Must stay 0 — Unsloth + Windows
# #         logging_steps               = 25,
# #         eval_strategy               = "steps",
# #         eval_steps                  = 100,
# #         save_strategy               = "steps",
# #         save_steps                  = 100,
# #         save_total_limit            = 3,
# #         load_best_model_at_end      = True,
# #         metric_for_best_model       = "eval_loss",
# #         greater_is_better           = False,
# #         seed                        = 42,
# #         report_to                   = "none",
# #         remove_unused_columns       = False,
# #     )

# #     # ── Trainer ────────────────────────────────────────────────────────────────
# #     trainer = SFTTrainer(
# #         model              = model,
# #         tokenizer          = tokenizer,
# #         train_dataset      = dataset["train"],
# #         eval_dataset       = dataset["validation"],
# #         dataset_text_field = "text",
# #         max_seq_length     = MAX_SEQ_LEN,
# #         data_collator      = data_collator,
# #         dataset_num_proc   = 1,     # Already tokenised — this does nothing
# #         packing            = False,
# #         args               = training_args,
# #     )

# #     # ── Train ──────────────────────────────────────────────────────────────────
# #     print("Starting fine-tuning...")
# #     start = time.time()
# #     trainer_stats = trainer.train()

# #     elapsed = time.time() - start
# #     print(f"\nTraining complete in {elapsed / 60:.1f} minutes")
# #     print(f"Final training loss: {trainer_stats.training_loss:.4f}")

# #     model.save_pretrained("./lora_adapters")
# #     tokenizer.save_pretrained("./lora_adapters")
# #     print("LoRA adapters saved to ./lora_adapters")




































# # # from unsloth import FastLanguageModel
# # # import torch
# # # from datasets import load_from_disk
# # # from trl import SFTTrainer
# # # from transformers import TrainingArguments, DataCollatorForSeq2Seq
# # # import time

# # # # ── Configuration ──────────────────────────────────────────────────────────────
# # # MODEL_NAME    = "unsloth/Meta-Llama-3.1-8B-Instruct"
# # # MAX_SEQ_LEN   = 2048   # Max token length; reduce to 1024 if VRAM is tight
# # # DTYPE         = None   # Auto-detect: Float16 on older GPUs, BFloat16 on Ampere+
# # # LOAD_IN_4BIT  = True   # Enables QLoRA; halves VRAM usage
# # # # ───────────────────────────────────────────────────────────────────────────────

# # # if __name__ == "__main__":
    
# # #     print("fine tuning began")
# # #     # Load your prepared dataset
# # #     model, tokenizer = FastLanguageModel.from_pretrained(
# # #         model_name     = MODEL_NAME,
# # #         max_seq_length = MAX_SEQ_LEN,
# # #         dtype          = None,
# # #         load_in_4bit   = LOAD_IN_4BIT,
# # #     )


# # #     model = FastLanguageModel.get_peft_model(
# # #         model,
# # #         r                          = 16,
# # #         target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj",
# # #                                       "gate_proj", "up_proj", "down_proj"],
# # #         lora_alpha                 = 16,
# # #         lora_dropout               = 0.05,
# # #         bias                       = "none",
# # #         use_gradient_checkpointing = "unsloth",
# # #         random_state               = 42,
# # #         use_rslora                 = False,
# # #         loftq_config               = None,
# # #     )


# # #     dataset = load_from_disk("data/hf_dataset")


# # #     print("padding token added")
# # #     # Data collator handles dynamic padding within each batch
# # #     data_collator = DataCollatorForSeq2Seq(
# # #         tokenizer,
# # #         model=model,
# # #         padding=True,
# # #         pad_to_multiple_of=8
# # #     )

# # #     print("data collator set")

# # #     training_args = TrainingArguments(
# # #         output_dir                  = "./checkpoints",

# # #         # ── Training duration ───────────────────────────────────────────────────
# # #         num_train_epochs            = 3,        # 2–4 epochs is standard for SFT
# # #         per_device_train_batch_size = 4,        # Reduce to 2 if OOM
# # #         per_device_eval_batch_size  = 4,
# # #         gradient_accumulation_steps = 4,        # Effective batch = 4 * 4 = 16

# # #         # ── Learning rate schedule ──────────────────────────────────────────────
# # #         learning_rate               = 2e-4,     # Standard for QLoRA fine-tunes
# # #         lr_scheduler_type           = "cosine", # Cosine decay performs well here
# # #         warmup_ratio                = 0.05,     # 5% of steps for warmup

# # #         # ── Memory & speed ──────────────────────────────────────────────────────
# # #         fp16                        = not torch.cuda.is_bf16_supported(),
# # #         bf16                        = torch.cuda.is_bf16_supported(),
# # #         optim                       = "adamw_8bit",  # 8-bit Adam saves ~3 GB VRAM
# # #         dataloader_num_workers      = 2,

# # #         # ── Logging & checkpointing ─────────────────────────────────────────────
# # #         logging_steps               = 25,
# # #         eval_strategy               = "steps",
# # #         eval_steps                  = 100,
# # #         save_strategy               = "steps",
# # #         save_steps                  = 100,
# # #         save_total_limit            = 3,        # Keep only last 3 checkpoints
# # #         load_best_model_at_end      = True,
# # #         metric_for_best_model       = "eval_loss",
# # #         greater_is_better           = False,

# # #         # ── Reproducibility ─────────────────────────────────────────────────────
# # #         seed                        = 42,
# # #         report_to                   = "none",   # Disable wandb/tensorboard
# # #     )


# # #     print("training args set")

# # #     trainer = SFTTrainer(
# # #         model           = model,
# # #         tokenizer       = tokenizer,
# # #         train_dataset   = dataset["train"],
# # #         eval_dataset    = dataset["validation"],
# # #         dataset_text_field = "text",        # The column containing your formatted prompts
# # #         max_seq_length  = MAX_SEQ_LEN,
# # #         data_collator   = data_collator,
# # #         dataset_num_proc= 2,                # Parallel tokenisation
# # #         packing         = False,            # Set True to pack short examples together (faster, but may hurt quality)
# # #         args            = training_args,
# # #     )



# # #     print("trainer created")


# # #     print("Starting fine-tuning...")
# # #     start = time.time()

# # #     trainer_stats = trainer.train()

# # #     elapsed = time.time() - start
# # #     print(f"\nTraining complete in {elapsed / 60:.1f} minutes")
# # #     print(f"Final training loss: {trainer_stats.training_loss:.4f}")

# # #     model.save_pretrained("./lora_adapters")
# # #     tokenizer.save_pretrained("./lora_adapters")

# # #     print("LoRA adapters saved to ./lora_adapters")