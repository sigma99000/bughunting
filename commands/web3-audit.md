---
name: web3-audit
description: Solidity / EVM contract audit — invariant checks, OpenZeppelin diff, known-pattern issues.
---

# /web3-audit

**Args:** `target=<contract-address|local-path> [chain=eth|bsc|polygon|arbitrum]`

## What this command does

Loads `web3-audit`. Performs:

1. If contract address, fetches verified source from the explorer
   (Etherscan / equivalent).
2. Diffs against known OpenZeppelin base contracts to surface
   modified inheritance.
3. Walks the known-pattern checklist:
   - Reentrancy (CEI violations, missing `nonReentrant`)
   - Integer over/underflow (Solidity < 0.8 without SafeMath)
   - Access control (missing `onlyOwner`, `tx.origin` checks)
   - Oracle manipulation (single-source price feeds, spot price use)
   - Flash-loan attackability of governance / AMM logic
   - Signature malleability (ecrecover without `s` range check)
   - Delegatecall to user-controlled address
   - Uninitialized proxy storage
   - Front-runnable approve/transferFrom
   - Permit replay across chains (missing chainId)
4. Optionally runs `slither` and `mythril` if installed.

## Output contract

```
Contract: 0xABC...123 (Vault.sol, 412 LOC)
Compiler: solc 0.8.19
Inheritance: ERC4626 + Ownable (OZ 4.8 — clean diff)

Findings:
  H-01: oracle.latestAnswer() used without staleness check  (line 142)
  M-02: deposit() not guarded against share-price manipulation via direct ERC20 transfer
  L-03: emit Withdraw() before _burn() — observability impact only

Next: /chain finding=h-01 (combine with flash-loan oracle attack)
```

## Discipline

- Immunefi-bound findings require a **runnable PoC** (Foundry/Hardhat
  test). `/report platform=immunefi` will refuse to render without
  one.
- Mainnet-fork PoCs use a pinned block to make results reproducible.
- Never submit "could be vulnerable in future" — Immunefi rejects
  speculation.
