"""Shared CSS. Kept in one place so every tab looks consistent -- cards,
badges, and monospace context blocks, in a clean, modern, product-style
visual language (no illustration or playful styling)."""

CSS = """
<style>
:root {
    --ink: #0f172a;
    --muted: #64748b;
    --border: rgba(15, 23, 42, 0.10);
    --surface: rgba(15, 23, 42, 0.03);
    --accent: #2563eb;
    --accent-soft: rgba(37, 99, 235, 0.08);
    --good: #16a34a;
    --good-soft: #dcfce7;
    --warn: #b45309;
    --warn-soft: #fef3c7;
    --bad: #b91c1c;
    --bad-soft: #fee2e2;
}

h1, h2, h3, h4 { letter-spacing: -0.01em; }

.app-header {
    padding: 0.25rem 0 1.25rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.app-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
}
.app-subtitle {
    color: var(--muted);
    font-size: 0.95rem;
    margin-top: 0.15rem;
}

.status-pill {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.4rem;
    letter-spacing: 0.01em;
}
.pill-blue { background: var(--accent-soft); color: var(--accent); }
.pill-green { background: var(--good-soft); color: var(--good); }
.pill-amber { background: var(--warn-soft); color: var(--warn); }
.pill-gray { background: var(--surface); color: var(--muted); }
.pill-red { background: var(--bad-soft); color: var(--bad); }

.source-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.95rem 1.1rem;
    margin-bottom: 0.65rem;
    background: white;
}

.mono-block {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.83rem;
    white-space: pre-wrap;
    background: var(--surface);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    border: 1px solid var(--border);
}

.flow {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    align-items: center;
    margin: 0.5rem 0 1.1rem 0;
}
.flow-step {
    padding: 0.4rem 0.85rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--muted);
}
.flow-step.done { background: var(--good-soft); color: var(--good); border-color: transparent; }
.flow-step.skipped { background: var(--bad-soft); color: var(--bad); border-color: transparent; opacity: 0.85; }
.flow-arrow { opacity: 0.35; font-size: 0.9rem; }

.hero-statement {
    font-size: 1.05rem;
    font-weight: 600;
    text-align: center;
    padding: 1rem;
    border-radius: 12px;
    background: var(--accent-soft);
    border: 1px solid rgba(37, 99, 235, 0.18);
    color: var(--ink);
}

.section-label {
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--muted);
    margin-bottom: 0.3rem;
}
</style>
"""


def inject():
    import streamlit as st

    st.markdown(CSS, unsafe_allow_html=True)
