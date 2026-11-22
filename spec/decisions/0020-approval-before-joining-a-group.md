# 0020. Approval before a device joins a group, and recovery by removal and re-adding

**Status:** Proposed

## Context

[Decision 0016](0016-user-identity-and-linked-devices.md) gives each device a trust state for every device of a contact: approved, held, or distrusted. A held or distrusted device receives nothing. In groups this held only in part. DCGKA gives every member device a copy of every member's ratchet (DCGKA paper, section 4), so a device that one member has not approved still reads that member's group messages if another member added it. [Decision 0019](0019-two-party-component-for-dcgka.md), point 7, left open whether a member sends its seed secrets to such a device.

The team requires that a device that is not approved sees nothing at all, in groups as in direct messages.

Decision 0019 also records that a two-party message that cannot be read breaks the state between two devices in a group, and that DCGKA has no step to restart it.

[Decision 0006](0006-dcgka-for-groups.md) allows a change to DCGKA only by a new decision record. This is that record. It uses DCGKA's own add and remove operations, and adds one condition under which an add takes effect.

## Decision

1. **Approval of a device for a group.** An *approval* is a group control message. It names the group and the approved device's identity KEM public key and signature public keys. Like every control message, it is signed under the sender's identity key (decision 0006). A device sends an approval only for a device whose trust state it holds as approved:
   - The user's own devices are approved through the device list that the user key signs (decision 0016, point 5). A device approves them without asking its user.
   - A contact's device is approved as decision 0016, point 10, describes.
   - A device of a group member who is not a contact starts as held. The user sees the device, its user identifier and its fingerprint, and approves or distrusts it, as for a contact's device. These trust states are local, like those of decision 0016.
2. **Proposal.** To add a device to a group, a member device sends a *proposal*: a control message that names the device and carries its user's current device list (decision 0016, point 4) and the device's signed prekey (decision 0019, point 5). Every member device checks the list and sends an approval when its user approves. A device that holds or distrusts the proposed device sends nothing.
3. **The add takes effect only with every approval.**
   - A member device sends DCGKA's add for a device only when its causal history holds an approval of that device, for that group, from every member device. The members are those that the add's causal predecessors determine, as DCGKA computes membership.
   - Every member device checks the same condition when it processes the add. If it fails, the add is invalid: no member applies it, and no member sends the device anything. The condition depends only on the add's causal predecessors, so every member reaches the same result.
   - An approval stays valid for that device in that group until the approving device distrusts the device, or leaves the group.
   - Adding a user means proposing each of their devices. Each device joins on its own approvals. A user's new device joins a group in the same way (decision 0016, point 12): the user's other devices approve it at once, and every other member device must approve it as well.
   - How a member treats a later message that names an invalid add among its causal predecessors is **[open]**. An honest member never sends an invalid add.
4. **Distrust removes the device for everyone.** When a member device distrusts a device that is a member of a group, it removes that device with DCGKA's remove. The device can join again only under point 3, and the distrusting device does not approve it again, because distrust is bound to the device's keys (decision 0016, point 10). DCGKA already lets any member remove any member. Which members may remove whom is left to the permission rules of [open question 16](../v0.1/open-questions.md#16-community-moderation-without-an-operator).
5. **Recovery of a broken pair: removal and re-adding.**
   - When a member device B cannot read a two-party message from member device A in a group (decision 0019, Consequences), B sends a *repair request*: a control message that names A and the message.
   - B is then removed from the group and added again. One of the other devices of B's user that is a member of the group does this. If there is none, A does it.
   - The new add needs no action from users. The approvals of B in that group still hold (point 3).
   - B then starts new two-party states with every member, as any added device does.
   - How members merge two repairs of the same device made at the same time is **[open]**.
6. **DCGKA is otherwise unchanged.** Seed secrets go to every member device, as the paper specifies. Every member device has been approved by every other member device, so no member device is held or distrusted by another. This settles decision 0019, point 7.

## Consequences

- **A device that is not approved receives nothing,** with one exception. Two devices added at the same time have not approved each other. In DCGKA, each sends the other its ratchet state with its acknowledgment of the other's add (DCGKA paper, section 6, on two users "concurrently added to the group"). This is **[open]** (question 15), with two options:
  - A member device that processes the add of a device it has not approved removes that device, and proposes it again. Cost: the device may already hold the remover's ratchet state from the acknowledgment, and each concurrent add costs a further removal and add.
  - A member device does not acknowledge an add of a device it has not approved until its user decides. Cost: a change to DCGKA's add-ack step, which needs analysis.
- **Joining is slower.** Every member device must approve every new device. Under online-only delivery ([decision 0005](0005-serverless-online-only-delivery.md)), an add waits until every member device has been online and its user has decided. One device that is lost or never online blocks every add, until it is removed.
- **Any member device can block adds by withholding approval, and remove any device by distrusting it.** DCGKA already lets any member remove any member. Rules that limit this belong to question 16.
- **Users judge devices of strangers.** In a group whose members are not all contacts, each user approves the devices of members they do not know. Safety codes ([open question 4](../v0.1/open-questions.md#4-key-verification-method)) help. Users who approve without checking weaken the guarantee to what decision 0016 had.
- **Size.** An approval carries the approved device's public keys and a hybrid signature of about 4.7 KB. Adding one device to a group of n member devices takes n approvals, about 1 MB for 128 devices, and members relay each of them to every member ([decision 0017](0017-retry-expiry-and-relaying.md)). A proposal carries a whole device list, about 8.6 KB per device on it (decision 0016).
- **Recovery is a membership change.** A removal costs about as much as a key update (decision 0019: about 306 KB for 128 devices), and the add costs an acknowledgment from every member. B cannot read the group messages that were sent between the break and its new add.
- **Approvals are signed and not deniable.** Any member can show a third party which device approved which device, as for other control messages (decision 0006).
- **More for members to observe.** This is added to [the list of what other parties can observe](../v0.1/metadata.md):
  - which member device approved which device, and when;
  - that a device was removed after it was proposed or added, which suggests that a member distrusts it;
  - from proposals, every device of a proposed user and its addresses, including devices that are not in the group;
  - from repair requests, that two devices lost their two-party state, and when.
- **The paper's analysis.** The condition of point 3 only stops some adds from taking effect, and points 4 and 5 use DCGKA's own operations. Whether DCGKA's proofs still hold with this condition is **[open]** for the same review that decision 0019 needs.
- **Formal model.** [Decision 0013](0013-formal-verification.md) requires the group model to change with the protocol. `group_approval.pv` shows that an honest member sends its seed secret to a device only if every member device approved that device for that group. It has two honest members and a fixed membership. It does not cover concurrent adds, removal, distrust, or recovery.

## Alternatives considered

- **Seed secrets to every member device, as DCGKA does, with approval by the adding member only** (decision 0019, point 7, first option). Not chosen. A device that one member holds or distrusts reads that member's group messages, which the team's requirement rules out.
- **Leaving held devices out of a member's seed secrets** (decision 0019, point 7, second option). Not chosen. It changes DCGKA's core: the left-out device's copy of the sender's ratchet diverges from everyone else's.
- **Approval by a set number of members, or by members with a role** (question 16, option B). Not chosen now. It is weaker than approval by every member device. It can be revisited when question 16 is decided.
- **A new two-party state from a fresh prekey, announced in a control message, for recovery.** Not chosen. It adds a step to DCGKA that needs new analysis. Removal and re-adding use DCGKA's own operations.
