# Import namedtuple for translation
from collections import namedtuple

# Initial All the methods that BF has
Inc = namedtuple('Inc', ['x', 'offset'])
Dec = namedtuple('Dec', ['x', 'offset'])
Rgt = namedtuple('Rgt', ['x'])
Lft = namedtuple('Lft', ['x'])
Inp = namedtuple('Inp', ['offset'])
Out = namedtuple('Out', ['offset'])
Opn = namedtuple('Opn', [])
Cls = namedtuple('Cls', [])

# For optimizations
Clr = namedtuple('Clr', ['offset'])
Cpy = namedtuple('Cpy', ['off'])
Mul = namedtuple('Mul', ['off', 'factor'])

# BF to IR
def bf_to_ir(brainfuck):
    simplemap = {'+': Inc(1, 0),
                 '-': Dec(1, 0),
                 '>': Rgt(1),
                 '<': Lft(1),
                 ',': Inp(0),
                 '.': Out(0),
                 '[': Opn(),
                 ']': Cls()}
    return [simplemap[c] for c in brainfuck if c in simplemap]

# IR to Py Code
def ir_to_py(ir):
    plain = {Inc: 'mem[p] += %(x)d',
             Dec: 'mem[p] -= %(x)d',
             Rgt: 'p += %(x)d',
             Lft: 'p -= %(x)d',
             Inp: 'mem[p] = ord(os.read(0, 1)[0])',
             Out: 'os.write(1, chr(mem[p]))',
             Opn: 'while(mem[p]):',
             Cls: '',
             Clr: 'mem[p] = 0',
             Cpy: 'mem[p+%(off)d] += mem[p]',
             Mul: 'mem[p+%(off)d] += mem[p] * %(factor)d'}

    woff  = {Clr: 'mem[p+%(offset)d] = 0',
             Inc: 'mem[p+%(offset)d] += %(x)d',
             Dec: 'mem[p+%(offset)d] -= %(x)d',
             Inp: 'mem[p+%(offset)d] = ord(os.read(0, 1)[0]',
             Out: 'os.write(1, chr(mem[p+%(offset)d]))'}
    code = ''
    code += 'import os\n'
    code += 'def main():\n'
    code += '    mem = [0] * 5000\n'
    code += '    p = 0\n'
    depth = 1
    for op in ir:
        if str(op.__class__) == "<class 'ir.Cls'>":
            depth -= 1
        if depth > 0:
            for i in range(depth):
                code += '    '
        if getattr(op, 'offset', 0):
            code += (woff[op.__class__] % op._asdict())
        else:
            code += (plain[op.__class__] % op._asdict())
            if str(op.__class__) == "<class 'ir.Opn'>":
                depth += 1
        code += '\n'
    code += 'def entry_point(argv):\n    main()\n    return 0\n\n'
    code += 'def target(*args):\n    return entry_point, None\n\n'
    code += 'if __name__ == "__main__":\n    res = entry_point(sys.argv)\n' + \
            '    sys.exit(res)\n'
    return code
