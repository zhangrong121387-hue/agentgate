# AgentGate — Agent ID-gated drops on BNB Smart Chain

**One verified person. One pass. No Sybil farms.**

AgentGate is a reusable smart-contract gate that lets any project on BNB Smart
Chain restrict a function — a mint, a drop, a claim — to holders of a
**SPACE ID Agent ID**. It ships with a working reference product, the
**AgentGate Badge**: a free commemorative ERC-721 that only Agent ID holders
can mint, one per person, ever.

- **Project name:** AgentGate
- **One-liner:** An open-source, inherit-and-go gate that makes any BSC drop
  Sybil-resistant by checking the caller's Agent ID — plus a live free badge
  drop that proves it end to end.
- **Chain:** BNB Smart Chain (BSC, chain id 56)
- **License:** MIT
- **Status:** Phase 1 — contracts written, compiled and fully tested locally;
  web page built. Deployment to BSC mainnet is phase 2 (see checklist below).

---

## How Agent ID is used — the core mechanic

The Agent ID contract on BSC
(`0x60b9262456de011f7d15a54cdd8c48baaa8b022f`, "SPACE ID Agent ID", symbol AI)
is an ERC-721 whose tokens are **non-transferable identity credentials**:
one verified (KYC) person can claim exactly one, shaped like `name.ai`.

AgentGate turns that fact into a primitive:

```solidity
hasAgentID(account)  ==  IAgentID(0x60b9...022f).balanceOf(account) > 0
```

Because the identity is one-per-person and cannot be transferred or sold:

- **Sybil resistance without an allowlist.** A farmer with 1,000 fresh
  wallets holds at most one Agent ID, so they pass the gate at most once.
  No list for the project to maintain, no signatures to issue.
- **Per-person (not per-wallet) claim tracking.** The badge contract records
  `claimed[address]`, and the gate guarantees that a *second* address
  controlled by the same person has no Agent ID to pass with. Together:
  one badge per human, permanently.
- **The identity is the centerpiece, not a sticker.** Every mint emits
  `AgentIDVerified(holder)` alongside `BadgeMinted(holder, tokenId)`, the
  gate contract address is `immutable` (it can never be swapped for a weaker
  identity contract), and the gate fails closed — if the identity check
  doesn't pass, nothing mints.

The gate is a base contract (`contracts/AgentGate.sol`) any project inherits:

```solidity
contract MyDrop is AgentGate {
    constructor() AgentGate(0x60b9262456de011f7d15a54cdd8c48baaa8b022f) {}

    function mint() external {
        _requireAgentID();  // reverts unless caller holds an Agent ID
        // ... your logic ...
    }
}
```

## Architecture

```
contracts/
├── IAgentID.sol        Minimal interface: balanceOf only — the smallest
│                       possible trust surface on the identity contract.
├── AgentGate.sol       The reusable gate (abstract base contract).
│                       Immutable Agent ID address, hasAgentID(),
│                       _requireAgentID() / _requireAgentIDOf().
├── AgentGateBadge.sol  The reference product: free ERC-721 badge,
│                       Agent ID-gated mint(), one claim per address ever,
│                       owner-controlled window, shrink-only supply cap.
├── ERC721Minimal.sol   Self-contained ERC-721 + Ownable implementations.
│                       Zero external dependencies, so the source verified
│                       on BscScan is exactly the source you can read here.
└── MockAgentID.sol     TEST ONLY stand-in for the identity contract.
                        Never deployed to mainnet.
test/
└── AgentGateBadge.test.js   22 Hardhat tests (see BUILD-LOG.md).
web/
└── index.html          Single self-contained page: eligibility checker
                        (live Agent ID read via public BSC RPC), demo mint,
                        integration guide, owner-powers disclosure.
```

## Owner powers — explicit disclosure

The badge contract's owner can do exactly three things, and nothing else:

1. **Open or close the mint window** — `setMintOpen(bool)`.
2. **Lower the supply cap** — `setMaxSupply(uint256)`. The cap can *never*
   be raised, and never set below the amount already minted.
3. **Transfer or renounce ownership** — renouncing freezes powers 1–2
   forever.

The owner **cannot**:

- mint badges (there is no owner mint function; the owner must call the
  public `mint()` and pass the same Agent ID gate as everyone else);
- block, pause or reverse badge transfers (badges are plain, freely
  transferable ERC-721 tokens);
- charge or enable fees of any kind;
- withdraw funds — the contract has **no payable functions**, no
  receive/fallback, and can never hold a balance;
