from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

from app.ai.prompts.audit_prompt import build_audit_prompt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

DEFAULT_BASE_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "llama-3.2-1b-instruct"
)

DEFAULT_ADAPTER_PATH = (
    PROJECT_ROOT
    / "models"
    / "pta-llama-3.2-1b-lora"
    / "final"
)


# ============================================================
# SINGLETON STATE
# ============================================================

_llama_instance: "LlamaInference | None" = None

_llama_lock = threading.Lock()

_generation_lock = threading.Lock()


# ============================================================
# LLAMA INFERENCE
# ============================================================

class LlamaInference:
    """
    PTA CTDISR fine-tuned Llama 3.2 1B inference wrapper.

    Base model:
        models/llama-3.2-1b-instruct

    LoRA adapter:
        models/pta-llama-3.2-1b-lora/final

    IMPORTANT:
        The tokenizer is loaded ONLY from the base model.
        The LoRA directory is used ONLY for the adapter.
    """

    def __init__(
        self,
        base_model_path: str | Path | None = None,
        adapter_path: str | Path | None = None,
    ) -> None:

        self.base_model_path = Path(
            base_model_path
            if base_model_path is not None
            else DEFAULT_BASE_MODEL_PATH
        )

        self.adapter_path = Path(
            adapter_path
            if adapter_path is not None
            else DEFAULT_ADAPTER_PATH
        )

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.tokenizer = None
        self.model = None

        self._load_model()

    # ========================================================
    # LOAD MODEL
    # ========================================================

    def _load_model(self) -> None:

        print("=" * 70)
        print("PTA CTDISR Llama 3.2 1B Inference")
        print("=" * 70)

        print(
            f"Base model : {self.base_model_path}"
        )

        print(
            f"LoRA       : {self.adapter_path}"
        )

        print(
            f"Device     : {self.device}"
        )

        # ====================================================
        # PATH VALIDATION
        # ====================================================

        print("-" * 70)
        print("Checking BASE model files...")
        print("-" * 70)

        if not self.base_model_path.exists():
            raise FileNotFoundError(
                "Base Llama model directory was not found:\n"
                f"{self.base_model_path}"
            )

        required_base_files = [
            "config.json",
            "tokenizer.json",
            "tokenizer_config.json",
        ]

        missing_base_files = [
            filename
            for filename in required_base_files
            if not (
                self.base_model_path / filename
            ).is_file()
        ]

        if missing_base_files:
            raise FileNotFoundError(
                "Required base model files are missing:\n"
                + "\n".join(
                    f" - {filename}"
                    for filename in missing_base_files
                )
            )

        print("BASE files OK")

        # ====================================================
        # LORA VALIDATION
        # ====================================================

        print("-" * 70)
        print("Checking PTA LoRA files...")
        print("-" * 70)

        if not self.adapter_path.exists():
            raise FileNotFoundError(
                "LoRA adapter directory was not found:\n"
                f"{self.adapter_path}"
            )

        required_adapter_files = [
            "adapter_config.json",
            "adapter_model.safetensors",
        ]

        missing_adapter_files = [
            filename
            for filename in required_adapter_files
            if not (
                self.adapter_path / filename
            ).is_file()
        ]

        if missing_adapter_files:
            raise FileNotFoundError(
                "Required LoRA adapter files are missing:\n"
                + "\n".join(
                    f" - {filename}"
                    for filename in missing_adapter_files
                )
            )

        print("LoRA files OK")

        # ====================================================
        # 1. TOKENIZER
        # ====================================================

        print("-" * 70)
        print("1. Loading BASE tokenizer...")
        print("-" * 70)

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_path,
                local_files_only=True,
                use_fast=True,
            )

        except Exception as exc:
            raise RuntimeError(
                "Failed to load BASE Llama tokenizer.\n"
                f"Path: {self.base_model_path}\n"
                f"Error: {exc}"
            ) from exc

        # ----------------------------------------------------
        # PAD TOKEN
        # ----------------------------------------------------

        if self.tokenizer.pad_token is None:

            if self.tokenizer.eos_token is not None:

                self.tokenizer.pad_token = (
                    self.tokenizer.eos_token
                )

            else:

                raise RuntimeError(
                    "Tokenizer has no PAD or EOS token."
                )

        print("TOKENIZER OK")

        print(
            f"Tokenizer class: "
            f"{self.tokenizer.__class__.__name__}"
        )

        print(
            f"Vocabulary size: "
            f"{self.tokenizer.vocab_size}"
        )

        print(
            f"Chat template: "
            f"{bool(self.tokenizer.chat_template)}"
        )

        print(
            f"BOS token: "
            f"{self.tokenizer.bos_token}"
        )

        print(
            f"EOS token: "
            f"{self.tokenizer.eos_token}"
        )

        print(
            f"PAD token: "
            f"{self.tokenizer.pad_token}"
        )

        # ====================================================
        # 2. BASE MODEL
        # ====================================================

        print("-" * 70)
        print("2. Loading BASE Llama 3.2 1B model...")
        print("-" * 70)

        try:

            if self.device == "cuda":

                print("CUDA detected.")

                try:

                    from transformers import BitsAndBytesConfig

                    quantization_config = (
                        BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_quant_type="nf4",
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_use_double_quant=True,
                        )
                    )

                    base_model = (
                        AutoModelForCausalLM.from_pretrained(
                            self.base_model_path,
                            quantization_config=(
                                quantization_config
                            ),
                            device_map="auto",
                            local_files_only=True,
                        )
                    )

                    print("4-bit BASE model loaded.")

                except Exception as exc:

                    print(
                        "4-bit loading failed."
                    )

                    print(
                        f"Reason: {exc}"
                    )

                    print(
                        "Using standard CUDA loading."
                    )

                    base_model = (
                        AutoModelForCausalLM.from_pretrained(
                            self.base_model_path,
                            dtype=torch.float16,
                            device_map="auto",
                            local_files_only=True,
                        )
                    )

                    print(
                        "Standard CUDA BASE model loaded."
                    )

            else:

                print(
                    "CUDA not detected."
                )

                print(
                    "Loading Llama 3.2 1B on CPU."
                )

                print(
                    "This may take some time."
                )

                base_model = (
                    AutoModelForCausalLM.from_pretrained(
                        self.base_model_path,
                        dtype=torch.float32,
                        low_cpu_mem_usage=True,
                        local_files_only=True,
                    )
                )

                base_model = base_model.to("cpu")

                print(
                    "CPU BASE model loaded."
                )

        except Exception as exc:

            raise RuntimeError(
                "Failed to load BASE Llama model.\n"
                f"Path: {self.base_model_path}\n"
                f"Error: {exc}"
            ) from exc

        print("BASE MODEL OK")

        # ====================================================
        # 3. LORA ADAPTER
        # ====================================================

        print("-" * 70)
        print("3. Loading PTA LoRA adapter...")
        print("-" * 70)

        try:

            self.model = PeftModel.from_pretrained(
                base_model,
                self.adapter_path,
                local_files_only=True,
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to load PTA LoRA adapter.\n"
                f"Path: {self.adapter_path}\n"
                f"Error: {exc}"
            ) from exc

        self.model.eval()

        if self.device == "cpu":
            self.model = self.model.to("cpu")

        print("LORA MODEL OK")

        # ====================================================
        # GENERATION CONFIG
        # ====================================================

        self.model.generation_config.pad_token_id = (
            self.tokenizer.pad_token_id
        )

        self.model.generation_config.eos_token_id = (
            self.tokenizer.eos_token_id
        )

        # Deterministic generation.
        #
        # IMPORTANT:
        # Do NOT set temperature/top_p/top_k when
        # do_sample=False.
        self.model.generation_config.do_sample = False

        print("=" * 70)
        print(
            "PTA CTDISR Llama 3.2 1B loaded successfully."
        )
        print("=" * 70)

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    def _build_prompt(
        self,
        control: str,
        control_description: str,
        control_interpretation: str,
        evidence: str,
    ) -> str:

        prompt_data = build_audit_prompt(
            control=control,
            control_description=control_description,
            control_interpretation=control_interpretation,
            evidence=evidence,
        )

        if not isinstance(prompt_data, dict):

            raise TypeError(
                "build_audit_prompt() must return a dictionary "
                "containing system and user messages."
            )

        system_message = str(
            prompt_data.get("system", "")
        ).strip()

        user_message = str(
            prompt_data.get("user", "")
        ).strip()

        if not system_message:

            raise ValueError(
                "Audit system prompt is empty."
            )

        if not user_message:

            raise ValueError(
                "Audit user prompt is empty."
            )

        # ====================================================
        # LLAMA CHAT TEMPLATE
        # ====================================================

        if self.tokenizer.chat_template:

            messages = [
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ]

            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        else:

            prompt = (
                f"System:\n"
                f"{system_message}\n\n"
                f"User:\n"
                f"{user_message}\n\n"
                f"Assistant:\n"
            )

        if not prompt or not prompt.strip():

            raise ValueError(
                "Final audit prompt is empty."
            )

        return prompt.strip()

    # ========================================================
    # GENERATE PTA AUDIT
    # ========================================================

    def generate_pta_audit(
        self,
        control: str,
        control_description: str,
        control_interpretation: str,
        evidence: str,
        max_new_tokens: int = 200,
    ) -> str:

        if self.model is None:
            raise RuntimeError(
                "Llama model is not loaded."
            )

        if self.tokenizer is None:
            raise RuntimeError(
                "Llama tokenizer is not loaded."
            )

        # ----------------------------------------------------
        # SAFE GENERATION LIMIT
        # ----------------------------------------------------

        max_new_tokens = max(
            100,
            min(max_new_tokens, 400),
        )

        # ====================================================
        # BUILD PROMPT
        # ====================================================

        print("-" * 70)
        print("4. Creating audit prompt...")
        print("-" * 70)

        prompt = self._build_prompt(
            control=control,
            control_description=control_description,
            control_interpretation=control_interpretation,
            evidence=evidence,
        )

        print(
            f"Prompt characters: {len(prompt):,}"
        )

        # ====================================================
        # TOKENIZATION
        # ====================================================

        print("-" * 70)
        print("5. Tokenizing prompt...")
        print("-" * 70)

        try:

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=4096,
                padding=False,
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to tokenize audit prompt.\n"
                f"Error: {exc}"
            ) from exc

        # ====================================================
        # DEVICE
        # ====================================================

        target_device = (
            "cuda"
            if self.device == "cuda"
            else "cpu"
        )

        inputs = {
            key: value.to(target_device)
            for key, value in inputs.items()
        }

        input_length = (
            inputs["input_ids"].shape[-1]
        )

        print(
            f"Prompt tokens: {input_length}"
        )

        # ====================================================
        # GENERATION
        # ====================================================

        print("-" * 70)
        print("6. Generating PTA audit...")
        print("-" * 70)

        if self.device == "cpu":

            print(
                "CPU inference is active."
            )

            print(
                "Llama 3.2 1B generation may take some time."
            )

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # Only use deterministic generation parameters.
        #
        # NO:
        #   temperature
        #   top_p
        #   top_k
        #
        # because do_sample=False.
        # ----------------------------------------------------

        generation_kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": False,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "use_cache": True,
        }

        generation_start = time.perf_counter()

        try:

            with _generation_lock:

                with torch.inference_mode():

                    output = self.model.generate(
                        **inputs,
                        **generation_kwargs,
                    )

        except Exception as exc:

            raise RuntimeError(
                "Llama generation failed.\n"
                f"Error: {exc}"
            ) from exc

        generation_time = (
            time.perf_counter()
            - generation_start
        )

        # ====================================================
        # REMOVE INPUT TOKENS
        # ====================================================

        generated_tokens = output[
            0,
            input_length:,
        ]

        print(
            f"Generated tokens: "
            f"{len(generated_tokens)}"
        )

        # ====================================================
        # DECODE
        # ====================================================

        try:

            response = self.tokenizer.decode(
                generated_tokens,
                skip_special_tokens=True,
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to decode Llama output.\n"
                f"Error: {exc}"
            ) from exc

        response = response.strip()

        print(
            f"Generation time: "
            f"{generation_time:.2f} seconds"
        )

        print("-" * 70)
        print("RAW LLM RESPONSE")
        print("-" * 70)
        print(response)
        print("-" * 70)

        if not response:

            raise RuntimeError(
                "Llama generated an empty response."
            )

        return response


# ============================================================
# SINGLETON
# ============================================================

def get_llama() -> LlamaInference:

    global _llama_instance

    if _llama_instance is not None:

        print(
            "Reusing already loaded "
            "PTA Llama 3.2 1B model."
        )

        return _llama_instance

    with _llama_lock:

        if _llama_instance is None:

            print("=" * 70)
            print(
                "Initializing PTA Llama model..."
            )
            print("=" * 70)

            _llama_instance = LlamaInference()

            print(
                "Llama model initialized."
            )

    return _llama_instance


# ============================================================
# RESET
# ============================================================

def reset_llama() -> None:

    global _llama_instance

    with _llama_lock:

        if _llama_instance is None:

            print(
                "No PTA Llama model is currently loaded."
            )

            return

        try:

            if _llama_instance.model is not None:
                del _llama_instance.model

        except Exception:
            pass

        try:

            if _llama_instance.tokenizer is not None:
                del _llama_instance.tokenizer

        except Exception:
            pass

        _llama_instance = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print(
            "PTA Llama singleton has been reset."
        )