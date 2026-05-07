## Summary

- Summarize the change here.

## Type of Change

- [ ] Documentation only
- [ ] Test only
- [ ] Bug fix
- [ ] Feature
- [ ] Deployment preparation

## Safety Checklist

- [ ] No secrets, tokens, private keys, cookies, or service credentials are included.
- [ ] `.env`, database files, logs, and tunnel output are not committed.
- [ ] Pharmacy safety boundaries are preserved.
- [ ] No diagnosis, prescription replacement, dosage advice, or medication change advice was added.
- [ ] Bale API assumptions were updated in `docs/ASSUMPTIONS_BALE_API.md` if behavior changed.

## Verification

- [ ] `python -m unittest discover -s tests`
- [ ] `python -m compileall app tests`
- [ ] `git diff --check`

## Notes
