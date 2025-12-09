# >_ uv run --with check50 check50 --local ai50/projects/2024/x/heredity

import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": { 2: 0.01, 1: 0.03, 0: 0.96 },

    "trait": {
        # Probability of trait given two copies of gene
        2: { True: 0.65, False: 0.35 },

        # Probability of trait given one copy of gene
        1: { True: 0.56, False: 0.44 },

        # Probability of trait given no gene
        0: { True: 0.01, False: 0.99 }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": { 2: 0, 1: 0, 0: 0 },
            "trait": { True: 0, False: 0 }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def get_genes_count(name, one_gene, two_genes):
    return (1 if name in one_gene else
            2 if name in two_genes else 0)

def get_pass_prob(count):
    """
    Returns the probability of a parent with 'count' genes
    pasing the gene to the child.
    """
    if count == 2: return 1 - PROBS['mutation']
    elif count == 1: return 0.5
    else: return PROBS['mutation']

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    p = 1.0

    for person in people.values():
        name = person['name']
        mother, father = person['mother'], person['father']

        genes_query = get_genes_count(name, one_gene, two_genes)
        trait_query = name in have_trait

        is_parents_data_available = mother is not None

        # Compute and apply probability of genes_query to result.
        if is_parents_data_available:
            m_genes = get_genes_count(mother, one_gene, two_genes)
            f_genes = get_genes_count(father, one_gene, two_genes)

            # Note: mother passing the gene and father passing
            # the gene are independent events.
            m_pass_prob = get_pass_prob(m_genes)
            f_pass_prob = get_pass_prob(f_genes)

            child_genes_probs = {
                # mother passes gene AND father passes gene
                2: m_pass_prob * f_pass_prob,

                # (mather passes gene AND father doesn't)
                #   OR
                # (father passes gene AND mother doesn't)
                1: (m_pass_prob * (1 - f_pass_prob)) + (f_pass_prob * (1 - m_pass_prob)),

                # father doesn't pass gene AND mother doesn't either
                0: (1 - f_pass_prob) * (1 - m_pass_prob)
            }

            p *= child_genes_probs[genes_query]
        else:
            p *= PROBS['gene'][genes_query]

        # Compute and apply probability of trait_query to result
        p *= PROBS['trait'][genes_query][trait_query]

    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for name in probabilities:
        genes = get_genes_count(name, one_gene, two_genes)
        trait = name in have_trait
        probabilities[name]['gene'][genes] += p
        probabilities[name]['trait'][trait] += p
    return probabilities


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for name in probabilities:
        genes_probs_sum = sum(probabilities[name]['gene'].values())
        trait_probs_sum = sum(probabilities[name]['trait'].values())
        probabilities[name]['gene'] = {
            count: probabilities[name]['gene'][count] / genes_probs_sum
            for count in (2,1,0)
        }
        probabilities[name]['trait'] = {
            True:  probabilities[name]['trait'][True]  / trait_probs_sum,
            False: probabilities[name]['trait'][False] / trait_probs_sum
        }
    return probabilities


if __name__ == "__main__":
    main()
