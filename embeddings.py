from fastembed import TextEmbedding
from typing import List

# Load Model
print("\033[96m(Embedding)\033[0m Load a Model")
model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", providers=["CUDAExecutionProvider"])
print("\033[96m(Embedding)\033[0m Model Loaded (all-MiniLM-L6-v2)")

def encode(input: str) -> List[float]:
    try:
        print("\033[96m(Embedding)\033[0m Start Embedding")

        embedding = list(model.embed([input]))[0]

        print("\033[96m(Embedding)\033[0m Finished Embedding")
        return embedding.tolist()
    except Exception as e:
        print(f"\033[96m(Embedding) \033[33m Failed to Embedding {e}")
        return []