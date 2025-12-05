# >_ uv run --with check50 check50 --local ai50/projects/2024/x/knights

from logic import *


AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


# Abstracting the rules of the game
axiom = And(
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Biconditional(CKnight, Not(CKnave)),
)

ASays = lambda sentence: Biconditional(AKnight, sentence)
BSays = lambda sentence: Biconditional(BKnight, sentence)
CSays = lambda sentence: Biconditional(CKnight, sentence)


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    axiom,
    ASays(And(AKnight, AKnave))
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    axiom,
    ASays(And(BKnave, AKnave))
)


# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    axiom,
    ASays(Biconditional(AKnight, BKnight)),
    BSays(Biconditional(AKnight, BKnave))
)


# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    axiom,
    Biconditional(ASays(AKnight), Not(ASays(AKnave))),
    BSays(ASays(AKnave)),
    BSays(CKnave),
    CSays(AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
