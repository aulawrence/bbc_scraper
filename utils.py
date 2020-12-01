import re


def format_article_readability(article):
    """Format article for readability.
    Readability expects sentences separated by newline and words by space.

    Args:
        article (str): Article text.

    Returns:
        str: Article text formatted for readability.
    """
    return re.sub(r"([.?!]+)", r"\1\n", article)
