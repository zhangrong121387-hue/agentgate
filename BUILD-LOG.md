# AgentGate — Build Log

## Phase 1 — 2026-11-18 (local only; nothing deployed, no wallet touched)

### Environment & toolchain
- Node v24.22.1, npm 10.9.4
- Hardhat **2.29.2** (`hardhat@^2.26.0` resolved), `@nomicfoundation/hardhat-toolbox@^5.0.0`, `ethers@^6.13.0`
- Solidity compiler **0.8.24** (downloaded by Hardhat), optimizer enabled (200 runs), EVM target `paris` (chosen for BSC compatibility — avoids post-Paris opcodes)
- `npm install`: 637 packages, ~2 min, no errors

### What was built
| File | Notes |
|---|---|
| `contracts/IAgentID.sol` | Minimal interface — `balanceOf` only. |
| `contracts/AgentGate.sol` | Reusable gate base contract; `immutable` Agent ID address; `hasAgentID`, `_requireAgentID`, `_requireAgentIDOf`; canonical `AgentIDVerified` event; typed `NoAgentID` error; fails closed. |
| `contracts/AgentGateBadge.sol` | Demo badge "AgentGate Badge" (AGB). Free `mint()`, Agent ID-gated, one claim per address ever (`claimed` mapping, never reset), supply cap, owner open/close window, fixed `metadataURI` set at construction (no setter). |
| `contracts/ERC721Minimal.sol` | Hand-written, dependency-free ERC-721 (metadata ext., safe-mint receiver check, standard approvals/transfers) + `OwnableMinimal` (transfer/renounce). No hooks, no fees, no blocking. |
| `contracts/MockAgentID.sol` | Test-only identity stub (permissionless register/unregister). Never for deployment. |
| `test/AgentGateBadge.test.js` | 22 tests, Hardhat + chai matchers. |
| `web/index.html` | Single self-contained page; inline CSS/JS; hand-rolled ABI selectors (computed with ethers and cross-checked); fetch-based JSON-RPC with two BSC RPC fallbacks; `window.ethereum` for connect/mint. JS syntax verified with `node --check`. |
| `README.md` | Intro, mechanic, architecture, owner-powers disclosure, red-line compliance notes, build/test instructions, phase-2 deployment checklist, submission blurb draft. |

### Compile
```
$ npx hardhat compile
Compiled 5 Solidity files successfully (evm target: paris).
```

### Test results — 22 passing, 0 failing (`npx hardhat test`, ~2 s)
- **Gate:** hasAgentID reflects mock; immutable agentID address exposed; holder mints (events `AgentIDVerified` + `BadgeMinted` verified with args); non-holder reverts `NoAgentID(address)`; holder whose ID is removed can no longer mint.
- **One-per-person:** second mint reverts `AlreadyClaimed`; claim record survives window close/reopen; two different holders can each mint.
- **Window:** starts closed (`MintClosed`); owner opens/closes (event verified); non-owner cannot (`NotOwner`).
- **Supply cap:** dedicated cap=2 instance — third distinct holder reverts `SoldOut`.
- **Owner limits:** owner without an Agent ID cannot mint (`NoAgentID`); owner *with* an Agent ID mints only via public `mint()` and only once; owner cannot raise cap (`InvalidMaxSupply`); owner can lower cap but not below `totalMinted` (lowering to exactly `totalMinted` ⇒ subsequent mints `SoldOut`); non-owner cannot change cap; after `renounceOwnership()` window/cap calls revert forever; plain BNB transfer to the contract reverts and its balance stays 0 (no payable surface).
- **ERC-721 behaviour:** `tokenURI(1)` returns the fixed URI, nonexistent token reverts; badge freely transferable, and transferring away does **not** reset the minter's claim record; name/symbol = "AgentGate Badge"/"AGB".

### Design decisions (and why)
1. **Zero external dependencies** (hand-written ERC-721/Ownable instead of OpenZeppelin): BscScan verification and judge review read exactly the shipped source; smaller audit surface. Cost: more care needed in the ERC-721 — covered by tests.
2. **`setMaxSupply` = lower-only, never below `totalMinted`, raisable never** (the more restrictive of the options offered): nobody, owner included, can dilute badge holders after launch.
3. **Mint window starts CLOSED** and is opened explicitly by the owner after deployment: prevents anyone minting before the metadata/site are ready, and makes "open the drop" a deliberate, visible on-chain act.
4. **Fixed collection-wide `metadataURI`**, set at construction, no setter: matches the "fixed metadata URI" spec and removes a whole class of post-launch metadata-swap concerns.
5. **Claim is recorded before `_safeMint`** (checks-effects-interactions) and the badge has no transfer hooks: no re-entrancy path to a second badge.
6. **Badge is freely transferable** (spec: no transfer blocking). The *claim right* is what is one-per-person; the token itself is a normal ERC-721. Documented in README + a dedicated test.
7. **Check order in `mint()`**: window → claimed → supply → identity (cheap local checks first; no path reaches minting without the identity check).
8. **Web page degrades gracefully** with `CONFIG.BADGE_CONTRACT = ""`: mint section shows "deployment pending", eligibility check still works against the live Agent ID contract.

