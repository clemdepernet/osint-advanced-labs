# Blockchain & Cryptocurrency — Cheat Sheet

_Core concepts and the commands to trace value on-chain. For OSINT / forensics use._

## Core idea

A **blockchain** is an append-only, public ledger replicated across many nodes. Transactions are grouped into **blocks**; each block carries the **hash** of the previous one, so altering the past breaks every later hash (tamper-evident). A **consensus** rule (proof-of-work / proof-of-stake) decides the next valid block. A **cryptocurrency** is value recorded on such a ledger; ownership is proven by cryptography, not by a bank account.

## Keys, addresses, signatures

| Term | What it is |
|---|---|
| Private key | secret number; signs transactions; **IS** control of the funds |
| Public key | derived from the private key (one-way; cannot reverse) |
| Address | short hash of the public key; what you share to receive funds |
| Seed / mnemonic | 12–24 words that regenerate all keys of a wallet |
| Signature | proves a transaction was authorised by the private key |

> Addresses are **pseudonymous, not anonymous**. One entity holds many addresses; re-linking them (clustering) is the tracer's core job.

## Two ledger models

| Model | Chains | How balances work |
|---|---|---|
| UTXO | Bitcoin, Litecoin | coins are discrete "unspent outputs", consumed & re-created |
| Account | Ethereum, Solana, BSC | a balance per address, like a bank account |

Every transaction is signed, timestamped and **permanent**. Inputs/outputs are the edges you follow.

## Where to look (explorers)

| Chain | Explorer |
|---|---|
| Bitcoin | blockchair.com, mempool.space, blockchain.com |
| Ethereum / EVM | etherscan.io, blockscout, bscscan.com |
| Solana | solscan.io, solana.fm |
| DeFi / tokens | dexscreener.com, geckoterminal.com, birdeye.so |
| Risk / rug | rugcheck.xyz, tokensniffer.com, honeypot.is |

## Query on-chain automatically

```bash
# Token metadata + trading pairs (DexScreener REST, keyless)
curl -s "https://api.dexscreener.com/latest/dex/tokens/<MINT>" | jq '.pairs[0]'
# Bitcoin address balance + txs (Blockchair)
curl -s "https://api.blockchair.com/bitcoin/dashboards/address/<ADDR>" | jq '.data'
# Ethereum balance via JSON-RPC
curl -s -X POST https://rpc.ankr.com/eth -H "content-type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xADDR","latest"],"id":1}'
# Ethereum tx list (Etherscan, needs a free key)
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xADDR&apikey=$KEY"
# Solana token risk (RugCheck)
curl -s "https://api.rugcheck.xyz/v1/tokens/<MINT>/report" | jq '{score,mintAuthority,freezeAuthority}'
```

## Tracing & clustering heuristics

- **Common-input**: inputs spent together are usually one owner (UTXO).
- **Change-address**: spot the wallet's own change output.
- **Deployer**: the signer of the token's first mint / liquidity-creation transaction.
- **Funding source**: follow the deployer's earliest inflow — CEX (KYC), mixer/bridge, or personal wallet.
- **Holder clustering**: many wallets created in the same minute receiving supply via bundled txs = insiders.

## Obfuscation (and its limits)

Mixers/tumblers, cross-chain **bridges** & chain-hopping, privacy coins (Monero, Zcash), **peel chains** (many small hops). Raises cost, rarely perfect — **entry/exit points still leak**.

## Chokepoints — where a name appears

Centralised **exchanges (KYC)**, on/off-ramps, OTC desks, payment processors, reused public addresses (donations, forums, X bios), IP/device leaks when using a service. Follow the money to a chokepoint.

## Token red flags (rug check)

- **Mint authority** not revoked → unlimited new supply.
- **Freeze authority** not revoked → can freeze your tokens.
- Liquidity **not** burned/locked; top holders clustered; brand-new socials.

> **OPSEC**: query from a burner/VM, rate-limit, never sign anything with a real wallet, keep provenance (tx hash, URL, UTC). Rate each link (Admiralty); heuristics are probabilistic.
