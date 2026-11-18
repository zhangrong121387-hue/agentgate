// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IAgentID — minimal interface for the SPACE ID Agent ID contract
/// @notice The Agent ID contract lives on BNB Smart Chain (chain id 56) at
///         0x60b9262456de011f7d15a54cdd8c48baaa8b022f. It is an ERC-721
///         ("SPACE ID Agent ID", symbol "AI") whose tokens are
///         non-transferable identity credentials: one verified (KYC) person
///         can hold exactly one Agent ID, shaped like `name.ai`.
///
///         AgentGate only ever needs one question answered — "does this
///         address hold an Agent ID?" — so this interface intentionally
///         exposes nothing but `balanceOf`. Keeping the surface this small
///         means any contract that integrates AgentGate takes on no extra
///         trust assumptions about the identity contract.
interface IAgentID {
    /// @notice Number of Agent ID tokens held by `account`.
    /// @dev Because an Agent ID is one-per-person and non-transferable,
    ///      `balanceOf(account) > 0` is a reliable "is a verified unique
    ///      human agent" check — the entire foundation of AgentGate.
    /// @param account The address to check.
    /// @return The number of Agent IDs held (0 or 1 in practice).
    function balanceOf(address account) external view returns (uint256);
}