### Known placeholders / notes
- `metadataURI` used in tests: `ipfs://agentgate-badge-metadata-placeholder/badge.json` — a placeholder; real metadata JSON must be uploaded (IPFS or stable HTTPS) before deployment (phase 2, checklist step 1).
- Web `CONFIG.BADGE_CONTRACT` is intentionally empty until deployment.
- The live Agent ID contract itself was **not** called during phase 1 (local-only scope); the gate logic was verified against `MockAgentID`. A fork test or a read-only mainnet `balanceOf` sanity check can be added in phase 2 before deploying.

### Left for phase 2
- Upload badge metadata; deploy `AgentGateBadge` (Remix or other route — TBD with the user) with `(0x60b9262456de011f7d15a54cdd8c48baaa8b022f, <metadataURI>, 10000)`.
- BscScan source verification.
- Fill `CONFIG.BADGE_CONTRACT` in `web/index.html`; host the page.
- `setMintOpen(true)`; live smoke test (one holder mint + one non-holder rejection).
- Promotion to reach ≥30 distinct Agent ID holder interactions; monitor `BadgeMinted` events.
- Fill website/contract fields into the submission blurb (README bottom) and submit before 2026-12-09 16:00 CST.

## Phase 2 — 2026-11-18 (Stage A prep done; deployment BLOCKED on route — see below)

### baw preflight (2026-11-18 ~19:2x CST)
- `baw skill-check`: skill 1.15.0, no update. `baw cli-check`: CLI 1.12.0, OK.
- `baw wallet status`: **CONNECTED**. Session expires 2026-11-20T02:37Z.
- `baw wallet settings`: Developer Mode **enabled** (expires 2026-11-25T02:37Z), `balanceExceeded=false`.
- BSC BNB balance (fresh): **0.022862588313652199 BNB**.

### A.1 Metadata — self-contained data URI (no external service)
- Artwork drawn in code: `metadata/badge.svg` (899 bytes) — dark ID-card motif, gold shield + check, "AgentGate Badge / AGENT ID VERIFIED", no Binance branding.
- `metadata/metadata.json`: name "AgentGate Badge", image = `data:image/svg+xml;base64,…` (1,226 chars).
- **Final tokenURI** (in `metadata/tokenURI.txt`, 2,277 chars total — target was < 8 KB):
  `data:application/json;base64,eyJuYW1lIjoiQWdlbnRHYXRlIEJhZGdlIiw…` (full string in the file).

### A.2 Deployment route check — **baw CANNOT deploy contracts**
- The baw skill/CLI has no deploy command (command list: auth, wallet, market-order, limit-order, x402-payment, prediction, approvals, defi, signal, tracker, leaderboard, contract-call, sign-message). `contract-call` is documented for calls to an existing contract: `--to` is "required for EVM".
- Empirical check (read-only preview, nothing broadcast): `baw contract-call preview --binanceChainId 56 --from 0xF0C5832df6Ec3C1565842784Ff9229FA4566eEA5 --value 0 --inputData <init code>` (no `--to`) → backend error code 2, `SERVICE_ERROR`: **"to is required for EVM contract-call"**. Passing the zero address as `--to` would be a plain call to 0x0, NOT a creation — it deploys nothing, so that path was not used.
- **Conclusion: deployment must be done by the user in Remix** (fallback steps below). Everything else in phase 2 (Sourcify verify, `setMintOpen`, smoke mint) can still be done by the agent afterwards — `setMintOpen` via baw only if the deployer/owner is the Agentic Wallet (route 1 below).
- Prepared artifacts: `deploy/init-code.txt` (creation bytecode + encoded args, 9,213 bytes), `deploy/constructor-args.txt`.
  - Runtime bytecode 6,781 bytes; constructor args 2,432 bytes (long because of the data-URI metadata).
