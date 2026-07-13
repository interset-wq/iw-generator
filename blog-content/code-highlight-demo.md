---
title: "Code Highlighting Demo"
date: 2025-07-12
category: Test
tags: [code, highlight, test]
---

# Code Highlighting Demo

iw-generator supports syntax highlighting for multiple languages using Pygments.

## Python

```python
def fibonacci(n: int) -> list[int]:
    """Generate Fibonacci sequence."""
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

print(fibonacci(10))
```

## JavaScript

```javascript
const debounce = (fn, delay) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
};
```

## Rust

```rust
use std::collections::HashMap;

fn main() {
    let mut scores: HashMap<&str, i32> = HashMap::new();
    scores.insert("Blue", 10);
    scores.insert("Yellow", 50);
}
```

## Go

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

All code blocks have a language label and copy button.
