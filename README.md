# Brainf * ck Interpreter / Brainf * ck Translator

**PyCon TW 2017 Talk -- PyPy's approach to construct domain-specific language runtime**
[Slide Link for Part 2](https://www.slideshare.net/star0217/pycon-tw-2017-pypys-approach-to-construct-domainspecific-language-runtime-part-2)

## bf_jit.py
It's a Brainf * ck Interpreter with JIT Enabled and some Optimization,
Compile it with PyPy, either enable JIT or not, and run <exec> <BF_Code>

## trans.py
It's the main file of the Brainf * ck Translator, it translate your BF code to Python,
and it can be compiled with PyPy,
Usage: <python> trans.py <input_file> <output file>
and either compile your output file with PyPy, or run it with Python/PyPy

The Translator use all the Optimization mentioned in the talk,
feel free to modify the trans.py to see the different result when translating your Brainf * ck code.

**bf_jit.py is from [wdv4758h/brainf*ck_bench](https://github.com/wdv4758h/brainfuck_bench)**
