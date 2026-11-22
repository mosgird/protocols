# Accessibility

This repository is a specification written as Markdown. Its accessibility goals cover two readers: people reading the documents, and implementers who build software from them.

## The documents

- Headings are used in order and say what the section contains.
- Link text makes sense on its own. "See the list of what other parties can observe" is preferred to "click here".
- Tables have header rows.
- Meaning is never carried by color or by layout alone.
- The text is plain Markdown that works with screen readers, zoom, and text-to-speech.
- Any figure or diagram has a text description beside it that says what it shows. A figure never carries information the text does not also state.
- Figures are made by people, not by AI tools. See [AI_POLICY.md](AI_POLICY.md).

## Plain language

Sentences are short. Terms are defined once, in [terminology.md](spec/v0.1/terminology.md), and used with the same meaning everywhere.

## For implementers

The specification does not define a user interface. Implementations meet the accessibility goals in their own repositories. The desktop repository, for example, has its own accessibility document.

The protocol should not require an interaction that depends on sight or hearing alone. If a future section does, it must say so and name an alternative.

## Status

This document states intent for the documents as they are today. It does not claim that any reader or implementation has been tested.
