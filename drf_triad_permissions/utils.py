from .matching import match_any


def triad_superset(triads):
    """
    From a list of triads, remove all triads that are more restrictive than other triads.
    """
    final = []
    while triads:
        # Pick first triad from the list and make it reference
        query = triads.pop()
        # Include the reference only if it cannot be matched by another triad
        # Namely, discard the triad if it can be matched by another triad
        if not match_any(query, triads):
            final.append(query)
    return final