- change the metadata URI, the token name/symbol, or the Agent ID contract
  the gate checks (all fixed at construction; the gate address is
  `immutable`).

## Safety & compliance notes (vs. the hackathon red lines)

- **Open source, owner powers disclosed:** this README and the contract
  header both enumerate every owner power; source will be verified on
  BscScan at deployment.
- **No promised returns:** the badge is a free commemorative proof of
  identity. It promises nothing of value, and the web page says so.
- **No Binance impersonation:** the project and token are named
  "AgentGate" / "AgentGate Badge" (AGB) — no "Binance", "币安" or "BNB"
  branding; the web page footer explicitly states the project is not
  affiliated with or endorsed by Binance or SPACE ID.
- **No user secrets, ever:** the contracts and page never ask for seed
  phrases, private keys, pairing codes or login sessions. Minting is a
  normal transaction the user signs and confirms in their own wallet.
- **No silent asset movement:** the only state-changing user action is the
  user's own `mint()` call. There are no approvals, no transfers out, no
  scheduled or automatic operations.
- **Not a "look up anyone's wallet" tool:** the eligibility checker only
  answers "does this address hold an Agent ID: yes/no" for an address the
  visitor types in themselves — the same public `balanceOf` read anyone
  can make — and resolves no names to wallets.

## Build & test locally

Requirements: Node.js ≥ 18, npm.

```bash
npm install        # Hardhat 2.29 + toolbox + ethers 6 (dev dependencies)
npx hardhat compile
npx hardhat test   # 22 tests, all passing — see BUILD-LOG.md
```

Compiler: Solidity 0.8.24, optimizer 200 runs, EVM target `paris`
(BSC-compatible). The web page has no build step: open `web/index.html`
in a browser (serve it with any static server, e.g. `npx serve web`).

## Deployment checklist (phase 2)

1. **Prepare metadata:** upload the badge metadata JSON to IPFS (or a stable
   HTTPS URL); this becomes the constructor's `metadataURI`.
2. **Deploy** `AgentGateBadge` (e.g. via Remix) with:
   - `agentIDAddress` = `0x60b9262456de011f7d15a54cdd8c48baaa8b022f`
   - `metadataURI` = the URI from step 1
   - `maxSupply` = `10000`
   Fund the deployer with a small amount of BNB for gas (a few cents).
3. **Verify on BscScan:** submit the flattened/standard-JSON source
   (solc 0.8.24, optimizer 200 runs) until the contract shows as verified
   and open source; double-check the constructor arguments decode.
4. **Wire the web page:** set `CONFIG.BADGE_CONTRACT` in `web/index.html`
   to the deployed address; host the page (project site).
5. **Open the drop:** call `setMintOpen(true)` from the owner wallet.
   Sanity-check one real mint from an Agent ID-holding wallet and one
   rejection from a wallet without an Agent ID before announcing.
6. **Promote & track:** announce the free badge to Agent ID holders;
   the innovation-award threshold is ≥ 30 distinct Agent ID addresses
   interacting with the contract during the event window — monitor
   `BadgeMinted` events / BscScan.
7. **Submit** the hackathon entry (project name, site URL, contract
   address, Agent ID usage explanation — draft below) before
   **2026-12-09 16:00 CST**.
8. *(Optional, post-submission)* renounce ownership once the drop is in
   its final state, freezing the window/cap settings permanently.

---

## Hackathon submission blurb (draft)

- **Project name:** AgentGate
- **One-liner:** One verified person, one pass — an open-source Agent ID
  gate that makes any BSC drop Sybil-resistant, proven live by a free
  badge drop.
- **Website:** *(to fill after hosting — phase 2)*
- **Contract (BSC):** *(to fill after deployment — phase 2)*
- **How Agent ID is used:** AgentGate's core mechanic *is* the Agent ID.
  The gate contract checks `balanceOf` on the SPACE ID Agent ID contract
  (`0x60b9...022f`) before any protected function runs; because an Agent
  ID is non-transferable and issued one-per-verified-person, passing the
  gate means "a unique verified human", not "an address on a list". The
  reference product, AgentGate Badge, combines the gate with a permanent
  per-address claim record to enforce one free badge per person, ever —
  a second wallet doesn't help a farmer, because it holds no Agent ID.
  The same three-line integration (`AgentGate` inheritance +
  `_requireAgentID()`) is offered to every other project as an MIT-licensed
  base contract, so Agent ID becomes the default admission ticket for
  drops across the ecosystem rather than a one-off integration.
