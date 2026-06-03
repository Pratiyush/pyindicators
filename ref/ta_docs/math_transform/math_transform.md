# Math Transform & Operators (vector math used by/with indicators)

- **Category:** math_transform / math_operators (TA-Lib groups)

## Element-wise math transforms (TA-Lib Math Transform)
ACOS, ASIN, ATAN, COS, COSH, SIN, SINH, TAN, TANH, CEIL, FLOOR, EXP, LN, LOG10, SQRT.
- Apply a math function to each element. Edge cases: domain limits (ACOS/ASIN need input in [-1,1]; LN/LOG10/SQRT need > 0 / ≥ 0) → produce NaN outside domain.

## Window math operators (TA-Lib Math Operators)
MIN, MAX, MININDEX, MAXINDEX, MINMAX, MINMAXINDEX, SUM over a rolling window; ADD, SUB, MULT, DIV element-wise.
- Edge cases: DIV by zero → guard/NaN; MIN/MAX warmup = N-1.

## Usage
These back many indicators (Donchian uses MAX/MIN; Fisher uses LN; angle uses ATAN). Keep them as thin reusable utilities so indicator classes never hand-roll them.

## References & libraries
- TA-Lib Math Transform & Math Operators groups; tulip `add`,`sub`,`mul`,`div`,`min`,`max`,`sum`,`abs`,`ln`,`log10`,`exp`,`sqrt`,`floor`,`ceil`,`sin`,`cos`,`tan`,`asin`,`acos`,`atan`, etc.
