\### Introduction

Activation functions are used to figure out if a neuron has fired or not. In an artificial neural network the activation function is applied to the output (weighted sum + bias) of an individual neuron. The purpose of an activation function is to understand whether the particular input should be activated but also to normalize the activations. All activation function's output range from 0 to 1. Note, because weights can be less than 1, inputs can be negative.


\### Step Function

$$

y= \\begin{cases}1 \& x>0 \\\\ 0 \& x \\leqslant 0\\end{cases}

$$