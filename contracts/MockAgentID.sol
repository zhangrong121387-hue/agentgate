// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IAgentID} from "./IAgentID.sol";

/// @title MockAgentID — test-only stand-in for the SPACE ID Agent ID contract
/// @notice Reproduces the one behaviour AgentGate depends on — `balanceOf`
///         returning 1 for registered holders, 0 for everyone else — so the
///         test suite can run entirely on a local chain. NOT for deployment:
///         unlike the real Agent ID, registration here is permissionless.
/// @dev Lives in contracts/ only so Hardhat compiles it with everything
///      else; it is never part of the production deployment.
contract MockAgentID is IAgentID {
    mapping(address => bool) private _holders;

    /// @notice Test helper: mark `account` as an Agent ID holder.
    function register(address account) external {
        _holders[account] = true;
    }

    /// @notice Test helper: remove holder status from `account`.
    function unregister(address account) external {
        _holders[account] = false;
    }

    function balanceOf(address account) external view override returns (uint256) {
        return _holders[account] ? 1 : 0;
    }
}
