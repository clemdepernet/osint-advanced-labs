# Dark Web — Cheat Sheet

_Access safely, find services, investigate, and know the limits. Defensive / authorised use only._

## The layers of the web

| Layer | What | Example |
|---|---|---|
| Surface | indexed by search engines | public sites |
| Deep | not indexed, but reachable | intranets, DBs, paywalled, behind a form |
| Dark | needs special software | Tor `.onion`, I2P, Freenet |

> The **deep web** is the vast majority of the web and is **not** the dark web. Don't conflate them.

## Tor in one minute

- Tor anonymises **transport**: traffic is relayed through 3 nodes (guard → middle → exit); no single relay sees both who you are and what you fetch.
- A **hidden service** (`.onion`) is reachable only inside Tor; the server's location is hidden too.
- Tor does **not** anonymise **behaviour**: logins, writing style, metadata, and JavaScript can deanonymise you.

## Access safely (OPSEC first)

- Use a **dedicated VM** or **Tails** (amnesic OS), never your host.
- **Tor Browser** at the default security level; do not maximise the window, do not install add-ons.
- No personal accounts, no real identity, one **persona** per case (Day 1).
- Disable or be wary of JavaScript; never open downloaded files inside the VM without care.
- Verify onion addresses via a trusted directory — clones for phishing are everywhere.

```bash
# Check you are actually going through Tor
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
# Fetch an onion over Tor from the CLI
curl --socks5-hostname 127.0.0.1:9050 http://<onion>.onion/
torsocks <tool>            # torify a tool with no proxy option
```

## Finding hidden services

| Source | Use |
|---|---|
| dark.fail | verified onion directory (anti-phishing mirror list) |
| Ahmia (ahmia.fi) | onion search engine (clearnet-accessible) |
| Tor.taxi | curated links directory |
| onion indexers | keyword search of `.onion` services |

> Cross-check any onion via **dark.fail** before visiting: known forums/markets are massively cloned to steal logins and crypto.

## Investigating

- **Compartmentalise** access (VM, Tor, burner accounts) — one setup per case.
- **Capture everything**: Hunchly, screenshots, full HTML, plus URL + UTC + SHA-256 (chain of custody).
- **Translate & normalise** foreign-language content; record the original.
- **Pivot** to the clearnet: reused handles, PGP keys, crypto addresses, contact emails, analytics IDs.
- Log every entity with an **Admiralty** rating and confidence per hop.

## Deanonymisation vectors (how services leak)

- Operator OPSEC errors (reused pseudonyms, PGP keys, emails, crypto addresses).
- Server misconfig (SSH banners, TLS certs, status pages, leaked real IP).
- Bitcoin/crypto flows to KYC chokepoints.
- Correlation via writing style, hours of activity, shared infrastructure.

## Legal & ethical limits

Viewing, test purchases, and infiltration are **strictly regulated** (jurisdiction + your status). Never access, download or scrape illegal content. For child-abuse material: do **not** interact — record the URL and report to the authorities (NCMEC / national hotline). Validate the legal perimeter **before** acting.

## Tools

`Tor Browser` · `Tails` · `torsocks` / `proxychains4` · `OnionScan` (audit a service you own) · `Hunchly` (capture) · `curl --socks5-hostname` · `dark.fail` / `Ahmia` (discovery).

> **Golden rule**: passive, authorised, compartmentalised, documented. The dark web leaks — through error, chokepoints and terminals — but only careful, legal work turns a leak into evidence.
