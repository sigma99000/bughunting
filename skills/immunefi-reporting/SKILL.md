---
name: immunefi-reporting
description: Immunefi report template — Web3-specific evidence (Foundry PoC, mainnet fork), economic-loss demonstration.
keywords: [immunefi, web3, defi, smart contract, foundry, hardhat, mainnet fork, economic loss]
---

# immunefi-reporting

## When this skill loads

`/report platform=immunefi`.

## Mandatory artifacts

Immunefi reports **require** a runnable PoC. The skill refuses to
render unless:

1. A Foundry or Hardhat test exists in the engagement folder
   (`engagements/<proj>/poc/`) that reproduces the bug.
2. The test runs against a mainnet fork pinned to a specific block.
3. The test asserts the economic loss with a concrete dollar value.

## Severity taxonomy

```
Critical       — direct theft of funds (>= $X tier)
High           — temporary freeze of funds, governance takeover
Medium         — griefing with quantifiable cost
Low            — design issues, no immediate impact
None           — informational
```

Each protocol on Immunefi publishes its own bounty caps per severity.

## Template

```markdown
## Summary

A reentrancy vulnerability in `Vault.withdraw()` allows an attacker
to drain the contract by re-entering during the `call` to the user's
fallback. Maximum economic loss: $4.2M (the current `totalAssets()`).

## Vulnerability Details

Contract: `0xVault...` (Etherscan link)
Function: `Vault.withdraw(uint256 amount)` (line 142)
Compiler: solc 0.8.19
Network: Ethereum mainnet, block 18000000

## Impact

Loss of all assets currently in the vault (~$4.2M at block
18000000 pricing). Attacker requires only a single transaction
and any wallet with sufficient gas to deploy the attack contract.

## Proof of Concept

Foundry test in `poc/test/Exploit.t.sol`:

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;
import "forge-std/Test.sol";
import "../src/Vault.sol";

contract ExploitTest is Test {
    Vault vault = Vault(0x...);
    function setUp() public { vm.createSelectFork("mainnet", 18000000); }
    function testReentrancyDrain() public { /* ... */ }
}
```

Run:
```
forge test --fork-url $MAINNET_RPC --match-test testReentrancyDrain -vvvv
```

Expected: `Drained: 4187531.94 USDC`.

## Recommendation

Add `nonReentrant` modifier; apply CEI (Checks-Effects-Interactions).
Inherit `ReentrancyGuard` from OpenZeppelin v5.

## References

- OpenZeppelin ReentrancyGuard docs
- SWC-107 (Reentrancy)
```

## Discipline

- Never submit a "theoretical" exploit. Immunefi's PoC requirement
  is strict.
- Never submit a known-resolved issue (check the project's prior
  Immunefi disclosures).
- Don't include private keys; use Foundry's `vm.startPrank`.
- Mainnet-fork tests must pin block — un-pinned tests fail
  reproducibility.

## See also

- `web3-audit`
- `triage-validation`
