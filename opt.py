from ir import *

def opt_contract(ir):
    optimized = [ir[0]]
    for op in ir[1:]:
        prev = optimized[-1]
        if(op.__class__ in (Inc, Dec, Rgt, Lft) and
           op.__class__ == prev.__class__ and
           getattr(op, 'offset', 0) == getattr(prev, 'offset', 0)):
            optimized[-1] = prev._replace(x = prev.x + op.x)
        else:
            optimized.append(op)
    return optimized

def opt_clearloop(ir):
    optimized = []
    for op in ir:
        optimized.append(op)
        if (op.__class__ == Cls and
            len(optimized) > 2  and
            optimized[-2].__class__ in (Inc, Dec) and
            optimized[-2].x == 1 and
            optimized[-2].offset == 0 and
            optimized[-3].__class__ == Opn):
            optimized.pop(-1)
            optimized.pop(-1)
            optimized[-1] = Clr(0)
    return optimized

def opt_copyloop(ir):
    # Because it's very like multiply, so use multiloop to solve this
    return opt_multiloop(ir, True)

def opt_multiloop(ir, onlycopy=False):
    ir = ir[:]
    i  = 0
    while True:
        while i < len(ir):
            if isinstance(ir[i], Opn):
                break
            i += 1
        else:
            break
        j = i + 1
        while j < len(ir):
            if isinstance(ir[j], Cls):
                break
            if isinstance(ir[j], Opn):
                i = j
            j += 1
        else:
            break
        if set(op.__class__ for op in ir[i + 1:j]) - \
           set([Inc, Dec, Rgt, Lft]) != set():
            i = j
            continue
        mem, p = {}, 0
        for op in ir[i + 1: j]:
            if isinstance(op, Inc):
                mem[p + op.offset] = mem.get(p, 0) + op.x
            elif isinstance(op, Dec):
                mem[p + op.offset] = mem.get(p, 0) - op.x
            elif isinstance(op, Rgt):
                p += op.x
            elif isinstance(op, Lft):
                p -= op.x
        if p != 0 or mem.get(0, 0) != -1:
            i = j
            continue
        mem.pop(0)
        if onlycopy and set(mem.values() + [1]) != set([1]):
            i = j
            continue
        optblock = [Cpy(p) if onlycopy else Mul(p, mem[p])
                    for p in mem]
        ir = ir[:i] + optblock + [Clr(0)] + ir[j + 1:]
        i += len(optblock) + 2
    return ir

def opt_offsetops(ir):
    ir = ir[:]
    i = 0
    while i < len(ir):
        BLOCKOPS = (Inc, Dec, Rgt, Lft, Clr, Inp, Out)
        while i < len(ir) and ir[i].__class__ not in BLOCKOPS:
            i += 1
        if i >= len(ir):
            break
        j = i
        while j < len(ir) and ir[j].__class__ in BLOCKOPS:
            j += 1
        optblock, offset, order, p = [], {}, [], 0
        for op in ir[i:j]:
            if isinstance(op, Lft):
                p -= op.x
            elif isinstance(op, Rgt):
                p += op.x
            elif op.__class__ in (Out, Inp, Clr):
                optblock.extend(x._replace(offset=p) for x in offset.get(p, []))
                optblock.append(op._replace(offset=p))
                offset[p] = []
            else:
                if not offset.get(p, []):
                    offset[p] = []
                offset[p].append(op)
                order.append(p)
        for off in order:
            optblock.extend(op._replace(offset=off) for op in offset[off])
            offset[off] = []
        if p > 0:
            optblock.extend([Rgt(1) for _ in range(p)])
        elif p < 0:
            optblock.extend([Lft(1) for _ in range(-p)])

        ir = ir[:i] + optblock + ir[j:]
        i += len(optblock) + 1
    return ir

def opt_cancel(ir):
    opposite = {Inc: Dec,
                Dec: Inc,
                Lft: Rgt,
                Rgt: Lft}
    optimized = []
    for op in ir:
        if len(optimized) == 0:
            optimized.append(op)
            continue
        prev = optimized[-1]
        if prev.__class__ == opposite.get(op.__class__) and \
           getattr(prev, 'offset', 0) == getattr(op, 'offset', 0):
            x = prev.x - op.x
            if x < 0:
                optimized[-1] = op._replace(x=-x)
            elif x > 0:
                optimized[-1] = prev._replace(x=x)
            else:
                optimized.pop(-1)
        else:
            optimized.append(op)
    return optimized
