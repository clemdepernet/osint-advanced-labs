# OPSEC note - threat model & protection level

_Fill this BEFORE creating anything (persona, container, browser profile). One page max._

| Item | Answer |
|---|---|
| Case ID | |
| Investigator (internal ref only, never the real name here) | |
| Date (UTC) | |
| Legal basis / who authorised the persona | |

## 1. Who am I protecting against?
- [ ] Opportunist / curious target (checks who viewed the profile)
- [ ] Organised group (checks fingerprints, correlates accounts, retaliates)
- [ ] State-level / platform insider (subpoenas, logs, telemetry)

## 2. What must I protect?
- [ ] My real identity
- [ ] The existence of the investigation
- [ ] My methods and tooling
- [ ] The identity of my client / employer

## 3. Consequences of compromise
Describe in 2-3 lines what happens if the target links the persona to you or to the case
(target goes dormant, evidence destroyed, harassment, physical risk, legal exposure...).

## 4. Effort the adversary will invest
Low / Medium / High - and why.

## 5. Chosen attribution posture
- [ ] Non-attribution (passive, nothing ties to me)
- [ ] Managed attribution (persona, plausible & consistent)
- [ ] Attribution (open, official)

## 6. Countermeasures (proportionate to 1-4)

| Layer | Decision | Rationale |
|---|---|---|
| Machine (host / VM / disposable container) | | |
| Network exit (direct / VPN / Tor / VPN->Tor) | | |
| Browser (profile / Tor Browser / anti-fingerprint) | | |
| Identity (none / persona / real) | | |
| Evidence capture (Hunchly / manual / none) | | |
| Data at rest (encrypted volume? retention?) | | |

## 7. Explicit trade-offs accepted
What did you decide NOT to protect, and why is that acceptable for this case?
