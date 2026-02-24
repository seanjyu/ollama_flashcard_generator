from flashcard_gen import generate_flashcard_set, generate_flashcard_set_rag

notes = """
# Chapter 2 - Fundamentals of Unconstrained Optimization



- Unconstrained optimization is the most basic level of optimization

- In this setting there is only an objective function that depends on real variables with no conditions on the variables. Therefore the mathematical formulation is simply: $$\\min\_{x} f(x) \\quad \\text{where }x \\in \\mathbb{R}^{n} \\text{, }n\\geq 1$$

- Note $f:\\mathbb{R}^{n} \\rightarrow \\mathbb{R}$ and $f$ is a smooth function.

- We typically may not have global information on the function $f$ beforehand but we may have a set of points



#### What is a solution?

- Generally, a perfect solution would be a \*global optimum\* (i.e. minimizer or maximizer). For the sake of simplicity the following text will use the minimizer case but the same rules apply to a maximizer.

- The formal definition for a global minimizer is as follows

&nbsp;	- A point $x^\*$ is a global minimizer if $f(x^{\*})\\leq f(x)$ for all x 

- However, we don't always have access to a global image of the function therefore we sometimes have a local minimizer which only applies to a neighborhood (aka an open set). There are two types of local minimizer - strict and weak - the difference is in the inequality (in the strict case there is no equality constraint).

- The formal definitions of weak and strict local minimizers are as follows:

&nbsp;	- A point $x^\*$ is a \*\*weak\*\* local minimizer if there is a neighborhood $\\mathcal{N}$ of $x^\*$ such that $f(x^{\*})\\leq f(x)$ for all $x \\in \\mathcal{N}$ 

&nbsp;	- A point $x^\*$ is a \*\*strict\*\* local minimizer if there is a neighborhood $\\mathcal{N}$ of $x^\*$ such that $f(x^{\*}) < f(x)$ for all $x \\in \\mathcal{N}$ 

- A further categorization would be \*isolation\*. This is just the idea that some neighborhoods may have multiple local minimizers. The formal definition is as follows:

&nbsp;	- A point $x^\*$ is a \*\*isolated\*\* local minimizer if there is a neighborhood $\\mathcal{N}$ of $x^\*$ such that $x^\*$ is the only local minimizer in $\\mathcal{N}$

- Some strict local minimizers are not isolated. The book gives an example of $f(x) = x^{4}\\cos\\left( \\frac{1}{x} \\right) + 2x^{4}$

- It can be difficult for algorithms to identify global optima as the solution can be stuck at local optimum(s).



#### Recognizing a local minimum

- There are more efficient ways that testing all points in a neighborhood for a minimum value, particularly when a function is smooth. i.e. use differentiation!



>\[!Theorem] Taylor theorem

>\*Suppose that $f: \\mathbb{R}^{n} \\rightarrow \\mathbb{R}$ is continuously differentiable and that $p \\in \\mathbb{R}^n$. Then \*:

>$$f(x+p) = f(x) + \\nabla f(x + tp)^{T}p$$

>\*for some $t \\in (0,1)$. Moreover, if f i twice continuously differentiable, we have that\*

>$$\\nabla f(x+p) = \\nabla f(x) + \\int^{1}\_{0} \\nabla^{2}f(x + tp)p\\, dt$$

>\*and that\*

>$$f(x+p) = f(x) + \\nabla f(x)^{T}p+ \\frac{1}{2} p^{T}\\nabla ^{2}f(x+tp) p$$

>\*for some $t \\in (0,1)$\*



\*Necessary conditions\* for optimality are derived by assuming that $x^{\*}$ is a local minimizer and then proving facts about $\\nabla f(x^{\*})$ and $\\nabla^{2} f(x^{\*})$



#### First-Order Necessary Conditions

\*If $x^\*$ is a local minimizer and f is continuously differentiable in an open neighborhood of $x^{\*}$, then $\\nabla f(x^{\*}) = 0$.



Proof:

!\[\[A01-11-nocedal\_wright\_chp\_1-3\_first\_order\_proof.png]]

Proof in english:

Given that the gradient of the function is not 0, this means that there is a direction in which the function value will still decrease (the proof uses the Taylor theorem for function evaluation). Therefore $x^{\*}$ is not the local minimizer. 



$x^{\*}$ is called a stationary point if $\\nabla f(x^{\*})=0$



#### Second-Order Necessary Conditions

\*If $x^{\*}$ is a local minimizer of $f$ and $\\nabla^{2} f$ exists and is continuous in an open neighborhood of $x^{\*}$, then $\\nabla f(x^{\*}) = 0$ and $\\nabla^2 f(x)$ is positive semidefinite.\*



Proof

!\[\[A01-11-nocedal\_wright\_chp\_1-3\_second\_order\_proof.png]]

Proof in english:

Similar to the first order necessary condition proof, the idea is that if $\\nabla^{2}f(x^{\*})$ is not positive semidefinite then there exists a direction in which the curvature is not 0, such that $x$ could move in that direction and obtain a smaller value.



#### Second-Order Sufficient Conditions

\*Suppose that $\\nabla^{2}f$ is continuous in an open-neighborhood of $x\*$ and that $\\nabla f(x^{\*})= 0$ and $\\nabla f^{2}(x^{\*})$ is positive definite. Then $x^{\*}$ is a strict local minimizer of $f$.\*



Proof:

!\[\[A01-11-nocedal\_wright\_chp\_1-3\_second\_order\_sufficient\_proof.png]]



Recall that the definition of strict minimizer is such that the minimum only occurs at a single point, whereas in a normal minimizer, the function could be a line.



If the function is convex then local optimizer = global optimizer. More formally:

\*When $f$ is convex, any local minimizer $x^{\*}$ is a global minimizer of $f$ . If in addition $f$ is differentiable, then any stationary point $x^{\*}$ is a global minimizer of $f$ .\*

!\[\[A01-11-nocedal\_wright\_chp\_1-3\_convex\_1.png]]

!\[\[A01-11-nocedal\_wright\_chp\_1-3\_convex\_2.png]]



This book will look at continuous functions (note smoothness implies differentiability up to $C^{k}$). For non-smooth functions a solution can be found by using \*subgradient\* or \*generalized gradient\* methods.



#### Overview of Algorithms

In general optimization algorithms first start at a given point $x\_{0}$, and generates a sequence of iterates $\\{x\_{k}\\}\_{k=0}^\\infty$ that terminates when no progress is made (no solution found) or when an acceptable solution with sufficient accuracy is found.



The question is how to generate this sequence. Typically, information from the function $f$, the function evaluations at $f(x\_{k})$ are used (note this chapter is about unconstrained optimization so I would assume that in the constrained case that information would be used too). There are two main strategies:

\- Line search - Given a direction to iterate $x\_{k}$ determine the best step size to move.

\- Trust region - Given a region around current point $x\_{k}$ search the region for best possible new iterate.



#### Brief Overview of Line Search and Trust Region Methods

##### Line Search

In the \*line search\* strategy algorithms typically search for direction $p\_{k}$ and searches along this direction from the current iterate $x\_{k}$ for a new iterate with a lower function value. This is equivalent to the following minimization problem:

$$\\min\_{a>0} f(x\_{k} + \\alpha p\_{k})$$

Solving this problem exactly would result in finding the best direction $p\_{k}$ and the step length is given by $\\alpha$. However, this is expensive and not necessary for most applications. Instead one strategy is to calculate a limited number of step lengths to find the best (among the limited number), then repeat the process until the minimum of the function is found. i.e. choose step direction and then find best step length amount with limited trials. 



###### Search Directions

Typically the steepest direction is used, i.e. $- \\nabla f\_{k}$. Proof is shown on page 21. However, this is not always the case. Note any direction between $-\\nabla f\_{x} \\pm \\frac{\\pi}{2}(rad)$ will lead to a decrease in the function. Proof is on page 22, but it is very trivial since the next iterate is a inner product of the direction and the gradient, so long as the angle between these two vectors is less than $\\frac{\\pi}{2}$ the function will decrease.



Beyond the gradient direction (steepest descent), the Newton direction is arguably the most important search direction in optimization. It can be obtained by solving the linear system derived from setting the gradient of the second-order approximation (Taylor approximation) to zero. 

$$f(x\_{k}+p) \\approx f\_{k}+p^{T}\\nabla f\_{k} + \\frac{1}{2}p^{T}\\nabla^{2} f\_{k}p   

\\stackrel{\\text{def}}{=}m\_{k}(p)$$

Assuming that $\\nabla ^2f\_{k}$ is positive definite the newton direction can be found by obtaining the vector (direction) $p$ that minimizes $m\_k(p)$. This is done by setting the derivative of $m\_{k}(p)$ to zero giving the explicit formula:$$p\_{k}^{N}=-(\\nabla ^{2}f\_{k})^{-1}\\nabla f\_{k}$$

The newton direction is reliable when the difference between the true function ($f(x\_{k} + p)$) and its quadratic model $m\_{k}(p)$ is not too large. 

\- Not sure the point of the last paragraph on page 22 is. They compare the difference between taylor expansion between $f(x\_{k})$ and $f(x\_{k} + p)$?



The newton direction can be used in a line search method when $\\nabla^{2} f\_{k}$ is positive definite. $$\\nabla f\_{k}^{T}p\_{k}^{N}=-{p\_{k}^{N}}^{T}\\nabla^{2}f\_{k}p\_{k}^{N} \\leq -\\sigma\_{k}||p^{N}\_{k}||^{2}$$ 

Unless the gradient $\\nabla f\_{k}$ is zero (and therefore the step is $p\_{k}^N$ is also 0), $\\nabla f\_{k}^{T}p\_{k}^{N}<0$, so the Newton direction is a descent direction.

\- Should check?

Usually step length of 1 is used, but can be adjusted.



When $\\nabla^{2}f\_{k}$ is not positive definite the Newton direction may not be defined since $(\\nabla^{2}f\_{k})^{-1}$ may not exist. Even if it does not exist $\\nabla f\_{k}^{T}p\_{k}^{N}<0$ may not be true.



Methods that use the Newton Direction typically converge relatively fast. The main drawback is calculating the hessian matrix $\\nabla^{2}f(x)$.



Quasi-Newton methods use an approximation of the hessian matrix which are typically updated at each step. In the taylor expansion you can add and subtract the term $\\nabla^{2}f(x)p$ (subtract in the integral).

$$ \\nabla f(x + p) = \\nabla f(x) + \\nabla^2 f(x) p + \\int\_0^1 \\left\[ \\nabla^2 f(x + tp) - \\nabla^2 f(x) \\right] p \\, dt$$

Since $\\nabla f(\\cdot)$ is continuous the integral term is $o(||p||)$. Setting $x=x\_{k}$ and $p=x\_{k+1} - x\_{k}$ gives (note the inputs of f have been collapsed):$$\\nabla f\_{k+1} = \\nabla f\_k + \\nabla^2 f\_k (x\_{k+1} - x\_k) + o(\\|x\_{k+1} - x\_k\\|)$$

When $x\_{k}$ and $x\_{k+1}$ lie close to the solution $x^{\*}$, with $\\nabla^{2} f$ is positive definite then the expansion is dominated by the $\\nabla^2 f\_k (x\_{k+1} - x\_k)$ term. We can rewrite the above as:$$\\nabla^{2} f\_{k} (x\_{k+1} - x\_{k}) \\approx \\nabla f\_{k+1} - \\nabla f\_{k}$$

The hessian can therefore be approximated linearly replacing $\\nabla^{2}f\_{k }$ with $B\_{k+1}$ giving:$$B\_{k+1} s\_{k} = y\_{k}$$

Where $s\_{k} = x\_{k+1} - x\_k$ and $y\_{k}= \\nabla f\_{k+1} - \\nabla f\_{k}$. 



There are several ways in which $B\_{k+1}$ can be updated. Such as symmetric rank 1 (sr1) $$ B\_{k+1} = B\_k + \\frac{(y\_k - B\_k s\_k)(y\_k - B\_k s\_k)^T}{(y\_k - B\_k s\_k)^T s\_k}$$

and BFGS formula, named after its inventors, Broyden, Fletcher, Goldfarb, and Shanno $$ B\_{k+1} = B\_k - \\frac{B\_k s\_k s\_k^T B\_k}{s\_k^T B\_k s\_k} + \\frac{y\_k y\_k^T}{y\_k^T s\_k}$$

Quasi newton methods attempts to approximate the inverse of $\\nabla ^{2}f\_{k}$, such that $$p\_{k}^{N}=-(\\nabla ^{2}f\_{k})^{-1}\\nabla f\_{k}\\rightarrow-B\_{k}^{-1} \\nabla f\_{k}$$

Defining $H\_k \\overset{\\mathrm{def}}{=} B\_k^{-1}$ a possible approximation can be given by. TODO



The last class of directions are nonlinear conjugate gradient methods, which aim to solve: $$p\_{k} = -\\nabla f\_{k} + \\beta\_{k}p\_{k-1}$$

where $\\beta\_{k}$ is a scalar that ensures $p\_{k-1}$  and $p\_{k}$ are conjugate. This essentially reduces the problem to a system of linear equations which is equivalent to the problem of minimizing the convex quadratic function defined by $$\\phi(x) = \\frac{1}{2}x^TAx-b^{T}x$$

All these models will be further discussed in the book.

##### Trust Region   

In these methods a model is created at each step that is used to simulate a small region of the function, then using this model the optimal value is found. Note however, this new point must be within the region. The minimization can be formalized as:

$$-\\min\_{p} m\_{k}(x\_{k}+p), \\quad \\text{where $x\_{k}+p$ is within the trust region}$$

Where $m\_{k}$ is the model function and the candidate step is $p$. 

If no point causes the function to decrease the trust region can be shrunk and the process repeated. A quadratic function can be used as the model.

$$m\_k(x\_k + p) = f\_k + p^T \\nabla f\_k + \\frac{1}{2} p^T B\_k p,$$

There is a really basic example on pg 19-20.



Trust regions can use similar methods to newton direction methods due to them both approximating the second order derivative. Using the euclidean norm:$$\\min\_{p} f\_{k} + p^{T}\\nabla f\_{k} \\quad \\text{subject to $||p||\_{2} \\leq \\Delta\_{k}$}$$

Therefore the closed form solution can be given by: $$p\_{k} = -\\frac{\\Delta\_{k}\\nabla f\_{k}}{||\\nabla f\_{}||}$$
"""