- Read-only `eth_estimateGas` for the creation from the Agentic Wallet (3 RPCs agree — bsc-dataseed.binance.org, bsc-dataseed1/2.defibit.io):
  - gas estimate **3,080,989**; gas price at the time 0.05 gwei → expected cost ≈ **0.000154 BNB** (BSC gas price floats; even at 1 gwei it is ≈0.0031 BNB — well under the 0.01 BNB guardrail and the wallet's 0.02286 BNB).
  - Agentic Wallet BSC nonce at check time: 233 (0xe9).

### A.3 Verification prep
- `verify/standard-input.json` — the exact Hardhat build-info `input` (compiler **0.8.24+commit.e11b9ed9**, optimizer 200 runs, evmVersion paris; sources include test-only `MockAgentID.sol`, unused by the badge).
- `verify/sourcify-payload-template.json` — ready Sourcify v2 payload (`stdJsonInput` + `compilerVersion` + `contractIdentifier` = `contracts/AgentGateBadge.sol:AgentGateBadge`); only the deployed address is missing. Submit to `POST https://sourcify.dev/server/v2/verify/56/<address>` the moment an address exists.

### A.4 Repo
- `git init` (branch `main`), repo-local identity "Rong Zhang" <348597385+zhangrong121387-hue@users.noreply.github.com>; phase 1 + phase 2 prep committed locally. **Not pushed** (no GitHub credentials available right now).

### ⛔ STOPPED — user action needed: deploy in Remix (pick ONE route)

**Route 1 (preferred — keeps the Agentic Wallet as owner): Remix + WalletConnect to the Binance App wallet (0xF0C5…EA5).**
1. On your phone, open the Binance App (the wallet holding 0xF0C5832df6Ec3C1565842784Ff9229FA4566eEA5, ~0.0229 BNB on BSC — enough).
2. On a computer browser open https://remix.ethereum.org. In the File Explorer create four files with EXACTLY the contents of `contracts/IAgentID.sol`, `contracts/AgentGate.sol`, `contracts/ERC721Minimal.sol`, `contracts/AgentGateBadge.sol` from this repo (the agent can paste/provide them; do NOT include MockAgentID.sol).
3. Solidity Compiler tab: version **0.8.24**, optimizer **200 runs**, EVM version **paris** (Advanced settings), compile `AgentGateBadge.sol`.
4. Deploy & Run tab: Environment → **WalletConnect** → connect the Binance App wallet (pick "My Wallet" 0xF0C5…EA5 if asked). Confirm the account shown is 0xF0C5832df6Ec3C1565842784Ff9229FA4566eEA5 and the network is BSC Mainnet (56).
5. In the Deploy form for `AgentGateBadge`, fill the constructor fields:
   - `agentIDAddress`: `0x60b9262456de011f7d15a54cdd8c48baaa8b022f`
   - `metadataURI_`: the FULL contents of `metadata/tokenURI.txt` (one long `data:application/json;base64,…` string, 2,277 chars — paste it whole).
   - `maxSupply_`: `10000`
6. Click **Deploy** and approve in the Binance App. Expected gas ≈ 3.08M (≈0.0002–0.003 BNB).
7. Send the agent the **contract address** (and deploy tx hash) shown under "Deployed Contracts". The agent then does: Sourcify verification → `setMintOpen(true)` via baw → smoke mint → web CONFIG.

**Route 2 (simpler tooling, different owner): Remix + your self-custody MetaMask ("Account ntf", 0x9aFbdDFF5dFbae8372F7A794afcC2345700240F8).**
- Same steps 2–3 and 5–6, but Environment → **Injected Provider (MetaMask)** on BSC Mainnet.
- ⚠️ That wallet currently holds no BSC BNB (it holds RH-chain ETH) — first top it up with ~0.005 BNB on BSC (e.g. send from the Binance Agentic Wallet to 0x9aFbdDFF5dFbae8372F7A794afcC2345700240F8 on BSC; the agent can prepare that transfer for your approval).
- ⚠️ The badge **owner will be the MetaMask address**, so `setMintOpen(true)` must then be clicked by you in Remix (Deployed Contracts → `setMintOpen` with `true`) or via BscScan Write — the agent cannot do that step via baw. The agent still does verification prep, the smoke mint from the Agentic Wallet, and the web CONFIG.

## Phase 2 — Route A EXECUTED 2026-11-18 (~19:24–19:28 CST) — LIVE ✅

User chose Route A in chat ("你全包，我只确认一笔小额转账"). baw cannot deploy, so deployment was done from a one-time key funded by one 0.005 BNB transfer from the Agentic Wallet. (In the event, the funding preview returned `requireConfirmation=false`, so no in-app approval was needed at all.)

### Gas sanity (before any transfer)
- `eth_gasPrice` on two BSC RPCs: **0.05 gwei** (50,000,000 wei) on both.
- Worst case (deploy 3,080,989 + transferOwnership ~50k + sweep 21k) × 0.05 gwei ≈ **0.000158 BNB** → 0.005 BNB covers it ~31× (≥2× headroom ✓).

### One-time deployer
- Deployer address: **`0xD96F212971D4E985991bbafedB2DDe8766995F79`** (key generated locally with ethers, stored only in `deploy/deployer-key.txt` chmod 0600, **shredded after the sweep** — see below).
- Init code re-verified byte-identical against the artifacts + constructor args (agentID `0x60b9262456de011f7d15a54cdd8c48baaa8b022f`, tokenURI from `metadata/tokenURI.txt`, maxSupply 10000) before use.

### Transaction ledger (BSC, chain 56)
| # | Action | From → To | Tx hash | Gas used | Cost |
|---|---|---|---|---|---|
| 1 | Fund deployer 0.005 BNB (baw contract-call, preview clean, no risks, `requireConfirmation=false`) | Agentic Wallet → deployer | `0x4316f11cf40cf3ba7ca4fb2302a09d5f3dc831d218afd6692e9591dbc308ecaa` | 21,000 | ~0.00000105 BNB |
| 2 | **Deploy AgentGateBadge** | deployer → CREATE | `0x5ffc8aaf8ac990b846affe65aa91b383000913597e3c6a2a236c638b35fd91bd` | 3,055,825 @ 0.05 gwei | 0.00015279125 BNB |
| 3 | `transferOwnership(user)` | deployer | `0x0a7ae1606c5a39814dec1ed1649e0500d3fa492edd609eea6e20c5f372a84ec8` | 28,720 @ 0.05 gwei | 0.000001436 BNB |
| 4 | Sweep remainder back | deployer → Agentic Wallet | `0xdf4d21de27060d00089fb20eff923c6a13ccd73399a8cd454eec5913449fc30f` | 21,000 @ 0.05 gwei | 0.00000105 BNB (swept **0.00484472275 BNB**) |
| 5 | `setMintOpen(true)` (baw, preview clean) | Agentic Wallet (owner) | `0x3de0eed4634fef0bbbd815ddb0f0f6dd5e31fd4a1e1b6ffd80b148c5dd022b72` | 46,930 @ ~0.076 gwei | ≈0.0000035752 BNB |
| 6 | Smoke `mint()` (baw, preview clean) | Agentic Wallet | `0x9ce8181e3005f72fac7cf0cf5838662891840e5417083581bb6dd09004698f82` | 108,440 @ ~0.089 gwei | ≈0.0000096491 BNB |

- **Contract address: `0x42c9ED912025DF33cA1676AAD4651cDdeD3F09ED`** — `eth_getCode` non-empty on two RPCs; constructor state verified: `agentID()` = real Agent ID contract, `maxSupply()` = 10000, name/symbol = AgentGate Badge / AGB, `tokenURI(1)` = the 2,277-char data URI.
- **Owner handover verified on two RPCs**: `owner()` = `0xF0C5832df6Ec3C1565842784Ff9229FA4566eEA5` (the Agentic Wallet). Deployer balance after sweep = **0 wei** on two RPCs; **deployer key destroyed** (`shred -u deploy/deployer-key.txt`).
- **All-in cost to the user wallet ≈ 0.000170 BNB** (balance 0.02286258831 → 0.02269249581 BNB).
- **Sourcify v2 (chain 56): `exact_match`** — creationMatch AND runtimeMatch exact (verifiedAt 2026-11-18T11:26:08Z). BscScan's own verification was NOT separately submitted/checked — do not claim it.
- `mintOpen()` = **true** on two RPCs.

### Smoke test results
- User wallet: `balanceOf` = **1**, `hasClaimed` = true, **`ownerOf(2)` = user wallet** (see note below), `tokenURI` correct.
- Read-only `eth_call` of `mint()` from a non-holder (`0x…dEaD`) reverts with **`NoAgentID(address)`** (selector `0xff592cec`, argument = caller) ✓.
- ⚠️ **Note — token #1 is NOT the user's.** Nine seconds after `setMintOpen(true)` landed (block 134303153, 2026-11-18T11:26:33Z), an external Agent ID holder `0x62F9387B73f7CFDd0BB96C8A3451D07412481175` (Agent ID `balanceOf` = 1, verified) called the public `mint()` (tx `0x93d2959ea1f9c5025aa945a95a25367e720a2707bc538247a361860649ecd58f`) and took token #1 — a legitimate gated mint, so `totalMinted` = **2** and the user's smoke mint is token #2. Net effect: the badge already has its first organic Agent ID interaction.

### Web
- `web/index.html` `CONFIG.BADGE_CONTRACT` filled with the deployed address. Page hosting (GitHub Pages) still pending a user-provided repo-scoped PAT.

### After deployment (agent, once an address exists)
- Sourcify v2 verify (payload ready) → record match level; BscScan's own verify page may still need a manual submission (files ready in `verify/`).
- Route 1 only: `setMintOpen(true)` via baw preview→execute; read back `mintOpen() == true`.
- Smoke test: one free `mint()` from the Agentic Wallet via baw; verify `balanceOf(user) == 1`, `totalMinted == 1`; read-only `eth_call` of `mint()` from a random non-holder must revert `NoAgentID`.
- Fill `web/index.html` CONFIG with the deployed address; commit.
