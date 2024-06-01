""" PUC16 instruction definitions.
"""

from ..encoding import Instruction, Operand, Syntax
from ..isa import Relocation, Isa
from ..token import Token, bit_range, Endianness
from .registers import PUC16Register
from . import registers
from math import log2
from .. import effects

isa = Isa()

class PUC16Token(Token):
    class Info:
        size = 16
        endianness=Endianness.BIG,

    opcode = bit_range(12, 16)
    r1 = bit_range(8, 12)
    r2 = bit_range(4, 8)
    r3 = bit_range(0, 4)
    c4 = bit_range(0, 4)
    c8 = bit_range(0, 8)
    c8l = bit_range(4, 12)
    c12 = bit_range(0, 12)

class PUC16Instruction(Instruction):
    isa = isa

def make_rrr(mnemonic, opcode):
    r1 = Operand("r1", PUC16Register, write=True)
    r2 = Operand("r2", PUC16Register, read=True)
    r3 = Operand("r3", PUC16Register, read=True)
    syntax = Syntax([mnemonic, " ", r1, ",", " ", r2, ",", " ", r3])
    patterns = {
        "opcode": opcode,
        "r1": r1,
        "r2": r2,
        "r3": r3,
    }
    members = {
        "tokens": [PUC16Token],
        "r1": r1,
        "r2": r2,
        "r3": r3,
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

def make_rrc(mnemonic, opcode, addr=False, write=True):
    r1 = Operand("r1", PUC16Register, read = not write, write=write)
    r2 = Operand("r2", PUC16Register, read=True)
    c4 = Operand("c4", int)
    if addr:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", "[", r2, ",", " ", c4, "]"])
    else:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", r2, ",", " ", c4])

    patterns = {
        "opcode": opcode,
        "r1": r1,
        "r2": r2,
        "c4": c4,
    }
    members = {
        "tokens": [PUC16Token],
        "r1": r1,
        "r2": r2,
        "c4": c4,
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

@isa.register_relocation
class Abs8DataRelocation(Relocation):
    """ Apply 8 bit absolute data relocation """

    name = "abs8data"
    token = PUC16Token
    field = "c8"

    def calc(self, sym_value, reloc_value):
        return sym_value

def abs_data_relocations(self):
    yield Abs8DataRelocation(self.c12)

def make_rc(mnemonic, opcode, write=True, label=False, func=""):
    if write:
        r1 = Operand("r1", PUC16Register, write=True)
    else:
        r1 = Operand("r1", PUC16Register, read=True)

    if label:
        c8 = Operand("c8", str)
        if func != "":
            syntax = Syntax([mnemonic, " ", r1, ",", " ", func, "(", "@", c8, ")"])
        else:
            syntax = Syntax([mnemonic, " ", r1, ",", " ", "@", c8])
    else:
        c8 = Operand("c8", int)
        syntax = Syntax([mnemonic, " ", r1, ",", " ", c8])

    patterns = {
        "opcode": opcode,
        "r1": r1,
    }
    if not label:
        patterns["c8"] = c8;    
    members = {
        "tokens": [PUC16Token],
        "r1": r1,
        "c8": c8,
        "syntax": syntax,
        "patterns": patterns,
        "gen_relocations": abs_data_relocations,
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

def make_rm(mnemonic, opcode, minor):
    r1 = Operand("r1", PUC16Register, write=True)
    syntax = Syntax([mnemonic, " ", r1])

    patterns = {
        "opcode": opcode,
        "r1": r1,
        "c8": minor
    }
    members = {
        "tokens": [PUC16Token],
        "r1": r1,
        "syntax": syntax,
        "patterns": patterns
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

def make_mr(mnemonic, opcode, minor):
    r3 = Operand("r3", PUC16Register, read=True)
    syntax = Syntax([mnemonic, " ", r3])

    patterns = {
        "opcode": opcode,
        "r3": r3,
        "c8l": minor
    }
    members = {
        "tokens": [PUC16Token],
        "r3": r3,
        "syntax": syntax,
        "patterns": patterns
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

@isa.register_relocation
class Rel8BranchRelocation(Relocation):
    """ Apply 8 bit relative branch relocation """

    name = "rel8branch"
    token = PUC16Token
    field = "c8"

    def calc(self, sym_value, reloc_value):
        return sym_value - reloc_value - 1

def rel_branch_relocations(self):
    yield Rel8BranchRelocation(self.c8)

# Branch
def make_mc(mnemonic, opcode, minor):
    c8 = Operand("c8", str)
    syntax = Syntax([mnemonic, " ", "@", c8])

    patterns = {
        "opcode": opcode,
        "r1": minor,
        "c8": c8
    }
    members = {
        "tokens": [PUC16Token],
        "c8": c8,
        "syntax": syntax,
        "patterns": patterns,
        "gen_relocations": rel_branch_relocations,
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

@isa.register_relocation
class Abs12BranchRelocation(Relocation):
    """ Apply 12 bit absolute branch relocation """

    name = "abs12branch"
    token = PUC16Token
    field = "c12"

    def calc(self, sym_value, reloc_value):
        return sym_value

def abs_branch_relocations(self):
    yield Abs12BranchRelocation(self.c12)

# Jump
def make_c(mnemonic, opcode):
    c12 = Operand("c12", str)
    syntax = Syntax([mnemonic, " ", "@", c12])

    patterns = {
        "opcode": opcode,
        "c12": c12,
    }
    members = {
        "tokens": [PUC16Token],
        "c12": c12,
        "syntax": syntax,
        "patterns": patterns,
        "gen_relocations": abs_branch_relocations,
    }
    return type(mnemonic.title(), (PUC16Instruction,), members)

# Memory instructions:
Mov   = make_rc ("mov" ,   0)
MovT  = make_rc ("movt",   1)
MovL  = make_rc ("mov" ,   0, label=True, func="low")
MovTL = make_rc ("movt",   1, label=True, func="high")
B     = make_mc ("b"   ,   2, 0)
BZ    = make_mc ("bz"  ,   2, 1)
BNZ   = make_mc ("bnz" ,   2, 2)
BCS   = make_mc ("bcs" ,   2, 3)
BCC   = make_mc ("bcc" ,   2, 4)
Jump  = make_c  ("jmp" ,   3)
Jump.effect = lambda self: [effects.Assign(effects.PC, self.c12)]

Ldr   = make_rrc("ldr",   4, addr=True)
Str   = make_rrc("str",   5, addr=True, write=False)
Push  = make_mr ("push",  6, 0b00001110)
Pop   = make_rm ("pop",   7, 0b11100000)

# ALU instructions:
Add   = make_rrr("add",   16)
AddC  = make_rrc("add",   9)
Sub   = make_rrr("sub",  10)
SubC  = make_rrc("sub",  11)
Shift  = make_rrc("shl",  12)
And   = make_rrr("and",  13)
Or    = make_rrr("or",  14)
Xor   = make_rrr("xor",  15)

@isa.pattern("reg", "ADDI16(reg, reg)")
@isa.pattern("reg", "ADDU16(reg, reg)")
@isa.pattern("reg", "ADDI8(reg, reg)")
@isa.pattern("reg", "ADDU8(reg, reg)")
def pattern_add(context, tree, c0, c1):
    d = context.new_reg(PUC16Register)
    context.emit(Add(d, c0, c1))
    return d

@isa.pattern("reg", "ADDI16(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU16(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI16(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU16(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI16(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU16(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI16(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU16(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI8(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU8(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI8(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU8(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
def pattern_addc(context, tree, c0):
    d = context.new_reg(PUC16Register)
    context.emit(AddC(d, c0, tree[1].value))
    return d

@isa.pattern("reg", "ADDI16(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU16(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI16(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU16(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI16(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU16(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI16(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU16(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI8(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU8(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI8(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU8(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
def pattern_addc2(context, tree, c0):
    d = context.new_reg(PUC16Register)
    context.emit(AddC(d, c0, tree[0].value))
    return d

@isa.pattern("reg", "SUBI16(reg, reg)")
@isa.pattern("reg", "SUBU16(reg, reg)")
@isa.pattern("reg", "SUBI8(reg, reg)")
@isa.pattern("reg", "SUBU8(reg, reg)")
def pattern_sub(context, tree, c0, c1):
    d = context.new_reg(PUC16Register)
    context.emit(Sub(d, c0, c1))
    return d

@isa.pattern("reg", "SUBI16(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU16(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI16(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU16(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI16(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU16(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI16(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU16(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI8(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU8(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI8(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU8(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
def pattern_subc(context, tree, c0):
    d = context.new_reg(PUC16Register)
    context.emit(SubC(d, c0, tree[1].value))
    return d

@isa.pattern("reg", "SUBI16(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU16(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI16(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU16(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI16(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU16(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI16(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU16(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI8(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU8(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI8(CONSTI16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU8(CONSTU16, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
def pattern_subc(context, tree, c0):
    d = context.new_reg(PUC16Register)
    context.emit(SubC(d, c0, tree[0].value))
    return d

@isa.pattern("reg", "NEGI16(reg, reg)", size=2, cycles=2, energy=2)
@isa.pattern("reg", "NEGI8(reg, reg)", size=2, cycles=2, energy=2)
def pattern_neg(context, tree, c0):
    d = context.new_reg(PUC16Register)
    zero = context.new_reg(PUC16Register)
    context.emit(Mov(zero, 0))
    context.emit(Sub(d, zero, c0))
    return d

@isa.pattern("reg", "INVU16(reg, reg)", size=2, cycles=2, energy=2)
@isa.pattern("reg", "INVI16(reg, reg)", size=2, cycles=2, energy=2)
def pattern_inv(context, tree, c0):
    d = context.new_reg(PUC16Register)
    ff = context.new_reg(PUC16Register)
    context.emit(Mov(ff, 255))
    context.emit(MovT(ff, 255))
    context.emit(Xor(d, c0, ff))
    return d

@isa.pattern("reg", "INVU8(reg, reg)", size=2, cycles=2, energy=2)
@isa.pattern("reg", "INVI8(reg, reg)", size=2, cycles=2, energy=2)
def pattern_inv(context, tree, c0):
    d = context.new_reg(PUC16Register)
    ff = context.new_reg(PUC16Register)
    context.emit(Mov(ff, 255))
    context.emit(Xor(d, c0, ff))
    return d

@isa.pattern("reg", "ANDI16(reg, reg)")
@isa.pattern("reg", "ANDU16(reg, reg)")
@isa.pattern("reg", "ANDI8(reg, reg)")
@isa.pattern("reg", "ANDU8(reg, reg)")
def pattern_and(context, tree, c0, c1):
    d = context.new_reg(PUC16Register)
    context.emit(And(d, c0, c1))
    return d

@isa.pattern("reg", "ORI16(reg, reg)")
@isa.pattern("reg", "ORU16(reg, reg)")
@isa.pattern("reg", "ORI8(reg, reg)")
@isa.pattern("reg", "ORU8(reg, reg)")
def pattern_or(context, tree, c0, c1):
    d = context.new_reg(PUC16Register)
    context.emit(Or(d, c0, c1))
    return d

@isa.pattern("reg", "XORI16(reg, reg)")
@isa.pattern("reg", "XORU16(reg, reg)")
@isa.pattern("reg", "XORI8(reg, reg)")
@isa.pattern("reg", "XORU8(reg, reg)")
def pattern_xor(context, tree, c0, c1):
    d = context.new_reg(PUC16Register)
    context.emit(Xor(d, c0, c1))
    return d

@isa.pattern("reg", "MULU16(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU16(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU16(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU16(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU8(reg, CONSTI16)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU8(reg, CONSTU16)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
def pattern_mul(context, tree, c0):
    # Multiply with constant is needed for array handling; emulate
    if tree[1].value == 0:
        d = context.new_reg(PUC16Register)
        context.emit(Mov(d, 0))
        return d
    elif tree[1].value == 1:
        return c0

    assert(tree[1].value > 1)
    n = log2(tree[1].value) - 1
    assert(n.is_integer())
    d = context.new_reg(PUC16Register)
    context.emit(Shift(d, c0, 1))
    for i in range(int(n)):
        context.emit(Shift(d, d, 1))
    return d

# missing 8-bit shift
@isa.pattern("reg", "SHLI16(reg, CONSTU16)")
@isa.pattern("reg", "SHLU16(reg, CONSTU16)")
@isa.pattern("reg", "SHLI16(reg, CONSTI16)")
@isa.pattern("reg", "SHLU16(reg, CONSTI16)")
@isa.pattern("reg", "SHLI16(reg, CONSTU8)")
@isa.pattern("reg", "SHLU16(reg, CONSTU8)")
@isa.pattern("reg", "SHLI16(reg, CONSTI8)")
@isa.pattern("reg", "SHLU16(reg, CONSTI8)")
def pattern_shl(context, tree, c0):
    if tree.value == 0:
        return c0

    assert(tree[1].value > 0)
    d = context.new_reg(PUC16Register)
    context.emit(Shift(d, c0, 1))
    for i in range(tree[1].value-1):
      context.emit(Shift(d, d, 1))
    return d

# missing 8-bit shift
@isa.pattern("reg", "SHRI16(reg, CONSTU16)")
@isa.pattern("reg", "SHRU16(reg, CONSTU16)")
@isa.pattern("reg", "SHRI16(reg, CONSTI16)")
@isa.pattern("reg", "SHRU16(reg, CONSTI16)")
@isa.pattern("reg", "SHRI16(reg, CONSTU8)")
@isa.pattern("reg", "SHRU16(reg, CONSTU8)")
@isa.pattern("reg", "SHRI16(reg, CONSTI8)")
@isa.pattern("reg", "SHRU16(reg, CONSTI8)")
def pattern_shr(context, tree, c0):
    if tree.value == 0:
        return c0

    assert(tree[1].value > 0)
    d = context.new_reg(PUC16Register)
    context.emit(Shft(d, c0, -1))
    for i in range(tree[1].value-1):
      context.emit(Shft(d, d, -1))
    return d

@isa.pattern("reg", "FPRELU16")
@isa.pattern("reg", "FPRELU8")
def pattern_fprelu16(context, tree):
    # First stack element is at fp. Previous fp is at fp+1
    if tree.value.offset != -1:
        d = context.new_reg(PUC16Register)
        if tree.value.offset < -16:
            context.emit(Mov(d, tree.value.offset+1))
            context.emit(Add(d, registers.fp, d))
            return d
        else:
            context.emit(SubC(d, registers.fp, -(tree.value.offset+1)))
            return d
    else:
        return registers.fp

@isa.pattern("stm", "STRI16(reg, reg)", energy=2)
@isa.pattern("stm", "STRU16(reg, reg)", energy=2)
@isa.pattern("stm", "STRI8(reg, reg)", energy=2)
@isa.pattern("stm", "STRU8(reg, reg)", energy=2)
def pattern_str(context, tree, c0, c1):
    context.emit(Str(c1, c0, 0))

@isa.pattern("stm", "STRI16(ADDU16(reg, CONSTI16), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("stm", "STRU16(ADDU16(reg, CONSTI16), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("stm", "STRI16(ADDU16(reg, CONSTU16), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("stm", "STRU16(ADDU16(reg, CONSTU16), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
def pattern_strrc(context, tree, c0, c1):
    context.emit(Str(c1, c0, tree[0][1].value))

@isa.pattern("stm", "STRI16(FPRELU16, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRU16(FPRELU16, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRI8(FPRELU16, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRU8(FPRELU16, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRI16(FPRELU8, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRU16(FPRELU8, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRI8(FPRELU8, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRU8(FPRELU8, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
def pattern_strfp(context, tree, c0):
    context.emit(Str(c0, registers.fp, tree[0].value.offset+1))

@isa.pattern("reg", "LDRI16(reg)", energy=2)
@isa.pattern("reg", "LDRU16(reg)", energy=2)
@isa.pattern("reg", "LDRI8(reg)", energy=2)
@isa.pattern("reg", "LDRU8(reg)", energy=2)
def pattern_ldr(context, tree, c0):
    d = context.new_reg(PUC16Register)
    context.emit(Ldr(d, c0, 0))
    return d

@isa.pattern("reg", "LDRI16(ADDU16(reg, CONSTI16))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("reg", "LDRU16(ADDU16(reg, CONSTI16))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("reg", "LDRI16(ADDU16(reg, CONSTU16))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("reg", "LDRU16(ADDU16(reg, CONSTU16))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
def pattern_ldrrc(context, tree, c0):
    d = context.new_reg(PUC16Register)
    context.emit(Ldr(d, c0, tree[0][1].value))
    return d

@isa.pattern("reg", "LDRI16(FPRELU16)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRU16(FPRELU16)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRI8(FPRELU16)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRU8(FPRELU16)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRI16(FPRELU8)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRU16(FPRELU8)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRI8(FPRELU8)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRU8(FPRELU8)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
def pattern_ldrfp(context, tree):
    d = context.new_reg(PUC16Register)
    context.emit(Ldr(d, registers.fp, tree[0].value.offset+1))
    return d

# Misc patterns:
@isa.pattern("reg", "CONSTI16", condition=lambda t: t.value >= -128 and t.value <= 127)
@isa.pattern("reg", "CONSTU16", condition=lambda t: t.value <= 255)
@isa.pattern("reg", "CONSTI8")
@isa.pattern("reg", "CONSTU8")
def pattern_mov8(context, tree):
    d = context.new_reg(PUC16Register)
    context.emit(Mov(d, tree.value))
    return d

@isa.pattern("reg", "CONSTI16")
@isa.pattern("reg", "CONSTU16")
def pattern_mov16(context, tree):
    d = context.new_reg(PUC16Register)
    context.emit(Mov(d, (tree.value+65536)&255))
    context.emit(MovT(d, ((tree.value+65536)//256)&255))
    return d

@isa.pattern("stm", "MOVI16(reg)")
@isa.pattern("stm", "MOVU16(reg)")
@isa.pattern("stm", "MOVI8(reg)")
@isa.pattern("stm", "MOVU8(reg)")
def pattern_movr(context, tree, c0):
    d = tree.value
    context.emit(AddC(d, c0, 0, ismove=True))

@isa.pattern("reg", "REGI16", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU16", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGI8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU8", size=0, cycles=0, energy=0)
def pattern_reg(context, tree):
    return tree.value

@isa.pattern("reg", "I16TOU16(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U16TOI16(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "I8TOU8(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U8TOI8(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U8TOU16(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U8TOI16(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "I8TOI16(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "I8TOU16(reg)", size=0, cycles=0, energy=0)
def pattern_cast(context, tree, c0):
    return c0

@isa.pattern("reg", "U16TOU8(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U16TOI8(reg)", size=0, cycles=0, energy=0)
def pattern_cast(context, tree, c0):
    d = context.new_reg(PUC16Register)
    ff = context.new_reg(PUC16Register)
    context.emit(Mov(ff, 255))
    context.emit(And(d, c0, ff))
    return d

@isa.pattern("reg", "I16TOU8(reg)", size=0, cycles=0, energy=0)
#TODO: @isa.pattern("reg", "I16TOI8(reg)", size=0, cycles=0, energy=0)
def pattern_cast(context, tree, c0):
    d = context.new_reg(PUC16Register)
    ff = context.new_reg(PUC16Register)
    context.emit(Mov(ff, 255))
    context.emit(And(d, c0, ff))
    return d

@isa.pattern("reg", "LABEL")
def pattern_label(context, tree):
    d = context.new_reg(PUC16Register)
    context.emit(MovL(d, tree.value))
    context.emit(MovTL(d, tree.value))
    return d

# Jumping around:
@isa.pattern("stm", "JMP")
def pattern_jmp(context, tree):
    tgt = tree.value
    context.emit(Jump(tgt.name, jumps=[tgt]))

@isa.pattern("stm", "CJMPI16(reg, reg)", size=3, cycles=2, energy=2, condition=lambda t: t.value[0] == "==" or t.value[0] == "!=")
@isa.pattern("stm", "CJMPI8(reg, reg)", size=3, cycles=2, energy=2, condition=lambda t: t.value[0] == "==" or t.value[0] == "!=")
def pattern_cjmpi(context, tree, c0, c1):
    op, yes_label, no_label = tree.value
    opnames = {
        "==": BZ,
        "!=": BNZ,
    }
    Bop = opnames[op]
    d = context.new_reg(PUC16Register)
    context.emit(Sub(d, c0, c1));
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)

@isa.pattern("stm", "CJMPU16(reg, reg)", size=3, cycles=2, energy=2)
@isa.pattern("stm", "CJMPU8(reg, reg)", size=3, cycles=2, energy=2)
def pattern_cjmpu(context, tree, c0, c1):
    op, yes_label, no_label = tree.value
    opnames = {
        "==": (BZ, False),
        "!=": (BNZ, False),
        "<": (BCC, False),
        ">": (BCC, True),
        "<=": (BCS, True),
        ">=": (BCS, False),
    }
    Bop, swap = opnames[op]
    d = context.new_reg(PUC16Register)
    if swap:
        context.emit(Sub(d, c1, c0))
    else:
        context.emit(Sub(d, c0, c1))
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)

@isa.pattern("stm", "CJMPI16(reg, CONSTI16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU16(reg, CONSTI16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI16(reg, CONSTU16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU16(reg, CONSTU16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI16(reg, CONSTI8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU16(reg, CONSTI8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI16(reg, CONSTU8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU16(reg, CONSTU8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI8(reg, CONSTI16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTI16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI8(reg, CONSTU16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTU16)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI8(reg, CONSTI8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTI8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI8(reg, CONSTU8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTU8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
def pattern_cjmp0(context, tree, c0):
    # Special case for comparison to 0 (more efficient)
    op, yes_label, no_label = tree.value
    opnames = {
        "==": BZ,
        "!=": BNZ,
    }
    Bop = opnames[op]
    d = context.new_reg(PUC16Register)
    context.emit(AddC(c0, c0, 0))
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)
