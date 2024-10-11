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

    output = dict()
    key_number = len(corpus.keys())

    if len(corpus[page]) == 0:
        prob = 1 / key_number
        for key in corpus.keys():
            output[key] = prob
    else:
        prob = (1 - damping_factor) / key_number
        for key in corpus.keys():
            output[key] = prob
        value_number = len(corpus[page])
        damping_prob = damping_factor / value_number
        for linked_page in corpus[page]:
            output[linked_page] += damping_prob

    return output


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys = list(corpus.keys())
    page = random.choice(keys)
    output = dict()

    for k in corpus.keys():
        output[k] = 0

    for i in range(SAMPLES):
        tmp = transition_model(corpus, page, damping_factor)
        rand = random.random()
        total = 0
        for (k, v) in tmp.items():
            total += v
            if total > rand:
                page = k
                break

        output[page] += 1

    total_sum = 0
    for val in output.values():
        total_sum += val

    for k in output.keys():
        output[k] = output[k] / total_sum

    return output


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pr = dict()
    equal_prob = 1 / len(corpus.keys())
    for key in corpus.keys():
        pr[key] = equal_prob

    difference = set()
    prob = (1 - damping_factor) / len(corpus.keys())
    while True:
        for key in pr.keys():
            tmp = pr[key]
            total = 0
            for (k, v) in corpus.items():
                if key in v:
                    num_links = len(corpus[k])
                    if num_links == 0:
                        total += (pr[k] / len(corpus))
                    else:
                        total += (pr[k] / num_links)

            pr[key] = prob + damping_factor * total
            difference.add(abs(pr[key] - tmp))

        if max(difference) <= 0.001:
            break

        difference = set()

    total = 0
    for v in pr.values():
        total += v

    for k in pr.keys():
        pr[k] = (pr[k] / total)

    return pr


if __name__ == "__main__":
    main()
