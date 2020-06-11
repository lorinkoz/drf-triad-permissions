triadPermissions = (function () {
  const wildcards = {{% for wildcard, regex in WILDCARDS.items %}
    "{{ wildcard }}": /{{ regex }}/,{% endfor %}
  };
  function match(query, perm, strict) {
    let queryChunks = query.split("{{ TRIAD_DIVIDER }}"),
      permChunks = perm.split("{{ TRIAD_DIVIDER }}");
    if (strict === undefined) {
      strict = true;
    }
    if (queryChunks.length !== 3 || permChunks.length !== 3) {
      return null;
    }
    for (let i = 0; i < queryChunks.length; i++) {
      if (
        (!wildcards[permChunks[i]] ||
          !wildcards[permChunks[i]].test(queryChunks[i])) &&
        (strict || queryChunks[i] !== "{{ NON_STRICT_PLACEHOLDER }}") &&
        queryChunks[i] !== permChunks[i]
      ) {
        return false;
      }
    }
    return true;
  }
  return {
    match: match,
    matchAny: function (query, perms, strict) {
      if (perms === undefined) {
        perms = [];
      }
      return perms.some(function (x) {
        return match(query, x, strict);
      });
    },
    matchAll: function (query, perms, strict) {
      if (perms === undefined) {
        perms = [];
      }
      return perms.every(function (x) {
        return match(query, x, strict);
      });
    },
  };
})();
