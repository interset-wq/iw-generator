---
title: Code Highlighting Test
date: 2025-01-20
category: Test
tags: [code, highlight, test]
---

# Code Highlighting Test

This post tests code block highlighting with multiple languages.

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

const search = debounce((query) => {
  console.log(`Searching: ${query}`);
}, 300);
```

## Rust

```rust
use std::collections::HashMap;

fn main() {
    let mut scores: HashMap<&str, i32> = HashMap::new();
    scores.insert("Blue", 10);
    scores.insert("Yellow", 50);

    let team_name = "Blue";
    let score = scores.get(team_name).copied().unwrap_or(0);
    println!("{team_name}: {score}");
}
```

## Go

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    var wg sync.WaitGroup
    ch := make(chan int, 10)

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            ch <- n * n
        }(i)
    }

    wg.Wait()
    close(ch)

    for v := range ch {
        fmt.Println(v)
    }
}
```

## Shell

```bash
#!/bin/bash
set -euo pipefail

for file in *.md; do
    echo "Processing: $file"
    wc -l "$file"
done
```

## SQL

```sql
SELECT
    users.name,
    COUNT(orders.id) AS order_count,
    SUM(orders.amount) AS total_spent
FROM users
LEFT JOIN orders ON users.id = orders.user_id
WHERE orders.created_at >= '2024-01-01'
GROUP BY users.name
HAVING COUNT(orders.id) > 5
ORDER BY total_spent DESC;
```

## CSS

```css
.card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
}
```

## JSON

```json
{
  "name": "iw-generator",
  "version": "0.1.0",
  "dependencies": {
    "markdown": "^3.5.0",
    "jinja2": "^3.1.0"
  }
}
```

## Plain Text (no language)

```
This is a plain code block without any language specified.
It should still render with the toolbar.
```
