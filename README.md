---

```markdown
# FOL Theorem Prover using Resolution

## 📘 Overview

This project implements a **First-Order Logic (FOL) theorem prover** using the **Resolution** inference rule. It reads a knowledge base (KB) written in **Conjunctive Normal Form (CNF)** and determines whether the KB is satisfiable.

- If the prover derives the **empty clause**, it outputs:
  ```
  no
  ```
  indicating the KB is **unsatisfiable** (i.e., a contradiction is found).
- If no contradiction can be derived, it outputs:
  ```
  yes
  ```
  indicating the KB is **satisfiable**.

---

## 📥 Input Format

The input is a `.cnf` file with the following structure:

```text
Predicates: P1 P2 ...
Variables: x1 x2 ...
Constants: A B ...
Functions: f1 f2 ...
Clauses:
!predicate1(arg1,arg2) predicate2(arg1)
predicate3(Constant)
```

- **Predicates**, **variables**, **constants**, and **functions** are declared before the clauses.
- **Negation** is represented using the `!` symbol.
- **Whitespace** separates **literals** within each clause.
- Each clause represents a disjunction of literals.

### Example
```text
Predicates: dog animal
Variables: x
Constants: Fido
Functions:
Clauses:
!dog(x) animal(x)
dog(Fido)
```

Represents:
- ¬dog(x) ∨ animal(x)
- dog(Fido)

---

## ⚙️ How It Works

1. **Parsing**: Parses the CNF file to extract literals, terms, and clauses.
2. **Unification**: Uses most general unification (MGU) with occurs check to unify terms.
3. **Resolution**:
   - Iteratively resolves pairs of clauses.
   - Applies substitutions to generate new clauses.
   - Halts on empty clause (unsatisfiable) or when no new clauses are generated (satisfiable).

---

## ▶️ Usage

### Run the theorem prover:
```bash
python3 lab2.py <path_to_cnf_file>
```

### Example:
```bash
python3 lab2.py testcases/p01.cnf
```

### Output:
```text
yes
```

---

## ✅ Features

- ✔️ Supports propositional and first-order logic
- ✔️ Constants and variables
- ✔️ Functions (non-nested)
- ✔️ Universal quantifiers
- ✔️ Occurs check to ensure sound unification
- ✔️ Efficient clause comparison and duplication avoidance

---

## 📂 File Structure

```
lab2.py          # The main resolution-based theorem prover
README.md        # Project documentation
*.cnf            # Test case files (input to the theorem prover)
```

---

## 📚 References

- **Artificial Intelligence: A Modern Approach (3rd Edition)**  
  By Stuart Russell & Peter Norvig  
  Chapters 7 (Inference) & 9 (Unification and Resolution)

---

## 👨‍💻 Author

**Jatin Jain**  
Rochester Institute of Technology  
B.S. Computer Science | M.S. Cybersecurity

---

## 🔖 License

This project is for academic and educational use. Feel free to use and modify it with proper attribution.

```

