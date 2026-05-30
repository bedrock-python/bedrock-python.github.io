# Blog

News, release notes, and deep dives from the **Bedrock Python** ecosystem — the
infrastructure libraries and developer tools that power our backend services.

What you'll find here:

- **Releases** — what changed and why for each library and tool
- **Design** — the reasoning behind our architectural choices
- **Tutorials** — how to use the libraries in real production scenarios
- **Libraries** — focused write-ups on individual PyPI packages
- **Tools** — posts about standalone developer tools like `mr-review` and `mattermind`

## Browse

- [Archive](archive/index.md) — every post by year
- [Categories](category/index.md) — browse by topic
    - [Libraries](category/libraries.md)
    - [Tools](category/tools.md)
    - [Design](category/design.md)
    - [Tutorials](category/tutorials.md)
    - [Releases](category/releases.md)
    - [Meta](category/meta.md)

---

## Latest posts

### [Introducing mr-review: AI-powered merge request reviews](posts/2026-05-28-introducing-mr-review.md)

*2026-05-28 · Tools*

A new CLI tool that runs locally and uses an LLM to walk through a merge request
diff the way a thorough engineer would — staged review with brief, dispatch,
polish, and post phases, plus presets for thorough, security, style, and
performance reviews.

### [The Transactional Outbox pattern in Python: omni-box](posts/2026-05-15-transactional-outbox-with-omni-box.md)

*2026-05-15 · Libraries, Design*

How `omni-box` solves the classic dual-write problem between Postgres and Kafka
using the Transactional Outbox pattern, plus the Inbox side for idempotent
consumers.

### [Welcome to the Bedrock Python Blog](posts/2026-05-30-welcome.md)

*2026-05-30 · Meta*

An introduction to the ecosystem — what Bedrock Python is, the libraries that
form the foundation, reliability, and testing layers, and what you can expect
from this blog.
