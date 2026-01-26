"""
Hugging Face Text Generation Service
Provides text generation capabilities using Hugging Face transformers models.
"""
import os
import logging
from typing import Optional, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

logger = logging.getLogger(__name__)

class TextGenerationService:
    """
    Service for text generation using Hugging Face models.
    Supports both local models and models from Hugging Face Hub.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        use_pipeline: bool = True
    ):
        """
        Initialize the text generation service.
        
        Args:
            model_name: Hugging Face model identifier (e.g., 'gpt2', 'microsoft/DialoGPT-medium')
                       If None, uses default from environment or 'gpt2'
            device: Device to run on ('cuda', 'cpu', or None for auto-detection)
            use_pipeline: Whether to use transformers pipeline (simpler) or direct model access
        """
        self.model_name = model_name or os.getenv("HF_TEXT_MODEL", "gpt2")
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.use_pipeline = use_pipeline
        self.tokenizer = None
        self.model = None
        self.generator = None
        self._initialized = False
        
    def initialize(self):
        """
        Lazy initialization of the model.
        Models are automatically downloaded from Hugging Face Hub on first use.
        No manual download needed - transformers library handles it.
        """
        if self._initialized:
            return
            
        try:
            logger.info(f"Downloading/Loading model from Hugging Face Hub: {self.model_name} on device: {self.device}")
            
            if self.use_pipeline:
                # Use pipeline for simpler API - automatically downloads from Hugging Face Hub
                try:
                    self.generator = pipeline(
                        "text-generation",
                        model=self.model_name,  # Downloads from HF Hub if not cached
                        tokenizer=self.model_name,  # Downloads from HF Hub if not cached
                        device=0 if self.device == "cuda" else -1,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                except Exception as pipeline_error:
                    logger.warning(f"Pipeline initialization failed: {pipeline_error}, falling back to direct model access")
                    self.use_pipeline = False
                    # Initialize direct model access as fallback
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)  # Downloads from HF Hub
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,  # Downloads from HF Hub
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )
                    self.model.to(self.device)
                    if self.tokenizer.pad_token is None:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                # Direct model access - automatically downloads from Hugging Face Hub
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)  # Downloads from HF Hub
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,  # Downloads from HF Hub
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                self.model.to(self.device)
                
                # Set pad token if not present
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    
            self._initialized = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
        do_sample: bool = True,
        num_return_sequences: int = 1,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repetition_penalty: Penalty for repetition (1.0 = no penalty)
            do_sample: Whether to use sampling
            num_return_sequences: Number of sequences to return
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text string
        """
        if not self._initialized:
            self.initialize()
        
        # Validate prompt
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided")
            return ""
            
        try:
            if self.use_pipeline and self.generator:
                # Use pipeline with return_full_text=True to avoid indexing issues
                try:
                    results = self.generator(
                        prompt,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        repetition_penalty=repetition_penalty,
                        do_sample=do_sample,
                        num_return_sequences=1,  # Force to 1 to avoid issues
                        return_full_text=True,  # Get full text and extract manually
                        **kwargs
                    )
                    
                    # Extract generated text - handle different result formats
                    if isinstance(results, list) and len(results) > 0:
                        result_item = results[0]
                        if isinstance(result_item, dict):
                            full_text = result_item.get("generated_text", "")
                            # Remove the original prompt from the beginning
                            if full_text.startswith(prompt):
                                generated_text = full_text[len(prompt):].strip()
                            else:
                                generated_text = full_text
                        elif isinstance(result_item, str):
                            if result_item.startswith(prompt):
                                generated_text = result_item[len(prompt):].strip()
                            else:
                                generated_text = result_item
                        else:
                            generated_text = str(result_item)
                        return generated_text.strip() if generated_text else ""
                    
                    # If results is a dict directly
                    if isinstance(results, dict):
                        full_text = results.get("generated_text", "")
                        if full_text.startswith(prompt):
                            generated_text = full_text[len(prompt):].strip()
                        else:
                            generated_text = full_text
                        return generated_text.strip() if generated_text else ""
                    
                    logger.warning("Pipeline returned empty or unexpected result")
                    return ""
                except Exception as pipeline_error:
                    logger.warning(f"Pipeline generation failed: {pipeline_error}, trying direct model access")
                    # Fall back to direct model access
                    if not self.tokenizer or not self.model:
                        # Need to initialize direct access
                        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                        self.model = AutoModelForCausalLM.from_pretrained(
                            self.model_name,
                            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                        )
                        self.model.to(self.device)
                        if self.tokenizer.pad_token is None:
                            self.tokenizer.pad_token = self.tokenizer.eos_token
                    # Continue to direct model access below
                
            # Direct model access (either forced or as fallback)
            if not self.tokenizer or not self.model:
                # Initialize if not already done
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                self.model.to(self.device)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Tokenize with proper error handling
            try:
                # Use tokenizer properly - encode returns list, we need to handle it
                encoded = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True, padding=False)
                inputs = encoded["input_ids"].to(self.device)
                
                if inputs.shape[1] == 0:
                    logger.warning("Tokenized input is empty")
                    return ""
            except Exception as token_error:
                logger.error(f"Tokenization error: {token_error}")
                raise
            
            # Generate with proper error handling
            try:
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_new_tokens=min(max_new_tokens, 512),  # Limit to avoid issues
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        repetition_penalty=repetition_penalty,
                        do_sample=do_sample,
                        num_return_sequences=1,  # Force to 1
                        pad_token_id=self.tokenizer.eos_token_id if self.tokenizer.pad_token_id is None else self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        **{k: v for k, v in kwargs.items() if k not in ['max_length']}  # Remove max_length if present
                    )
            except Exception as gen_error:
                logger.error(f"Generation error: {gen_error}")
                raise
            
            # Decode the full output and extract new part
            try:
                if len(outputs) == 0 or outputs.shape[0] == 0:
                    logger.warning("Model generated empty output")
                    return ""
                
                # Decode full output
                full_decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Remove the prompt from the beginning
                if full_decoded.startswith(prompt):
                    generated_text = full_decoded[len(prompt):].strip()
                else:
                    # If prompt doesn't match, decode only new tokens
                    input_length = inputs.shape[1]
                    if outputs.shape[1] > input_length:
                        generated_ids = outputs[0][input_length:]
                        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
                    else:
                        generated_text = full_decoded
                
                return generated_text.strip() if generated_text else ""
            except Exception as decode_error:
                logger.error(f"Decoding error: {decode_error}")
                raise
                
        except Exception as e:
            logger.error(f"Error during text generation: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def generate_batch(
        self,
        prompts: list,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        **kwargs
    ) -> list:
        """
        Generate text for multiple prompts.
        
        Args:
            prompts: List of input prompts
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated text strings
        """
        results = []
        for prompt in prompts:
            generated = self.generate(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                **kwargs
            )
            results.append(generated)
        return results


# Global instance (singleton pattern)
_text_generator: Optional[TextGenerationService] = None


def get_text_generator(
    model_name: Optional[str] = None,
    device: Optional[str] = None,
    use_pipeline: bool = False  # Default to False for more reliable direct access
) -> TextGenerationService:
    """
    Get or create the global text generation service instance.
    
    Args:
        model_name: Model name (only used on first call)
        device: Device (only used on first call)
        use_pipeline: Whether to use pipeline (only used on first call)
        
    Returns:
        TextGenerationService instance
    """
    global _text_generator
    
    if _text_generator is None:
        _text_generator = TextGenerationService(
            model_name=model_name,
            device=device,
            use_pipeline=use_pipeline
        )
    
    return _text_generator


def generate_text(
    prompt: str,
    max_new_tokens: int = 100,
    temperature: float = 0.7,
    model_name: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function for quick text generation.
    
    Args:
        prompt: Input text prompt
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        model_name: Optional model name (creates new instance if different)
        **kwargs: Additional generation parameters
        
    Returns:
        Generated text string
    """
    generator = get_text_generator(model_name=model_name)
    return generator.generate(
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        **kwargs
    )
