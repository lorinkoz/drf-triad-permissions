triadPermissions = (function () {
  const wildcards = {
    {% for wildcard, regex in TRIAD_WILDCARDS.items %}
      "{{ wildcard }}": /{{ regex }}/,
    {% endfor %}
  };
  return {
    match: function (query, perm, strict) {
      let queryChunks = query.split("{{ TRIAD_DIVIDER }}"),
        permChunks = perm.split("{{ TRIAD_DIVIDER }}");
      if (strict === undefined) {
        strict = true;
      }
      if (queryChunks.length != 3 || permChunks.length != 3) {
        return null;
      }
      for (let i = 0; i < queryChunks.length; i++) {
        if (
          (!wildcards[permChunks[i]] ||
            !wildcards[permChunks[i]].test(queryChunks[i])) &&
          (strict || queryChunks[i] !== "{{ TRIAD_SOFT_WILDCARD }}") &&
          queryChunks[i] !== permChunks[i]
        ) {
          return false;
        }
      }
      return true;
    },
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
