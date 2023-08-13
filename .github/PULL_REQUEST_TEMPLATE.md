## Summary

What's the [new hotness](https://youtu.be/ha-uagjJQ9k?t=17)?

### Why?

What is my [purpose](https://youtu.be/X7HmltUWXgs?t=52)?

### How?

But how?!

## Checklist

Most checks are automated, but a few aren't, so make sure to go through and tick them off, even if they don't apply. This checklist is here to help, not deter you. Remember, "Slow is smooth, and smooth is fast".

- [ ] **Unit tests**
  - Every input should have a test for it.
  - Every potential raised exception should have a test ensuring it is raised.
- [ ] **Documentation**
  - New functions/classes/etc. must be added to `docs/api.rst`.
  - Changed/added classes/methods/functions have appropriate `versionadded`, `versionchanged`, or `deprecated` [directives](http://www.sphinx-doc.org/en/stable/markup/para.html#directive-versionadded).
  - The appropriate entry in `CHANGELOG.md` has been included in the "Unreleased" section, i.e. "Added", "Changed", "Deprecated", "Removed", "Fixed", or "Security".
- [ ] **Future work**
  - Future work should be documented in the contributor guide, i.e. `.github/CONTRIBUTING.md`.

If you have any questions not answered by a quick readthrough of the [contributor guide](https://pysparkplug.mattefay.com/en/latest/contributor_guide.html), add them to this PR and submit it.
