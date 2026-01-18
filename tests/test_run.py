# test_run.py
from flashcard_gen import generate_flashcard_set

# Testing some notes I made on flow and diffusion models

notes = """
\### 2 - Flow and Diffusion Models

\#### 2.1 - Flow models

\- Fundamental objects for flow 

&nbsp;	- Trajectory

&nbsp;		- $X:\[0,1] \\rightarrow\\mathbb{R}^{d}, t \\mapsto x\_{t}$

&nbsp;	- Vector Field

&nbsp;		- $u: \\mathbb{R}^{d}\\times\[0, 1] \\rightarrow \\mathbb{R}^{d}, \\,\\, (x, t) \\rightarrow u\_{t}(x)$

&nbsp;		- Essentially gives directions at each timestep and coordinate

&nbsp;	- Ordinary differential equation (ODE)

&nbsp;		- $x\_{0}, \\frac{d}{dt}x\_{t} = u\_{{t}}(x\_{t})$ (initial condition can be some coordinate and initial velocity - although the lecture only specifies the initial coordinate)
"""

# Generate multiple cards
cards = generate_flashcard_set(
    notes=notes,
    num_cards=5,
    keywords=[],
    model="qwen2.5:3b",
    card_type="basic",
    string_threshold=0.0,
    verbose=False
)

for card in cards:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")
