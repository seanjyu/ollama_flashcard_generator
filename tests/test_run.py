# # test_run.py
# from flashcard_gen import generate_flashcard_set
#
# # Testing some notes I made on flow and diffusion models
#
# notes = """
# ### 2 - Flow and Diffusion Models
#
# #### 2.1 - Flow models
#
# \- Fundamental objects for flow
#
# &nbsp;	- Trajectory
#
# &nbsp;		- $X:\[0,1] \\rightarrow\\mathbb{R}^{d}, t \\mapsto x\_{t}$
#
# &nbsp;	- Vector Field
#
# &nbsp;		- $u: \\mathbb{R}^{d}\\times\[0, 1] \\rightarrow \\mathbb{R}^{d}, \\,\\, (x, t) \\rightarrow u\_{t}(x)$
#
# &nbsp;		- Essentially gives directions at each timestep and coordinate
#
# &nbsp;	- Ordinary differential equation (ODE)
#
# &nbsp;		- $x\_{0}, \\frac{d}{dt}x\_{t} = u\_{{t}}(x\_{t})$ (initial condition can be some coordinate and initial velocity - although the lecture only specifies the initial coordinate)
# """
#
# # Generate multiple cards
# cards = generate_flashcard_set(
#     notes=notes,
#     num_cards=5,
#     keywords=[],
#     model="qwen2.5:3b",
#     card_type="basic",
#     string_threshold=0.0,
#     verbose=False
# )
#
# for card in cards:
#     print(f"Q: {card.front}")
#     print(f"A: {card.back}\n")

# test_run.py
from flashcard_gen import generate_flashcard_set, generate_flashcard_set_rag

notes = """
### Introduction

Activation functions are used to figure out if a neuron has fired or not. In an artificial neural network the activation function is applied to the output (weighted sum + bias) of an individual neuron. The purpose of an activation function is to understand whether the particular input should be activated but also to normalize the activations. All activation function's output range from 0 to 1. Note, because weights can be less than 1, inputs can be negative.



### Step Function

$$

y= \\begin{cases}1 \& x>0 \\\\ 0 \& x \\leqslant 0\\end{cases}

$$

The most basic activation function, if the input is less than or equal to 0, then output is 0, if the input is larger than 0 then the output is 1. Not really used since too basic.



### Linear Function

$$ y = x$$

Just input equals output. Not a very good activation function for hidden layers since it will mean that the neural network will take a long time to train. However, this function is used when the last layer's output is a regression. (i.e. continuous range instead of classification)



### Sigmoid (Logistic) function

$$

y = \\frac{1}{1+e^{-x}}

$$

The sigmoid function, also known as the logistic function, is a non-linear function. Non-linear activation functions are required for classification data. The good thing about this function is that it is continuous which is important for backpropagation. However, the gradient of this function is not very large meaning that it is prone to the vanishing gradient problem which is where the gradients may disappear during backpropagation. Also, due to the small gradients, models using this function take a long time to train. Another problem of this function is that 



### Hyperbolic Tangent (Tanh)

$$

y = \\frac{e^{x}- e^{-x}}{e^{x} + e^{-x}}

$$

Like the sigmoid function, this function is also non-linear but this function is zero centered meaning that it has negative values. However, this function still suffers from the vanishing gradient problem. Also, it is computationally expensive.



### Rectified Linear Activation Function (ReLU)

$$y= \\begin{cases}x \& x>0 \\\\ 0 \& x \\leqslant 0\\end{cases}$$

The rectified linear activation function, also known as ReLU, is a combination of the linear function and the step function. This function is one of the more commonly used functions since the it is non-linear, and continuous. Also, it is less susceptible to the vanishing gradient problem.



### Leaky ReLU

$$y= \\begin{cases}x \& x>0 \\\\ 0.1x \& x \\leqslant 0\\end{cases}$$

This function is just the ReLU with a gradient for negative portions. This function  However, requires more computing power. 
"""

KWARGS = {
    "num_cards": 5,
    "model": "qwen2.5:3b",
    "card_type": "basic",
    "string_threshold": 0.8,
    "verbose":False,
}

print("METHOD 1: generate_flashcard_set (no RAG)")

cards_basic = generate_flashcard_set(
    notes=notes,
    **KWARGS
)

for card in cards_basic:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")


print("=" * 60)
print("METHOD 2: generate_flashcards_with_rag")
print("=" * 60)

cards_rag = generate_flashcard_set_rag(
    notes=notes,
    **KWARGS
)

for card in cards_rag:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")


print("=" * 60)
print("METHOD 3: RAG with keywords")
print("=" * 60)

cards_rag_kw = generate_flashcard_set_rag(
    notes=notes,
    keywords=["sigmoid", "relu", "activation function"],
    **KWARGS
)

for card in cards_rag_kw:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")


print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Basic:        {len(cards_basic)} cards")
print(f"RAG:          {len(cards_rag)} cards")
print(f"RAG+keywords: {len(cards_rag_kw)} cards")