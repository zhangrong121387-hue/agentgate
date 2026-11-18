// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IAgentID} from "./IAgentID.sol";

/// @title AgentGate — reusable Agent ID gate for BNB Smart Chain projects
/// @notice Inherit from this contract to restrict any function to holders of
///         a SPACE ID Agent ID (0x60b9262456de011f7d15a54cdd8c48baaa8b022f on
///         BSC). An Agent ID is a non-transferable, one-per-verified-person
///         ERC-721 identity (`name.ai`), so gating on it gives a project
///         Sybil resistance that a plain address allowlist cannot: one human
///         can pass the gate exactly once, no matter how many wallets they
///         create.
///
/// @dev Integration is deliberately boring:
///
///      ```solidity
///      contract MyDrop is AgentGate {
///          constructor() AgentGate(0x60b9262456de011f7d15a54cdd8c48baaa8b022f) {}
///
///          function mint() external {
///              _requireAgentID();          // reverts unless caller holds an Agent ID
///              // ... your logic ...
///          }
///      }
///      ```
///
///      Design notes:
///      - The Agent ID contract address is `immutable`: it is fixed at
///        deployment, can never be swapped for a weaker identity contract,
///        and costs no storage read on the hot path.
///      - The gate is a *check*, not a registry: AgentGate stores nothing
///        about holders. Per-person claim tracking (one mint per ID, ever)
///        is the inheriting contract's job — see AgentGateBadge for the
///        reference implementation.
///      - The gate fails closed: if the identity contract call reverts or
///        returns 0, access is denied.
abstract contract AgentGate {
    /// @notice The Agent ID (SPACE ID) contract this gate checks against.
    /// @dev Immutable by design — see the contract-level notes above.
    IAgentID public immutable agentID;

    /// @notice Emitted never by the base contract itself; declared here so
    ///         integrators share one canonical event shape when they record
    ///         a gate pass. See AgentGateBadge for usage.
    event AgentIDVerified(address indexed holder);

    /// @notice The caller (or checked address) does not hold an Agent ID.
    error NoAgentID(address account);

    /// @param agentIDAddress Address of the Agent ID contract on this chain.
    ///        On BSC mainnet: 0x60b9262456de011f7d15a54cdd8c48baaa8b022f.
    constructor(address agentIDAddress) {
        require(agentIDAddress != address(0), "AgentGate: zero address");
        agentID = IAgentID(agentIDAddress);
    }

    /// @notice Does `account` hold an Agent ID?
    /// @param account The address to check.
    /// @return True if the address holds at least one Agent ID.
    function hasAgentID(address account) public view returns (bool) {
        return agentID.balanceOf(account) > 0;
    }

    /// @notice Revert unless `msg.sender` holds an Agent ID.
    /// @dev The one line an integrator needs. Fails closed with a typed
    ///      error carrying the offending address for easy debugging.
    function _requireAgentID() internal view {
        if (!hasAgentID(msg.sender)) {
            revert NoAgentID(msg.sender);
        }
    }

    /// @notice Revert unless `account` holds an Agent ID.
    /// @param account The address to check (e.g. a recipient distinct from
    ///        the caller).
    function _requireAgentIDOf(address account) internal view {
        if (!hasAgentID(account)) {
            revert NoAgentID(account);
        }
    }
}
