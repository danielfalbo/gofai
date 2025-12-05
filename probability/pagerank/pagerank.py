# >_ uv run --with check50 check50 --local ai50/projects/2024/x/pagerank

import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def adjusted(corpus):
    # Assume pages with no links have 1 link to each page in corpus
    pages_set = set(corpus.keys())
    for p in corpus:
        if len(corpus[p]) == 0:
            corpus[p] = pages_set
    return corpus


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_from_corpus = (1-damping_factor)/len(corpus)
    prob_from_curr_links = (damping_factor/len(corpus[page])
                            if len(corpus[page]) > 0 else 0)

    result = {}
    for p in corpus:
        is_linked_by_curr = p in corpus[page]
        result[p] = prob_from_corpus + (prob_from_curr_links
                                        if is_linked_by_curr else 0)

    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Assume pages with no links have 1 link to each page
    corpus = adjusted(corpus)

    visits = {c: 0 for c in corpus}

    probs = {p: 1/len(corpus) for p in corpus}
    for _ in range(n):
        curr = random.choices(list(probs.keys()), list(probs.values()))[0]
        visits[curr] += 1
        probs = transition_model(corpus, curr, damping_factor)

    visits_sum = sum(visits.values())
    return {p: visits[p]/visits_sum for p in corpus}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    PR = {page: 1/N for page in corpus}

    # Assume pages with no links have 1 link to each page in corpus
    corpus = adjusted(corpus)

    # Construct linked_by lookup table
    linked_by = {}
    for p in corpus:
        for link in corpus[p]:
            linked_by[link] = linked_by.get(link, set()) | {p}


    # Iterate
    last_max_delta = float('+inf')
    d = damping_factor
    NumLinks = lambda p: len(corpus[p]) if len(corpus[p]) > 0 else N
    while last_max_delta >= 0.001:
        last_max_delta = float('-inf')
        for page in PR:
            prev = PR[page]
            PR[page] = (1-d)/N + d*sum((PR[p]/NumLinks(p)
                                        for p in linked_by[page]), 0.0)
            diff = abs(prev - PR[page])
            last_max_delta = max(diff, last_max_delta)

    return PR


if __name__ == "__main__":
    main()
