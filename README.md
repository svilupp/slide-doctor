# Slide Doctor

**Revolutionize Your Presentations with AI-Powered Precision**

Slide Doctor transforms your PowerPoint presentations into polished, professional masterpieces using advanced AI technology. Whether you're a business professional, educator, or student, Slide Doctor ensures your slides are error-free, visually appealing, and impactful.

![Demo Video](./assets/video.gif)

> [!NOTE]
This project has been developed over the weekend at the Mistral AI London Hackathon (October 2024)

---

## Why Slide Doctor?

Creating high-quality presentations is crucial in today's fast-paced world where first impressions matter. Slide Doctor empowers you to:

- **Enhance Visual Appeal**: Automatically identifies and corrects layout issues, misalignments, and inconsistent formatting.
- **Improve Clarity**: Checks for spelling errors, ensures proper capitalization, and maintains consistent terminology.
- **Save Time**: Automates tedious proofreading and formatting tasks so you can focus on your content.
- **Boost Confidence**: Present with assurance knowing your slides meet professional standards.

Join countless individuals who have elevated their presentations with Slide Doctor. Make your slides not just good—but exceptional.

---

## Installation

Slide Doctor requires `uv` to run. If you don't have `uv` installed, follow these steps:

### Install UV

Download and Install UV:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For more details, visit the [UV Installation Guide](https://github.com/astral-sh/uv).

### Set Up Your Environment

Ensure you have your Mistral API Key added to your environment variables:

```sh
export MISTRAL_API_KEY=your_api_key_here
```

### Set up LibreOffice on Your Mac

Download LibreOffice [here](https://www.libreoffice.org/download/download-libreoffice/).

---

## Usage

With `uv` installed and your environment set up, you can start using Slide Doctor.

### Run Slide Doctor in Gradio Interface

```sh
uv run gradio_interface.py
```

### Example Workflow

1. **Prepare Your Presentation**: Have your PowerPoint file (`.pptx`) ready for analysis.

2. **Provide Basic Context**:

    ```plaintext
    Investor presentation. It must be high quality. I am Jan Smith and today is October 2024.
    ```

3. **Review the Report**: Slide Doctor will generate a detailed report highlighting issues and suggestions.

4. **Apply Corrections**: Choose to automatically apply fixes or manually adjust your slides based on the recommendations. TODO! This is not working yet...

---

## How It Works

Slide Doctor utilizes a combination of open-source libraries and AI agents to analyze and enhance your presentation:

- **Conversion Process**:

    - Converts slides to PDFs and then to PNG images for the visual analysis. Extract text via `python-pptx`.

- **AI-Powered Analysis**:

    - **Pixtral 12B LLM**: An advanced language model that examines both visual and textual elements.
    - **Mistral Large 2409**: Leading edge LLM to analyze the textual side of the presentation.

- **Key Features**:

    - **Spell Checker**: Identifies spelling mistakes and enforces consistent capitalization.
    - **Chart Checker (N.U.T.S.A.C. Source Check)**: Verifies the accuracy and source of data in charts.

Note: Not all checkers have been implemented yet! 
Outstanding:

- **Consistency Checker**: Ensures uniformity in terminology, dates, and names throughout the presentation.
- **Visual Checker**: Detects overlapping elements, improper text wrapping, and alignment issues.
- **Font Checker**: Alerts if there are too many font types or sizes, promoting a cohesive look.

It can be easily added without any code changed, just by updating `config/config.yaml` (think of it as a definition of "house style").

---

## Roadmap

In an ideal world, we would have liked to add:

- [ ] **Automated Fixes**: Enable Slide Doctor to not only identify issues but also automatically fix them.
- [ ] **Safe Editing**: Enable agentic self-fixing loop with Pixtral for quality assurance.
- [ ] **Executive Summaries**: Generate executive summaries by compiling slide titles and images.
- [ ] **Claim Verification**: Integrate with the Brave API to check the validity of statements and data within your slides.
- [ ] **Cross-Slide Consistency**: Implement advanced consistency checks similar to ColPali to ensure uniformity across all slides.
- [ ] **Markdown to Slides**: Convert Markdown files into PowerPoint presentations and back to enable easier PPTX generation (leverage [md2pptx](https://github.com/MartinPacker/md2pptx)).
- [ ] **Voice Dictation**: Introduce audio input where you can dictate slide content & context.

---

## Market Opportunity

The demand for high-quality presentations is immense. Businesses, educators, and professionals worldwide rely on PowerPoint to communicate ideas effectively. Slide Doctor taps into this need by offering an AI-driven solution to elevate presentation standards effortlessly.

---
## Acknowledgments

Slide Doctor was developed as part of **Mistral AI Hackathon**, hosted in London, October 2024 by Mistral AI, A16Z, and Cerebral Valley ("HackUK"). We thank all organizers and supporters who made this event possible.

---

Elevate your presentations today with Slide Doctor—because every slide deserves perfection.