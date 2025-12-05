"""
Toy Proof Checker
https://youtube.com/watch?v=IOiZatlZtGU
https://wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence
"""


from dataclasses import dataclass

# We start by implementing a simple typed programming language.
# We will skip parsing, we will just assume we're dealing with the AST.


# ============= Language Types =============
# Types are Propositions.


@dataclass
class IntType:
    def __repr__(self): return "Int"


@dataclass
class BoolType:
    def __repr__(self): return "Bool"


# For generalization and convenience, we can use our own dataclass 'Type'.


@dataclass
class Type:
    pass


@dataclass
class Atom(Type):
    """A basic proposition like 'A' or 'B'"""
    name: str
    def __repr__(self): return self.name


@dataclass
class Arrow(Type):
    """
    Represents Implication (A -> B).
    If you have a proof of left, you can get a proof of right.
    """
    left: Type
    right: Type
    def __repr__(self): return f"({self.left} -> {self.right})"


# ============= Language Code ==============
# AST Nodes are Proofs.

# We use 'any' for expressions nodes types because we want to be able to
# represent invalid programs and use a type checker to check their validity.


@dataclass
class Add:
    left: any
    right: any


@dataclass
class If:
    condition: any
    then_branch: any
    else_branch: any


# Actually, we can use our own 'Proof' dataclass here.
# When you see 'Proof', think of 'any' as above in the sense that
# a proof can be valid or invalid.

@dataclass
class Proof:
    """Base class for Proof terms (Programs)"""
    pass


@dataclass
class Num(Proof):
    value: int


@dataclass
class Bool(Proof):
    value: bool


@dataclass
class Var(Proof):
    """Variable: think of this as 'an assumption'"""
    name: str
    def __repr__(self): return self.name


@dataclass
class Lam(Proof):
    """
    Lambda Abstraction: Function Definition.
    This of this as an implication.
    To prove A -> B, we assume A (var_name, var_type) and prove B (body),
        λ a: b.
    """
    var_name: str
    var_type: Type  # The assumption A
    body: Proof     # The proof of B
    def __repr__(self):
        return f"(λ{self.var_name}:{self.var_type}. {self.body})"


@dataclass
class App(Proof):
    """
    Function Application.
    This corresponds to Modus Ponens.
    If we have (A -> B) and we have A, we get B.
    """
    func: Proof
    arg: Proof
    def __repr__(self): return f"({self.func} {self.arg})"


# ============= Type Checking ==============
# Types are Proposition,
# Programs are Proofs,
# being a Program with a valid Type means being the Proof of a True Proposition.


class TypeCheckError(Exception):
    pass


# Variables = Hypotheses
# Context will be a lookup table for the
#   types/values of our assumptions/variables.
# Nodes are Proofs as described above.
def check(ctx, node):
    """
    Asserts that the node is valid under our type system,
    throws a TypeCheckError if it's not.
    """


    # Base Cases: Literals

    if isinstance(node, Num):
        return IntType()

    if isinstance(node, Bool):
        return BoolType()


    # Variables

    if isinstance(node, Var):
        if node.name not in ctx:
            raise TypeCheckError(f"Use of unproven assumption: {node.name}")
        return ctx[node.name]


    # Addition

    if isinstance(node, Add):
        left_type = check(ctx, node.left)
        right_type = check(ctx, node.right)

        # Rule: Both sides must be Int
        if (not isinstance(left_type, IntType)
                or not isinstance(right_type, IntType)):
            raise TypeCheckError(
                f"Add expects Ints, got {left_type} and {right_type}")

        return IntType()


    # If-Statement

    if isinstance(node, If):
        cond_type = check(ctx, node.condition)
        then_type = check(ctx, node.then_branch)
        else_type = check(ctx, node.else_branch)

        # Rule: Condition must be Bool
        if not isinstance(cond_type, BoolType):
            raise TypeCheckError(f"If condition must be Bool, got {cond_type}")

        # Rule: Branches must match
        if then_type != else_type:
            raise TypeCheckError(
                f"Branches mismatch: then={then_type}, else={else_type}")

        return then_type


    # Function Definition: Implication.

    if isinstance(node, Lam):
        # Evaluate the Lambda's body inside a new context
        # where the assumption is true.
        # In other words, evaluate the Lambda's body in a new context
        # where the given variable is of the given type.
        body_type = check({**ctx, node.var_name: node.var_type},
                          node.body)
        # The check above will fail when body will not be valid given the arg.
        return Arrow(node.var_type, body_type)


    # Function Application: If (A->B) and A, B.

    if isinstance(node, App):
        func_type = check(ctx, node.func)
        arg_type = check(ctx, node.arg)

        if not isinstance(func_type, Arrow):
            # Attempting to call something that's not a function.
            raise TypeCheckError(
                f"Attempting to apply logic to non-implication: {func_type}")

        # The Moment of Truth: Does the argument match the requirement?
        if func_type.left != arg_type:
            raise TypeCheckError(
                f"""Logic Mismatch: Needed proof of {func_type.left},
                got {arg_type}""")

        # You're Right!
        return func_type.right

    raise TypeCheckError(f"Unknown node: {node}")


if __name__ == '__main__':
    program_valid = If(condition=Bool(True),
                       then_branch=Add(Num(5), Num(3)),
                       else_branch=Num(0))

    assert(type(check({}, program_valid)) == IntType)

    try:
        program_invalid = If(condition=Num(9),
                             then_branch=Add(Num(5), Num(3)),
                             else_branch=Num(0))
        check({}, program_invalid)
        assert(False is True)
    except TypeCheckError:
        assert(True)
    except:
        assert(False)

    A = Atom("A")

    # We want to prove A -> A.
    # If we can construct a valid program of type A, we win.
    # Let's try: x:A in x.
    proof = Lam(var_name='x', var_type=A, body=Var("x"))

    try:
        NO_ASSUMPTIONS_CTX = {}
        proven = check(NO_ASSUMPTIONS_CTX, proof)

        assert(proven == Arrow(A, A))
        # Hooray! A -> A
    except TypeCheckError as e:
        # We know A -> A, this will not happen.
        assert(False)
    except:
        # Our proof assistant must be bugs free ;)
        assert(False)

    print('all tests successful')
