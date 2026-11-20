# Security policy

This repository holds the Mosgird protocol specification. A flaw in the design is a security problem even when no code exists yet. The most serious reports are design flaws that let someone read message content, forge identities or keys, bypass end-to-end encryption, or learn metadata the specification says is hidden (see [overview section 3.3](spec/v0.1/overview.md#33-what-the-server-can-and-cannot-observe)).

## Reporting a vulnerability

Do not report security problems in a public issue or pull request.

Report them privately with GitHub's private vulnerability reporting: open the **Security** tab of this repository and choose **Report a vulnerability**. You can also go directly to https://github.com/mosgird/protocols/security/advisories/new.

Include:

- what the problem is, and where it is (file, section, or commit);
- what an attacker could do with it, including whether message content, keys, identities, or metadata are exposed;
- steps to reproduce, or a proof of concept if you have one;
- whether you want to be credited.

We read every report. We do not yet guarantee a response time, and this page will say so if that changes.

## Scope

In scope: problems in the specification that break the security or privacy goals in [overview section 1](spec/v0.1/overview.md#1-goals), and errors in the decision records or the cryptographic references they depend on.

Out of scope: content policy. The protocol does not define which content is allowed ([overview section 2](spec/v0.1/overview.md#2-non-goals-v01)).

## Disclosure

We ask for coordinated disclosure: report first, give us a reasonable time to fix the problem, and do not publish details until a fix is available or we agree on a date. We credit reporters who want credit.

## Supported versions

No version is released yet. Only `main` is supported. When releases exist, this section lists which ones receive security fixes.
