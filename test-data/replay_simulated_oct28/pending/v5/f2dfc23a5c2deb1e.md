=== SYSTEM PROMPT ===
You edit revision summaries. Rewrite the given summary so that it has AT MOST the stated number of words (count carefully; aim for about 10 percent under the limit). Keep every topic that the summary currently covers, keep technical terms, and add nothing that is not already in the summary. Output ONLY valid JSON, no fences: {"summary": string}


=== USER MESSAGE ===
Word limit: 100
Current length: 120 words

SUMMARY TO SHORTEN
Gradient descent minimises a loss L(w) by moving parameters opposite the gradient, using w_new = w_old - alpha * dL/dw, where alpha is the learning rate. A rate that is too small converges slowly; one that is too large can overshoot and diverge. Batch gradient descent uses the whole training set: stable but slow for large data. Stochastic gradient descent uses one example per update: fast and noisy, which can help escape shallow local minima. Mini-batch gradient descent uses small batches and is the usual choice in practice. For a convex loss such as mean squared error, a suitable learning rate reaches the global minimum. Feature scaling speeds convergence, and an epoch is one full pass through the training data.

Return the JSON now.

