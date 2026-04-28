🚀 Code Transpiler: Python → JavaScript
📌 Overview

The Python to JavaScript Transpiler is a compiler-based project that converts Python source code into equivalent JavaScript code.

It follows a structured compiler design approach using multiple phases like lexical analysis, parsing, semantic analysis, and code generation to ensure accurate and meaningful translation.

🎯 Problem Statement

Developers often need to run Python logic in JavaScript environments (browser or Node.js). Manually rewriting code is time-consuming and error-prone.

👉 This project solves that problem by automatically translating Python code into JavaScript while preserving its logic and behavior.

🔥 Key Features
✅ Converts Python code to JavaScript automatically
✅ Handles variables, loops, conditionals, and functions
✅ Uses Abstract Syntax Tree (AST) for structured transformation
✅ Maintains semantic correctness
✅ Generates clean and readable JavaScript code
✅ Web interface for input/output 

⚙️ Compiler Design Phases
1. Lexical Analysis (Lexer) = Breaks code into tokens (keywords, identifiers, operators)
2. Syntax Analysis (Parser) = Builds an Abstract Syntax Tree (AST)
3. Symbol Table = Stores variables, functions, and scope information
4. Semantic Analysis = Checks logical correctness (e.g., undeclared variables)
5. Code Generation = Converts AST into JavaScript code

🧠 Design Decisions
✔ Why AST-Based Approach?
Preserves program structure
Makes transformation easier and accurate
✔ Why No Formal Grammar?
Recursive Descent Parser already defines grammar in code
✔ Why No Intermediate Representation (IR)?
Not needed for optimization
Keeps output clean and readable

🏗️ System Architecture

User (Web Interface)
        ↓
Python Code Input
        ↓
Lexical Analyzer      ← Tokenizes keywords, identifiers, operators, literals
        ↓
Parser                ← Builds syntactic structure
        ↓
AST Generator         ← Constructs the Abstract Syntax Tree
        ↓
Semantic Analyzer     ← Validates scope rules and symbol table
        ↓
Transformer           ← Applies Python → JavaScript conversion rules
        ↓
Code Generator        ← Traverses transformed AST
        ↓
JavaScript Output

🎯 Project Goals
1. Implement a complete transpiler system
2. Understand real-world compiler design
3. Generate correct and readable JavaScript code
4. Bridge theory and practical implementation

🚀 How to Run
## Clone Repository
git clone https://github.com/your-username/code-transpiler.git
cd code-transpiler

## Install Dependencies
pip install -r requirements.txt

## Run Project
python app.py

👨‍💻 Team

## Team Tech Titans
Aditi Bisht
Ayushi Panwar
Shuruti Priyama
Raghav Khandelwal

🌟 Future Scope
Support full Python syntax
Add optimization phase
Improve UI/UX
Add real-time execution

⭐ Contribution
Feel free to fork, contribute, and improve this project!