KWARGS = {
    "num_cards": 5,
    "model": "qwen2.5:3b",
    "card_type": "basic",
    "string_threshold": 0.8,
    "verbose":False,
}

print("Method 1: Generate_flashcards_set - No Keywords")

cards_basic = generate_flashcard_set(
    notes=notes,
    **KWARGS
)

for card in cards_basic:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")

print("Method 2: Generate_flashcards_set - With Keywords")

cards_basic_keywords = generate_flashcard_set(
    notes=notes,
    keywords=["unconstrained optimization", "trust region methods", "line search", "Quasi-Newton Method"],
    **KWARGS
)

for card in cards_basic:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")

print("Method 3: generate_flashcards_with_rag - No Keywords")

cards_rag = generate_flashcard_set_rag(
    notes=notes,
    **KWARGS
)

for card in cards_rag:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")


print("Method 4: RAG with keywords")

cards_rag_keywords = generate_flashcard_set_rag(
    notes=notes,
    keywords=["unconstrained optimization", "trust region methods", "line search", "Quasi-Newton Method"],
    **KWARGS
)

for card in cards_rag_keywords:
    print(f"Q: {card.front}")
    print(f"A: {card.back}\n")


print("SUMMARY")

print(f"Basic:        {len(cards_basic)} cards")
print(f"Basic + keywords: {len(cards_basic_keywords)} cards")
print(f"RAG:          {len(cards_rag)} cards")
print(f"RAG+keywords: {len(cards_rag_keywords)} cards")