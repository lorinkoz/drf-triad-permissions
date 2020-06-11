from .settings import TRIAD_DIVIDER, NON_STRICT_PLACEHOLDER, COMPILED_WILDCARDS


def match(query, perm, strict=True):
    """
    Matches a query against a permission.
    Query must be less or equally restrictive than the permission.
    """
    query_chunks = query.split(TRIAD_DIVIDER)
    perm_chunks = perm.split(TRIAD_DIVIDER)
    if len(query_chunks) != 3 or len(perm_chunks) != 3:
        return None
    for query_chunk, perm_chunk in zip(query_chunks, perm_chunks):
        if (
            (perm_chunk not in COMPILED_WILDCARDS or not COMPILED_WILDCARDS[perm_chunk].match(query_chunk))
            and (strict or query_chunk != NON_STRICT_PLACEHOLDER)
            and query_chunk != perm_chunk
        ):
            return False
    return True


def match_any(query, perms, strict=True):
    """
    Matches a query against a list of permissions.
    Only one match is required to 'match any'.
    """
    for perm in perms:
        if match(query, perm, strict):
            return True
    return False


def match_all(query, perms, strict=True):
    """
    Matches a query against a list of permissions.
    All matches are required to 'match all'.
    """
    for perm in perms:
        if not match(query, perm, strict):
            return False
    return True
