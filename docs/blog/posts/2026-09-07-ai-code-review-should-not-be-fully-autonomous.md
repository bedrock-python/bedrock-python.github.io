---
date: 2026-09-07
authors:
  - alex
categories:
  - Tools
tags:
  - mr-review
  - code-review
  - llm
  - ai-agents
  - gitlab
  - github
---

# AI code review should not be fully autonomous

The obvious way to build an AI code reviewer is a webhook: a merge request opens, a model reads the diff, the comments appear. It is the first design everyone reaches for and the one I refused to build, because I had been on the receiving end of it. A bot that posts twelve comments on every merge request trains the team to skip all twelve, including the one that mattered, in about a week. This post is about the alternative that [mr-review](2026-05-28-introducing-mr-review.md) is built around: a pipeline where the model drafts and a person decides, and where nothing reaches the merge request that a human did not read first. It is a slower loop, on purpose, and it is the only version I have seen a team keep using.

<!-- more -->

What follows describes mr-review as it ships today, from its own documentation and source; the version at the time of writing is 0.2.2.

## What goes wrong when the bot posts

Three things, and they compound.

**Noise.** A model asked to review a diff will find something to say about every hunk, because it was asked to. Style remarks, restatements of what the code does, suggestions to add a docstring, a question about a variable name. Each is defensible; together they bury the one comment that says the retry loop can duplicate a charge. Reviewers learn the bot's comments are cheap and read them the way they read lint output, which is to say they scroll.

**Confident nonsense.** Sometimes the model is wrong, and it is wrong in complete sentences with a suggested fix. A human reviewer who is wrong is usually hedging; a model that is wrong is not. On a public merge request that comment now needs a reply, and the author spends ten minutes explaining to a bot why the code is fine, in front of colleagues, which is the specific experience that makes engineers hate the tool.

**Fatigue.** Every comment is a tax on the author and the reviewer. When most of them are noise or wrong, the tax buys nothing, and the rational response is to stop paying it: mute the bot, batch-resolve its threads, or quietly ask for it to be turned off. The autonomous reviewer's failure mode is not that it reviews badly. It is that it gets ignored, and then the one review that would have caught the incident gets ignored with the rest.

Every one of these is a consequence of the same decision: the model's output went straight to the merge request. Put a person between the two and all three change shape.

## The pipeline

A review in mr-review is a sequence of four stages, and it only moves forward:

```text
brief  →  dispatch  →  polish  →  post
```

**Brief** is what the model is asked. A preset, `thorough`, `security`, `style` or `performance`, decides the emphasis; toggles decide what context goes into the prompt beside the diff; free-text instructions carry whatever this repository cares about. The exact prompt can be fetched as text before anything is sent, so "what did we ask it" is never a mystery.

**Dispatch** sends the prompt to a model, streams the answer back, and parses it into comments: a file, a line, a severity from `critical` down to `suggestion`, and a body. The model is asked for a bare JSON array of those; if it answers with prose instead, the whole answer is kept as one `suggestion` rather than thrown away, and the parse error is reported. Nothing has touched the merge request yet.

**Polish** is the stage the autonomous design does not have. The comments sit in a UI, and a person reads them. A body can be edited; a severity can be changed; a comment can be dismissed. This is where the twelve become three. The two style remarks go. The restatement goes. The confident nonsense goes, before anyone had to reply to it. The one about the retry loop gets its severity raised and its wording tightened, because the person doing the polish knows the codebase and the model does not.

**Post** sends every comment still marked `kept` to the merge request as inline notes, and marks the iteration complete. What arrives is a review a human has vouched for. It carries the reviewer's name, and it is short.

There is no webhook receiver, no scheduler and no CI mode in the tool, and that is listed in its own documentation under what it does not do. A review starts because a person clicked. That constraint is the design.

## What the person adds

It is tempting to read the polish stage as a safety valve, a place to catch the model's mistakes. It is more than that. The person in the loop supplies the two things the model structurally cannot.

The first is context that is not in the diff. The model sees the change; the reviewer knows that this endpoint is called by the mobile client that cannot be updated for a year, that this table has a partition job running against it at 03:00, that the team decided last quarter not to add caching here. A comment the model got technically right and contextually wrong is dismissed in a second by someone who knows, and would have cost a thread by someone who did not.

The second is judgement about what is worth saying. A review is a message to a colleague, and its value goes down with its length. The model has no sense of that budget. The person does, and applies it, and the result reads like a review from a careful engineer who used a tool, rather than from a tool.

## The copilot, not the gatekeeper

The framing that makes this work is that the model is the reviewer's assistant, not the merge request's gate. It reads the whole diff without getting tired, it notices the missing `await` in the four-hundredth line, it checks every error path for the thing the security preset asked about, and it hands that to the person who will sign the review. The person decides. The team sees a review from a person.

That is also what keeps the tool honest about its own limits. Local models can be pointed at it, since any OpenAI-compatible endpoint is a provider, and a local model produces more noise and more nonsense than a frontier one; in the autonomous design that difference lands on the merge request, and in this one it lands on the polish stage, where it costs the reviewer a few more dismissals and nobody else anything. The pipeline degrades gracefully with the model because a person is the last stage.

## What it costs

A human in the loop is slower than a webhook, and the review does not appear on its own. Someone has to open the tool, pick the merge request, dispatch, polish and post, which is a few minutes per review. For a team that wanted the bot to replace the reviewer, that is the wrong tool; the bot never replaces the reviewer here, it makes the reviewer faster and more thorough. For a team that has watched an autonomous reviewer get muted, a few minutes per review is the price of the reviews being read.

mr-review runs as one or two containers against GitLab, GitHub, Gitea, Forgejo and Bitbucket with any Anthropic or OpenAI-compatible model behind it, and keeps its reviews as YAML on disk; the [introduction](2026-05-28-introducing-mr-review.md) covers the deployment. The four stages above are its whole shape.

The point was the third stage. Twelve comments in, three out, and a person's name on them.
