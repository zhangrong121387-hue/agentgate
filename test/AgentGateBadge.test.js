const { expect } = require("chai");
const { ethers } = require("hardhat");

const METADATA_URI = "ipfs://agentgate-badge-metadata-placeholder/badge.json";

describe("AgentGateBadge", function () {
  let mockAgentID, badge;
  let owner, holder, holder2, stranger, ownerNoID;

  beforeEach(async function () {
    [owner, holder, holder2, stranger] = await ethers.getSigners();

    const MockAgentID = await ethers.getContractFactory("MockAgentID");
    mockAgentID = await MockAgentID.deploy();

    const Badge = await ethers.getContractFactory("AgentGateBadge");
    badge = await Badge.deploy(await mockAgentID.getAddress(), METADATA_URI, 10000);

    // holder and holder2 hold an Agent ID; owner and stranger do not.
    await mockAgentID.register(holder.address);
    await mockAgentID.register(holder2.address);
  });

  describe("Agent ID gate (AgentGate base)", function () {
    it("hasAgentID reflects the identity contract", async function () {
      expect(await badge.hasAgentID(holder.address)).to.equal(true);
      expect(await badge.hasAgentID(stranger.address)).to.equal(false);
    });

    it("exposes the immutable Agent ID address", async function () {
      expect(await badge.agentID()).to.equal(await mockAgentID.getAddress());
    });

    it("holder can mint once the window is open", async function () {
      await badge.setMintOpen(true);
      await expect(badge.connect(holder).mint())
        .to.emit(badge, "AgentIDVerified")
        .withArgs(holder.address)
        .and.to.emit(badge, "BadgeMinted")
        .withArgs(holder.address, 1);
      expect(await badge.ownerOf(1)).to.equal(holder.address);
      expect(await badge.balanceOf(holder.address)).to.equal(1n);
      expect(await badge.hasClaimed(holder.address)).to.equal(true);
      expect(await badge.totalMinted()).to.equal(1n);
    });

    it("non-holder mint reverts with NoAgentID", async function () {
      await badge.setMintOpen(true);
      await expect(badge.connect(stranger).mint())
        .to.be.revertedWithCustomError(badge, "NoAgentID")
        .withArgs(stranger.address);
      expect(await badge.totalMinted()).to.equal(0n);
    });

    it("an address that loses its Agent ID can no longer mint", async function () {
      await badge.setMintOpen(true);
      await mockAgentID.unregister(holder.address);
      await expect(badge.connect(holder).mint()).to.be.revertedWithCustomError(
        badge,
        "NoAgentID"
      );
    });
  });

  describe("one badge per Agent ID holder, ever", function () {
    beforeEach(async function () {
      await badge.setMintOpen(true);
    });

    it("second mint by the same address reverts", async function () {
      await badge.connect(holder).mint();
      await expect(badge.connect(holder).mint())
        .to.be.revertedWithCustomError(badge, "AlreadyClaimed")
        .withArgs(holder.address);
      expect(await badge.totalMinted()).to.equal(1n);
    });

    it("claim record survives closing and reopening the window", async function () {
      await badge.connect(holder).mint();
      await badge.setMintOpen(false);
      await badge.setMintOpen(true);
      await expect(badge.connect(holder).mint()).to.be.revertedWithCustomError(
        badge,
        "AlreadyClaimed"
      );
    });

    it("different holders can each mint", async function () {
      await badge.connect(holder).mint();
      await badge.connect(holder2).mint();
      expect(await badge.totalMinted()).to.equal(2n);
      expect(await badge.ownerOf(2)).to.equal(holder2.address);
    });
  });

  describe("mint window", function () {
    it("starts closed: mint reverts before the owner opens it", async function () {
      expect(await badge.mintOpen()).to.equal(false);
      await expect(badge.connect(holder).mint()).to.be.revertedWithCustomError(
        badge,
        "MintClosed"
      );
    });

    it("owner can open and close; closing blocks minting again", async function () {
      await expect(badge.setMintOpen(true))
        .to.emit(badge, "MintWindowChanged")
        .withArgs(true);
      await badge.connect(holder).mint();
      await badge.setMintOpen(false);
      await expect(badge.connect(holder2).mint()).to.be.revertedWithCustomError(
        badge,
        "MintClosed"
      );
    });

    it("non-owner cannot touch the window", async function () {
      await expect(badge.connect(holder).setMintOpen(true))
        .to.be.revertedWithCustomError(badge, "NotOwner")
        .withArgs(holder.address);
    });
  });

  describe("supply cap", function () {
    it("cap is enforced: mint reverts with SoldOut once reached", async function () {
      const Badge = await ethers.getContractFactory("AgentGateBadge");
      const tiny = await Badge.deploy(
        await mockAgentID.getAddress(),
        METADATA_URI,
        2
      );
      await tiny.setMintOpen(true);
      const [, , , , fifth] = await ethers.getSigners();
      await mockAgentID.register(fifth.address);
      await tiny.connect(holder).mint();
      await tiny.connect(holder2).mint();
      await expect(tiny.connect(fifth).mint()).to.be.revertedWithCustomError(
        tiny,
        "SoldOut"
      );
      expect(await tiny.totalMinted()).to.equal(2n);
    });
  });

  describe("owner power limits", function () {
    beforeEach(async function () {
      await badge.setMintOpen(true);
    });

    it("owner cannot mint for themselves without an Agent ID", async function () {
      // The owner holds no Agent ID in this fixture: the gate applies to
      // the owner exactly like anyone else — there is no owner mint path.
      await expect(badge.connect(owner).mint())
        .to.be.revertedWithCustomError(badge, "NoAgentID")
        .withArgs(owner.address);
    });

    it("owner WITH an Agent ID mints only via the public mint, one badge", async function () {
      await mockAgentID.register(owner.address);
      await badge.connect(owner).mint();
      expect(await badge.ownerOf(1)).to.equal(owner.address);
      await expect(badge.connect(owner).mint()).to.be.revertedWithCustomError(
        badge,
        "AlreadyClaimed"
      );
    });

    it("owner cannot raise the supply cap", async function () {
      await expect(badge.setMaxSupply(10001))
        .to.be.revertedWithCustomError(badge, "InvalidMaxSupply")
        .withArgs(10001);
      await expect(badge.setMaxSupply(20000)).to.be.revertedWithCustomError(
        badge,
        "InvalidMaxSupply"
      );
    });

    it("owner can lower the cap, but not below the amount already minted", async function () {
      await badge.connect(holder).mint();
      await badge.connect(holder2).mint(); // totalMinted = 2
      await expect(badge.setMaxSupply(1))
        .to.be.revertedWithCustomError(badge, "InvalidMaxSupply")
        .withArgs(1);
      await expect(badge.setMaxSupply(2))
        .to.emit(badge, "MaxSupplyChanged")
        .withArgs(10000, 2);
      expect(await badge.maxSupply()).to.equal(2n);
      // Cap now equals minted supply: further mints are SoldOut.
      const [, , , , fifth] = await ethers.getSigners();
      await mockAgentID.register(fifth.address);
      await expect(badge.connect(fifth).mint()).to.be.revertedWithCustomError(
        badge,
        "SoldOut"
      );
    });

    it("non-owner cannot change the supply cap", async function () {
      await expect(badge.connect(holder).setMaxSupply(5))
        .to.be.revertedWithCustomError(badge, "NotOwner")
        .withArgs(holder.address);
    });

    it("renouncing ownership freezes window and cap forever", async function () {
      await badge.renounceOwnership();
      expect(await badge.owner()).to.equal(ethers.ZeroAddress);
      await expect(badge.setMintOpen(false)).to.be.revertedWithCustomError(
        badge,
        "NotOwner"
      );
      await expect(badge.setMaxSupply(5)).to.be.revertedWithCustomError(
        badge,
        "NotOwner"
      );
    });

    it("contract holds no funds: plain BNB transfer reverts", async function () {
      await expect(
        owner.sendTransaction({ to: await badge.getAddress(), value: 1n })
      ).to.be.reverted;
      expect(
        await ethers.provider.getBalance(await badge.getAddress())
      ).to.equal(0n);
    });
  });

  describe("badge behaviour (ERC-721)", function () {
    beforeEach(async function () {
      await badge.setMintOpen(true);
      await badge.connect(holder).mint();
    });

    it("tokenURI returns the fixed metadata URI", async function () {
      expect(await badge.tokenURI(1)).to.equal(METADATA_URI);
      await expect(badge.tokenURI(99)).to.be.reverted;
    });

    it("badges are freely transferable (no transfer blocking)", async function () {
      await badge.connect(holder).transferFrom(holder.address, stranger.address, 1);
      expect(await badge.ownerOf(1)).to.equal(stranger.address);
      // Claim record stays with the original minter: transferring the badge
      // away does not free up a second mint.
      await expect(badge.connect(holder).mint()).to.be.revertedWithCustomError(
        badge,
        "AlreadyClaimed"
      );
    });

    it("name and symbol are as specified", async function () {
      expect(await badge.name()).to.equal("AgentGate Badge");
      expect(await badge.symbol()).to.equal("AGB");
    });
  });
});
