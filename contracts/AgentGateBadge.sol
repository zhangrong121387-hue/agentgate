// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AgentGate} from "./AgentGate.sol";
import {ERC721Minimal, OwnableMinimal} from "./ERC721Minimal.sol";

/// @title AgentGateBadge — free commemorative badge, mintable only by Agent ID holders
/// @notice The reference product built on AgentGate. `mint()` is FREE (the
///         contract holds no funds and has no payable functions at all) and
///         is gated by the caller's Agent ID: because an Agent ID is
///         one-per-verified-person and non-transferable, "one badge per
///         address, ever" is in practice "one badge per human, ever" —
///         minting a second badge from a fresh wallet does not work,
///         because the fresh wallet holds no Agent ID.
///
/// @dev Owner powers — the COMPLETE list (also disclosed in README.md):
///        1. `setMintOpen(bool)` — open or close the mint window.
///        2. `setMaxSupply(uint256)` — LOWER the supply cap only. The cap
///           can never be raised, and never set below the amount already
///           minted. (Restrictive by design: nobody — not even the owner —
///           can dilute the badge after the fact.)
///        3. `transferOwnership` / `renounceOwnership` — hand over or give
///           up the two powers above. Renouncing freezes the window and
///           cap forever.
///      The owner CANNOT: mint (the owner must pass the same Agent ID gate
///      as everyone else, via the public `mint()`), block or reverse
///      transfers, charge fees, pause anything else, or withdraw funds
///      (the contract cannot receive funds in the first place).
contract AgentGateBadge is AgentGate, ERC721Minimal, OwnableMinimal {
    /// @notice The one metadata document describing every badge in this
    ///         collection. Fixed at construction; there is no setter.
    string public metadataURI;

    /// @notice Hard cap on badges that can ever exist. Can only go down
    ///         (see `setMaxSupply`), never up.
    uint256 public maxSupply;

    /// @notice How many badges have been minted so far. Token ids run
    ///         1..totalMinted.
    uint256 public totalMinted;

    /// @notice Whether the mint window is currently open. Starts CLOSED;
    ///         the owner opens it explicitly after deployment.
    bool public mintOpen;

    /// @notice Per-address claim record: true once an address has minted.
    ///         Together with the Agent ID gate this enforces one badge per
    ///         person, permanently — the mapping is never reset.
    mapping(address => bool) public claimed;

    event BadgeMinted(address indexed holder, uint256 indexed tokenId);
    event MintWindowChanged(bool open);
    event MaxSupplyChanged(uint256 oldMaxSupply, uint256 newMaxSupply);

    error MintClosed();
    error AlreadyClaimed(address account);
    error SoldOut();
    error InvalidMaxSupply(uint256 newMaxSupply);

    /// @param agentIDAddress The Agent ID contract (BSC mainnet:
    ///        0x60b9262456de011f7d15a54cdd8c48baaa8b022f).
    /// @param metadataURI_ Fixed metadata URI returned by `tokenURI` for
    ///        every badge (an IPFS or HTTPS JSON document).
    /// @param maxSupply_ Initial supply cap. 10,000 for the live deployment.
    constructor(
        address agentIDAddress,
        string memory metadataURI_,
        uint256 maxSupply_
    ) AgentGate(agentIDAddress) ERC721Minimal("AgentGate Badge", "AGB") {
        require(maxSupply_ > 0, "Badge: zero supply");
        metadataURI = metadataURI_;
        maxSupply = maxSupply_;
        mintOpen = false;
    }

    /// @notice Mint your badge. Free. One per Agent ID holder, ever.
    /// @dev Check order is deliberate: window → claim record → supply →
    ///      identity. The identity check (`_requireAgentID`) is last so
    ///      the cheap local reverts fire first, but no path reaches the
    ///      mint without passing it.
    function mint() external {
        if (!mintOpen) revert MintClosed();
        if (claimed[msg.sender]) revert AlreadyClaimed(msg.sender);
        if (totalMinted >= maxSupply) revert SoldOut();

        // The centerpiece: only an Agent ID holder gets through this line.
        _requireAgentID();

        claimed[msg.sender] = true;
        uint256 tokenId = ++totalMinted;
        emit AgentIDVerified(msg.sender);
        emit BadgeMinted(msg.sender, tokenId);
        _safeMint(msg.sender, tokenId);
    }

    /// @notice Has `account` already claimed its badge?
    function hasClaimed(address account) external view returns (bool) {
        return claimed[account];
    }

    /// @notice The fixed collection metadata URI (identical for every
    ///         token; reverts for tokens that do not exist).
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(tokenId >= 1 && tokenId <= totalMinted, "Badge: nonexistent token");
        return metadataURI;
    }

    // ------------------------------------------------------------------
    // Owner powers — the complete list (see the contract header).
    // ------------------------------------------------------------------

    /// @notice Open or close the mint window. Owner power #1 of 3.
    function setMintOpen(bool open_) external onlyOwner {
        mintOpen = open_;
        emit MintWindowChanged(open_);
    }

    /// @notice Lower the supply cap. Owner power #2 of 3.
    /// @dev Can NEVER raise the cap, and can never set it below the number
    ///      already minted. Lowering it to exactly `totalMinted` closes
    ///      the drop by supply.
    function setMaxSupply(uint256 newMaxSupply) external onlyOwner {
        if (newMaxSupply > maxSupply || newMaxSupply < totalMinted) {
            revert InvalidMaxSupply(newMaxSupply);
        }
        emit MaxSupplyChanged(maxSupply, newMaxSupply);
        maxSupply = newMaxSupply;
    }

    // Owner power #3 of 3 — transferOwnership / renounceOwnership —
    // is inherited from OwnableMinimal, unmodified.

    // Deliberately absent: no payable functions, no receive/fallback (plain
    // BNB transfers to this contract revert), no withdraw, no owner mint,
    // no transfer restrictions, no fee switches. The badge promises
    // nothing of value — it is a commemorative proof that the holder's
    // Agent ID passed the gate.
}
