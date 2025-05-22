# .openhands/dspy.md
## DSPy in a nutshell
[DSPy](https://github.com/stanfordnlp/dspy) is a *declarative* framework for composing language‑model programs instead of crafting one‑off prompts.

| Concept | DSPy construct | Tiny example |
|---------|----------------|--------------|
| **Data row** | `Example` | `Example(question="2+2", answer="4")` |
| **Module** | `Signature` subclass | `class Add(dspy.Signature): ...` |
| **Run** | `Predict` | `add = dspy.Predict(Add)` |

### 1 – Minimal “Hello DSPy”
```python
import dspy

class Add(dspy.Signature):
    a: int = dspy.InputField()
    b: int = dspy.InputField()
    result: int = dspy.OutputField(desc="a + b")

add = dspy.Predict(Add)
print(add(a=2, b=3).result)  # → 5
```

### 2 – Optimising with compile()
DSPy can search prompt variants or fine‑tune weights:

```python
train, dev = dspy.datasets.load_splits("simple_math")
compiled_add = dspy.compile(
    add,                 # module to optimise
    train_data=train,
    eval_data=dev,
    algorithm="beam"
)
```

### 3 – RAG or multi‑step reasoning
```python
from dspy import Toolkit, RetrievalQA

qa = RetrievalQA(
    retrieve=Toolkit.OpenAI(index_name="docs").top_k(3),
    answer=dspy.Predict("Answer")
)
print(qa("Explain RAFT consensus in 2 lines."))
```

### 4 – Program‑of‑Thought (PoT)
Compose chains‑of‑thought as *code you own* rather than raw prompts.  
This gives you version control, testing, and reuse.

### 5 – Where to go next
* **docs/** deep‑dive modules & cookbooks in the DSPy repo.
* Review the README for latest algorithms & LM back‑ends.
