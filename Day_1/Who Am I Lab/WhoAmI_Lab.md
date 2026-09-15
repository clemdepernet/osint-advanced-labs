# Who Am I?

## Lab Assignment: Opening Challenge — Profile Your Instructor

**Duration:** 75 min (45 min investigation, 15 min briefings, 15 min debrief)
**Position in the course:** Day 1, first session, before any theory.

### Why this challenge

You have all done OSINT before. Before we teach you anything, show us how you work. Your target is the person standing in front of you. You know the name, you know the face. Everything else you must find, source and rate. The instructor knows the ground truth, so what gets scored is not how *much* you find, but how much of it is **true, sourced and obtained within the rules**.

### Learning Objectives

By the end of this session, you will be able to:

- Run a time-boxed passive OSINT collection on a consenting real person.
- Pivot from a single seed (name + face) to identifiers, affiliations, places and timeline.
- Rate every finding with the **Admiralty scale** (source reliability × information credibility).
- Distinguish a verified fact from a plausible inference and from a fabrication.
- Notice what your *own* investigation leaked to the target.

---

## Rules of Engagement (read, sign, then start)

These rules are not optional. Breaking one disqualifies the team's briefing.

| # | Rule |
|---|---|
| 1 | **Passive only.** You read what is public. You do not contact, message, friend, follow, connect with, call or email the target, their employer, colleagues or relatives. |
| 2 | **No authentication as the target.** No password reset, no "forgot password" flows, no login attempts, no `holehe`-style probes that trigger emails to the target. |
| 3 | **No paid or leaked data.** No data-breach dumps, no people-search subscriptions, no dark-web sources. Free public web only. |
| 4 | **Family and minors are out of scope.** If you land on a relative, note "family member exists" and stop. No names, no photos. |
| 5 | **Location stops at the city.** City and country are in scope. Street address, building, licence plate, home photos are **forbidden** even if public. |
| 6 | **Same rules for AI assistants.** You may use an LLM to plan or summarise, but every fact must come from a URL you opened yourself. An unsourced fact scores negative. |
| 7 | **Time-box.** 45 minutes. Pens down when the timer rings. |
| 8 | **Destruction.** At the end of the debrief, every team deletes its notes, downloads and browser history related to the target, in front of the instructor. |

Sign the ROE sheet (`templates/rules_of_engagement.md`) as a team before you open a browser.

---

## Step 0 — Teams and setup (5 min)

- Teams of 3, **mixed nationalities** (one German, one Indian, one French speaker per team when possible). Working language: English.
- One shared document per team, the **Intel Card** (`templates/intel_card.md`). One person owns it. Every entry needs: fact, source URL, date seen, Admiralty rating.
- Decide *now*, before the first search, which browser profile and which accounts you will use. Write that decision at the top of the card. You will be asked about it.

---

## Step 1 — Collection (45 min)

Seed: the instructor's **full name** as written on the course schedule, and their **face**.

Suggested pivots (not a checklist — pick, justify, move on):

| Pivot | What to look for | Typical tools (free) |
|---|---|---|
| Name | professional profiles, publications, talks, company registers, press | search engines with quotes, LinkedIn, company registries (Infogreffe/Pappers, Handelsregister, MCA) |
| Handle | reuse of a username across platforms | WhatsMyName, `sherlock`, `maigret` |
| Face | other profiles using the same photo, event photos | Google Lens, Yandex Images, TinEye, PimEyes (free tier, no account) |
| Employer / school | timeline, colleagues, alumni pages, conference speaker lists | employer site, Wayback Machine, Bing |
| Domain | personal website, WHOIS history, certificates | `whois`, crt.sh, Wayback CDX |
| Content | writing style, topics, languages, hours of activity | GitHub, Medium, Twitter/X, YouTube, podcasts |

**Mandatory fields of the Intel Card**

1. Identity: full name, approximate age or birth year, nationality.
2. Location: current city/country (city level only).
3. Career: current employer/role, two previous positions, education.
4. Digital: at least one username, one personal domain or email *pattern* (not the address), one photo reused across platforms.
5. Interests/community: two verifiable interests or affiliations (talks, clubs, certifications, open-source).
6. Timeline: five dated events.
7. **Confidence**: every fact rated A1 → F6 (see scale below).
8. **What we did not find** and why (blocked, out of scope, no time).
9. **Our own footprint**: which accounts/browser/IP did we use? Could the target see us?

### The Admiralty scale (use it on every line)

| Source reliability | | Information credibility | |
|---|---|---|---|
| **A** | completely reliable (official register, target's own verified profile) | **1** | confirmed by other independent sources |
| **B** | usually reliable (employer site, established press) | **2** | probably true |
| **C** | fairly reliable (conference site, alumni page) | **3** | possibly true |
| **D** | not usually reliable (aggregator, people-search site) | **4** | doubtful |
| **E** | unreliable (anonymous forum, AI summary) | **5** | improbable |
| **F** | cannot be judged | **6** | cannot be judged |

A fact rated **A1** with a wrong source URL scores as fabrication. Be honest: a **C3** that is true beats an **A1** that is false.

---

## Step 2 — Briefing (15 min, 3 min per team)

One speaker per team. Format, strictly:

1. Three facts you are **most confident** about, with rating and source.
2. One fact you found **surprising** or hard to get, and the pivot that got you there.
3. One thing you **deliberately did not report** because of the ROE.
4. Your **own footprint**: could the target know your team looked?

No slides. Read from the Intel Card.

---

## Step 3 — Debrief and reveal (15 min)

The instructor discloses the ground truth. Each team corrects its card in red. Then the instructor shows **who viewed their profiles** during the last hour, and what that means for the rest of the day.

Questions to answer in your team, in writing, on the card:

3.1 How many of your facts were true? How many were inferences you presented as facts? How many were fabricated (by you or by a tool)?

3.2 Which single pivot produced the most value? Which one wasted the most time?

3.3 Did your team appear in the target's "who viewed" lists, notifications or logs? If yes, what would you change tomorrow?

3.4 What did the target *fail* to protect that you would fix first if you were them?

Then **Rule 8**: delete everything, in front of the instructor. The Intel Cards are handed over on paper or moved to the instructor's folder; no copy stays with the teams.

---

## Scoring (announced up front, 100 pts)

| Item | Points | Detail |
|---|---|---|
| True facts, correctly sourced | 40 | +4 per mandatory field met with a working source, max 10 fields |
| Pivot depth | 15 | +5 per pivot chain of ≥ 2 hops (name → handle → other platform), max 3 |
| Rating quality | 15 | Admiralty ratings consistent with the sources actually used |
| Honesty | 10 | "not found / out of scope" section filled truthfully |
| Briefing | 10 | clear, timed, one speaker, format respected |
| **OPSEC malus** | −5 each | team member visible in the target's profile viewers, notifications or any log |
| **Fabrication malus** | −5 each | fact with no URL, dead URL, or URL that does not contain the fact |
| **ROE breach** | disqualified | contact, login attempt, family, street address, paid/leaked data |

Highest score wins nothing but the right to be first in the next challenge. Lowest OPSEC malus wins the instructor's respect, which is worth more.

---

## What this challenge is really about

You will see today that hiding your IP is not enough, that a persona built in five minutes is a liability, and that a browsing session you cannot document is worthless in a report. Everything you did (or failed to do) in the last 45 minutes is the material for the rest of Day 1.
