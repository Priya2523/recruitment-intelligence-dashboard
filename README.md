# 🎯 Recruitment Follow-up & Offer-to-Joining Intelligence System

### *"Which candidate should I call today — and why?"*

An AI-supported dashboard that tells recruiters exactly which candidates need attention, how likely they are to actually join after accepting an offer, and what to say to them — automatically.

🔗 **Live App:** [recruitment-intelligence-dashboard.onrender.com](https://recruitment-intelligence-dashboard.onrender.com)
💻 **Code:** [github.com/Priya2523/recruitment-intelligence-dashboard](https://github.com/Priya2523/recruitment-intelligence-dashboard)

---

## 📌 Table of Contents

1. [The Problem](#-the-problem)
2. [Why I Built This](#-why-i-built-this)
3. [The Solution](#-the-solution)
4. [How It Works (Architecture)](#-how-it-works-architecture)
5. [Screenshots](#-screenshots)
6. [The Intelligence Layer — Explained Simply](#-the-intelligence-layer--explained-simply)
7. [What I Actually Did (Step by Step)](#-what-i-actually-did-step-by-step)
8. [Tech Stack](#-tech-stack)
9. [Data Privacy](#-data-privacy)
10. [Project Structure](#-project-structure)
11. [Running It Yourself](#-running-it-yourself)
12. [Limitations & What's Next](#-limitations--whats-next)
13. [About This Project](#-about-this-project)

---

## 🧩 The Problem

Small and mid-sized recruitment teams juggle hundreds of candidates across dozens of open roles at the same time. In practice, this creates four recurring headaches:

1. **No one knows who to follow up with today.** Recruiters rely on memory or scattered Excel sheets to decide who to call next.
2. **Offered candidates silently drop off.** A candidate accepts an offer, goes quiet, and doesn't show up on their joining date — with no early warning.
3. **No one can explain *why* a candidate is risky.** Even when someone senses a candidate might not join, there's no consistent, defensible reason to point to.
4. **No clear next action.** Even after spotting a problem, recruiters don't have a ready-made message or task to act on immediately.

In short: **recruiters have data, but not intelligence.**

## 💡 Why I Built This

This project is a direct continuation of my earlier [Recruitment Analytics Dashboard](https://github.com/Priya2523/recruitment-analytics-platform), which analyzed *past* recruiter activity (who searched for what, when, and how).

That dashboard answered "**what already happened**." This one answers "**what should happen next**."

The existing 835-candidate dataset (from clients like Prowess, Lodha, Fischer, Hilti & Alumil, and L&T) is rich in recruiter activity data — but it was never designed to track the *offer-to-joining* journey. Rather than inventing a disconnected, fake dataset, I chose a more realistic approach: **reuse the real recruitment data as the foundation, and layer a lifecycle-tracking and risk-intelligence system on top of it** — the same way a real product would evolve.

## 🛠️ The Solution

A system that automatically:

| # | What it answers | How |
|---|---|---|
| 1 | *Which candidates need follow-up today?* | A **Follow-up Priority Engine** scores every candidate on urgency |
| 2 | *Which offered candidates are at risk of not joining?* | A **Joining-Risk Engine** scores every candidate 0–100 on the chance they don't show up |
| 3 | *Why is this candidate high risk?* | Every score comes with the **exact reasons** (salary gap, long notice period, silence, etc.) |
| 4 | *What should the recruiter do about it?* | An **AI layer (Groq/Llama)** writes a plain-English recruiter task and a ready-to-send WhatsApp message |

The output is designed to read like a briefing, not a spreadsheet:

> **Candidate:** C1024 · **Joining Risk: 78% — HIGH**
> **Key signals:** Expected ₹8.5L vs Offered ₹7.5L · 60-day notice period · No response in 6 days · Joining in 18 days
> **AI explanation:** Candidate shows elevated joining risk due to a salary gap, long notice period, and declining communication.
> **Recommended action:** Contact today and reconfirm joining commitment. Discuss compensation concerns if applicable.

Every risk score, follow-up priority, and recommended action shown in the dashboard is generated this same way.

## 🏗️ How It Works (Architecture)

In plain terms: raw, messy recruiter spreadsheets go in one end, and a prioritized, explained, ready-to-act call list comes out the other end.
