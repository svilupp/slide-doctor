# Slide Doctor

**Slide Doctor: Your High-Quality Multi-Modal A.I. Agent for Prescribing Perfect, Professional PPTs**

Slide Doctor will make Powerpoint a breeze. Now everyone can have hi-quality, professional looking PPT slides. It aims to be the ultimate **Multi-modal A.I.** tool, powered by **Pixtral 12B** for fixing PPT Presentations.

---

## Install

You have to have `uv`

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

---

## Usage

Run with ( don't forget to add your Mistral API Key in the Env ):

```sh
uv run
```

---

## Details

The tool will:

- use open source libs to convert said slide(s) to PDF(s) then from pdf to PNG(s)
- use the a set of A.I. agents, including Pixtral 12B LLM and analyze the image(s) and generate a list of adjustments:
	* perform spellchecker (british, capitalization) — TEXT
	* chart-checker (N.U.T.S.A.C. aka source check) - VISUAL
	* consistency-checker (time, name) — TEXT
	* visual-checker (overlap, wrap fail, alignment of items, inappropriate font size for the element) — VISUAL
	* font checker (different fonts, too many font sizes - max 2-3)

Market Opportunity: Huge, business runs on Powerpoint // Management consulting is effectively expert networks + fancy powerpoint

---

## Future Work

Ideally, the tool should:

- markdown to slide // create exec summary?
    - compile all titles and slide images
    - https://github.com/MartinPacker/md2pptx
    - align with LLM to be the same style (unzip pptx and show the slide xml vs another slide xml and tell llm to be consistent)
- fix pptx
    - do it on a copy, is it valid? if it is, replace the original
- front end for showing errors - gradio
    - show image of the page and list issues
    - tick the once to solve
    - one page per view

---

---
