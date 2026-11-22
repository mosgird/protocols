# 0020. Approval before a device joins a group, and recovery by removal and re-adding

**Status:** Proposed

## Context

[Decision 0016](0016-user-identity-and-linked-devices.md) gives each device a trust state for every device of a contact: approved, held, or distrusted. A held or distrusted device receives nothing. In groups this held only in part. DCGKA gives every member device a copy of every member's ratchet (DCGKA paper, section 4), so a device that one member has not approved still reads that member's group messages if another member added it. [Decision 0019](0019-two-party-component-for-dcgka.md), point 7, left open whether a member sends its seed secrets to such a device.

The team requires that a device that is not approved sees nothing at all, in groups as in direct messages.

Decision 0019 also records that a two-party message that cannot be read breaks the state between two devices in a group, and that DCGKA has no step to restart it.

The DCGKA paper assumes that additions are unique: "if the same user is added more than once to the same group, then each user addition results in a separate protocol instance, and each is associated with a separate ID. This can be achieved e.g. by including a nonce in the user ID" (section 2).

[Decision 0006](0006-dcgka-for-groups.md) allows a change to DCGKA only by a new decision record. This is that record. It uses DCGKA's own add and remove operations, and adds a condition under which an add takes effect.

## Decision

1. **Approval and withdrawal.** An *approval* is a group control message that names the group and a device's *fingerprint*: the keyed BLAKE2b hash of the device's identity KEM public key and signature public keys, as for the fingerprints of decision 0016. A *withdrawal* has the same form and cancels an earlier approval. Like every control message, both are signed under the sender's identity key (decision 0006). A device sends an approval only for a device whose trust state it holds as approved:
   - The user's own devices are approved through the device list that the user key signs (decision 0016, point 5). A device approves them without asking its user.
   - A contact's device is approved as decision 0016, point 10, describes.
   - A device of a group member who is not a contact starts as held. The user sees the device, its user identifier and its fingerprint, and approves or distrusts it, as for a contact's device.

   A device that distrusts a device it has approved for a group sends a withdrawal in that group. If the device is a member, it then removes it (point 5).
