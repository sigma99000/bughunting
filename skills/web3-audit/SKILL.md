---
name: web3-audit
description: Solidity / EVM smart-contract audit knowledge — known patterns, OpenZeppelin diff, oracle / flash-loan / governance pitfalls.
keywords: [web3, solidity, evm, smart contract, defi, openzeppelin, reentrancy, oracle, flash loan, governance]
---

# web3-audit

## When this skill loads

`/web3-audit`, or any chat mentioning Solidity / Foundry / Hardhat.

## Quick reference — known-pattern checklist

| Pattern | Check |
|---|---|
| Reentrancy | External call before state change; missing `nonReentrant` |
| Integer over/underflow | Solidity < 0.8 without SafeMath; `unchecked {}` blocks |
| `tx.origin` for auth | Phishable; should be `msg.sender` |
| Single-source oracle | Spot price use for borrow/withdraw limit |
| Flash-loanable governance | Voting power based on `balanceOf` instead of snapshot |
| Signature malleability | `ecrecover` accepts both `s` values without check |
| Delegatecall to user input | Full control of contract context |
| Uninitialized proxy | `initialize()` callable by anyone |
| Front-runnable `approve` | Old `approve(spender, X)` → `approve(spender, 0)` → `approve(spender, Y)` pattern |
| Permit replay | Missing `chainId` in EIP-712 domain → cross-chain replay |
| Storage collision | Upgradeable proxy layout vs impl |
| Self-destruct / `SELFDESTRUCT` reliance | EIP-6049 deprecation (Cancun) |
| `block.timestamp` for randomness | Miner-manipulable |
| `block.number` for time | Variable block time |
| Hardcoded gas (`call{gas: 2300}`) | Post-Berlin opcode cost changes |
| Slippage protection missing | DEX interactions without `amountOutMin` |
| Token decimals assumption (18) | USDC/USDT are 6 |
| Rebase / fee-on-transfer tokens unsupported | `transfer` returns wrong amount |
| `_safeMint` reentrancy via `onERC721Received` | ERC-721 callback abuse |
| Off-by-one in fee math | `* 100` vs `* 10000` confusion |

## Tooling

```bash
# Slither — static analyzer
pip install slither-analyzer
slither .

# Mythril — symbolic execution
pip install mythril
myth analyze contract.sol

# Echidna — fuzzer
docker pull trailofbits/echidna
echidna-test contract.sol --config echidna.yaml

# Foundry — testing + fork
curl -L https://foundry.paradigm.xyz | bash
forge test --fork-url $MAINNET_RPC
```

## Diff against OpenZeppelin

```bash
git clone https://github.com/OpenZeppelin/openzeppelin-contracts
diff -r ./contracts/token/ERC20 openzeppelin-contracts/contracts/token/ERC20
```

Any deviation in storage layout / overflow checks / access control is
suspicious.

## Famous DeFi exploits (study material)

| Year | Project | Class | Loss |
|---|---|---|---|
| 2020 | bZx | Oracle manipulation | $8M |
| 2021 | Cream | Flash-loan + collateral mispricing | $130M |
| 2021 | Poly | Cross-chain bridge — `keeper` not verified | $611M |
| 2022 | Wormhole | Signature verification bypass | $325M |
| 2022 | Ronin Bridge | Compromised validator keys (not contract) | $625M |
| 2022 | Beanstalk | Governance flash-loan | $182M |
| 2023 | Euler | Donate-then-liquidate self | $200M |
| 2023 | Curve | Vyper compiler reentrancy guard bug | $73M |
| 2024 | Munchables | Insider — uninitialized upgrade | $62M |

## Discipline

- Findings without runnable Foundry tests will be rejected by
  Immunefi.
- "Could be exploited" → not a bug. Prove it.
- Mainnet fork tests need pinned block.

## See also

- `immunefi-reporting`
- `triage-validation`