2. **Proposal, with approval both ways.** To add a device D to a group, a member device sends a *proposal*: a control message that carries D's user's current device list (decision 0016, point 4), D's signed prekey (decision 0019, point 5), a fresh random member identifier for D, and D's own approvals of every current member device. D signs those approvals under its identity key and gives them to the proposing member over a decision 0012 session, after its own user has approved each member device. Every member device then sends an approval of D when its user approves D. A device that holds or distrusts D sends nothing.
3. **The add takes effect only with every approval.**
   - A member device sends DCGKA's add for D only when its causal history holds, for D in that group, an approval from every member device, with no later withdrawal from the same device. The members are those that the add's causal predecessors determine, as DCGKA computes membership.
   - Every member device checks the same condition when it processes the add. If it fails, the add is invalid: no member applies it, and no member sends D anything. Approvals and withdrawals are control messages, so the condition depends only on the add's causal predecessors, and every member reaches the same result.
   - An approval holds until the approving device withdraws it or leaves the group.
   - Adding a user means proposing each of their devices. Each device joins on its own approvals. A user's new device joins a group in the same way (decision 0016, point 12): the user's other devices approve it at once, and every other member device must approve it as well.
   - Messages that name an invalid add, and withdrawals concurrent with an add, are **[open]** ([open question 20](../v0.1/open-questions.md#20-membership-approval-in-groups)).
4. **A fresh member identifier for every add.** DCGKA identifies each member by the member identifier that its proposal carries. Every add of a device, including the re-add of point 6, uses a new one, as the paper's assumption of unique additions requires. When a member is removed, every member device deletes all state it keeps for that member identifier, including the two-party states. Approvals and withdrawals name the device's fingerprint, not a member identifier, so they carry over to the device's next add.
5. **Distrust removes the device for everyone.** A member device that distrusts a member device sends its withdrawal and then removes that device with DCGKA's remove. A member device that distrusts a user key (decision 0016, point 10) does this for every device of that user in every group it shares with them. The removed device can join again only under point 3, which the withdrawal prevents while the distrusting device is a member. DCGKA already lets any member remove any member. Which members may remove whom is left to the permission rules of [open question 16](../v0.1/open-questions.md#16-community-moderation-without-an-operator).
6. **Recovery of a broken pair: removal and re-adding.**
   - When a member device B cannot read a two-party message from member device A in a group (decision 0019, Consequences), B sends a *repair request*: a control message that names A and the message.
   - B is then removed from the group and added again, with a new member identifier (point 4). One of the other devices of B's user that is a member of the group does this, or else any member device that the rules of question 16 permit. Until those rules exist, any member device may.
   - The new add needs no action from users, because the approvals of B still hold (point 3). If a member has withdrawn its approval of B in the meantime, B is not added again.
   - B then starts new two-party states with every member, as any added device does.
   - How members merge two repairs of the same device made at the same time is **[open]** (question 20).
7. **DCGKA is otherwise unchanged.** Seed secrets go to every member device, as the paper specifies. Every member device has approved every other member device, and none has withdrawn that approval, so no member device is held or distrusted by another. This settles decision 0019, point 7.

## Consequences

- **A device that is not approved receives nothing from honest members.** Two cases remain:
  - Devices added at the same time have not approved each other. In DCGKA each sends the other its ratchet state with its acknowledgment of the other's add (DCGKA paper, section 6, on two users "concurrently added to the group"). This is **[open]** (question 20).
  - A dishonest member can pass any key it holds to any device, approved or not. No protocol prevents this. The guarantee holds against honest members and against outsiders.
- **Joining is slower.** Every member device must approve every new device, and the new device must approve every member device. Under online-only delivery ([decision 0005](0005-serverless-online-only-delivery.md)), an add waits until every member device has been online and its user has decided. One device that is lost or never online blocks every add until it is removed.
- **Any member device can block adds by withholding approval, and remove any device.** DCGKA already lets any member remove any member. Rules that limit this belong to question 16.
- **Users judge devices of strangers.** In a group whose members are not all contacts, each user approves the devices of members they do not know, and a new member's user approves every member device. Safety codes ([open question 4](../v0.1/open-questions.md#4-key-verification-method)) help. Users who approve without checking weaken the guarantee to what decision 0016 had.
- **Size.**
  - An approval or withdrawal carries a 32-byte fingerprint and a hybrid signature of about 4.7 KB. Adding one device to a group of n member devices takes n approvals from the members and n from the new device: about 1.2 MB for 128 devices. Members relay each control message to every member ([decision 0017](0017-retry-expiry-and-relaying.md)).
  - A proposal carries a whole device list, about 8.6 KB per device on it (decision 0016).
  - DCGKA's welcome message carries the group's history of control messages (DCGKA paper, section 6), so every later welcome includes these approvals. How the history in a welcome is pruned is **[open]** (question 20).
- **Recovery is a membership change.** The removal costs about as much as a key update (decision 0019: about 306 KB for 128 devices). The add costs the welcome and an acknowledgment from each of the 127 other members, each with a signature of about 4.7 KB and a two-party message of about 2.4 KB, about 0.9 MB in all. B cannot read A's messages from the break until the removal, nor any group message sent while it is removed. A new two-party state between devices that have not met in a session starts under the signed prekey, with the exposure that decision 0019 records.
- **Repair requests are not proof of a failure.** A member can send them to force removals and adds. Clients should notice repeated requests from one device.
- **Approvals and withdrawals are signed and not deniable.** Any member can show a third party which device approved or withdrew which device, as for other control messages (decision 0006).
- **More for members to observe.** This is added to [the list of what other parties can observe](../v0.1/metadata.md):
  - which member device approved or withdrew which device, and when, which shows distrust;
  - from proposals, every device of a proposed user and its addresses, including devices that are not in the group;
  - from repair requests, that two devices lost their two-party state, and when;
  - for a new member, from the welcome, the whole history of approvals, withdrawals and removals in the group.
- **The paper's analysis.** The condition of point 3 only stops some adds from taking effect, point 4 follows the paper's own assumption, and points 5 and 6 use DCGKA's own operations. Whether DCGKA's proofs still hold with the condition is **[open]**, for the same review that decision 0019 needs.
- **Formal model.** [Decision 0013](0013-formal-verification.md) requires the group model to change with the protocol. `group_approval.pv` has two honest member devices, of which one approves only one honest device. It shows that each member sends its seed secret to a device only with an approval from both members for that device and group, and that a seed secret stays secret from every device the second member has not approved. It does not cover membership computed from causal order, withdrawals, member identifiers, approval by the new device, concurrent adds, removal, or recovery.

## Alternatives considered

- **Seed secrets to every member device, as DCGKA does, with approval by the adding member only** (decision 0019, point 7, first option). Not chosen. A device that one member holds or distrusts reads that member's group messages, which the team's requirement rules out.
- **Leaving held devices out of a member's seed secrets** (decision 0019, point 7, second option). Not chosen. It changes DCGKA's core: the left-out device's copy of the sender's ratchet diverges from everyone else's.
- **Approval by a set number of members, or by members with a role** (question 16, option B). Not chosen now. It is weaker than approval by every member device. It can be revisited when question 16 is decided.
- **Re-adding a device under its old member identifier.** Not chosen. DCGKA starts a two-party state only for a member it holds none for, so the broken state would remain, and the paper assumes unique additions.
- **A new two-party state from a fresh prekey, announced in a control message, for recovery.** Not chosen. It adds a step to DCGKA that needs new analysis. Removal and re-adding use DCGKA's own operations.
