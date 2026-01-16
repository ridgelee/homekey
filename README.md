# Homekey - LLM-based Property Report Generation



## Intro

A lightweight prototype that turns **property photos + listing description + zipcode** into:

1. an **AI-generated enhanced image** (for “Image Studio” style editing), and
2. a **Markdown real estate analysis report** (community / climate / schools / crime + risks)

This project is intentionally minimal, but structured to reflect production-style architecture and decision-making under constraints.



## What This Prototype Implemented?

- **Input**:
  - a list of property images (image_id, url, optional room_type_hint)
  - a preferred visual style (e.g. Modern Style)
  - a listing description (free text, like a landloard Introduction, "Bright open layout, renovated kitchen, large windows, good natural light.")
  - a zipcode (e.g. 95112)
- **Output** (in **JOSN** format):
  - a single enhancement prompt that can be used by an image editor / generative model
  - an image enhancement plan per photo (suggested edits + mock enhanced URL)
  - zipcode insights (community, climate, schools, crime) via mock datasets
  - a final Property Brief:
    - 5 key highlights
    - risk flags
    - confidence notes
    - a polished Markdown report (LLM-generated using only provided data)



## Classic Pipeline Architecture

1. Input (images + style + listing_description + zipcode)
2. `build_enhancement_prompt()` create AI image prompt (LLM)
3. `image_enhance_plan generation`, can link to self-trained model to generate productive image
4. `fetch_zipcode_insights()`, community/climate/schools/crime (mock)
5. `build_brief()`, highlights + risk_flags + Markdown report (LLM), Structured Output JSON



## Core Modules

### 1. LLM Setup

- `_get_openai_client()` loads API key from environment.
- `DEFAULT_LLM_MODEL` defaults to gpt-4o-mini unless overridden.



### 2. Image Enhancement Prompt Builder (LLM)

- **Function:** `build_enhancement_prompt(style, listing_description, room_type_hint)`

- Generates one concise prompt for image enhancement that matches the chosen style.

- Design choices:

  - Uses a style phrase mapping (Modern Neutral, Luxury, etc.) to keep prompts consistent.
  - Adds hard constraints to reduce hallucination / unrealistic edits:
    - “Do NOT alter architecture”
    - “Do NOT add fake windows”
    - “Do NOT change room layout drastically”

- Eg. "Enhance the real estate photos by applying lighting correction ... Focus on maintaining a neutral color palette..."

  

### 3. Zipcode Insights Fetch and Summarize

- **Function**: `fetch_zipcode_insights(zipcode)`
- Internally calls 4 mock providers:
  - `fetch_community()`
  - `fetch_climate()`
  - `fetch_schools()`
  - `fetch_crime()`

- Each returns standardized fields:

  - summary
  - highlights[]
  - source
  - updated_at

  Crime also includes:

  - risk_level (Low | Medium | High)



### 4. Image Enhance Plan Generator

- It generates:
  - baseline suggested edits (lighting, color, declutter, staging)
  - style-specific edits via `_style_suggested_edits(style)`
  - room-specific edits via `_room_suggested_edits(room_type_hint)`

- Eg. 

  ```Json
  {
    "image_id": "img_2",
    "room_type_hint": "kitchen",
    "suggested_edits": [
      "Correct lighting and exposure",
      "Optimize color balance",
      "Declutter visible surfaces",
      "Refine staging for the room",
      "Use neutral color balance and clean whites",
      "Keep decor minimal and modern",
      "Clear counters, enhance appliance finish"
    ]
  }
  ```



### 5. Final Report Generator (LLM)

- **Function:** `build_brief(listing_description, zipcode_insights, image_enhance_plan)`
- It produces:
  - **AI highlights** (up to 5)
  - **risk_flags** (rule-derived)
  - **confidence_notes** (explicitly stating limitations)
  - **🌟narrative_markdown** (LLM-generated report)
- Eg.
  - If crime risk is Medium/High → add crime risk flag
  - If schools contain “mixed/varied/uneven” → add school variability flag
  - If climate hints mention extremes → add climate caution flag
  - Missing listing description or no images → flag incomplete input

- **Constraint decision:**

  The report is LLM-written, but the system enforces “**non-hallucinating**” behavior by providing:

  - strict system prompt (“Use only the provided data”)
  - explicit “verbatim blocks” for image display and plan lines



## How to Run?

1. make sure install: `openai`

2. Set OpenAI API Key(you can use mine): 

   ```bash
   export OPENAI_API_KEY=""
   ```

3. Run code:

   ```bash
   python property_brief.py
   ```

- Example Output:

```Json
{
  "enhancement_prompt": "Enhance the real estate photos by applying lighting correction to maximize natural light, optimizing colors for a bright and clean appearance, decluttering the space to create a minimal look, and implementing modern staging improvements. Focus on maintaining a neutral color palette that complements the bright open layout of the renovated kitchen and living room with large windows.",
  "image_enhance_plan": [
    {
      "image_id": "img_1",
      "original_url": "https://example.com/living.jpg",
      "room_type_hint": "living_room",
      "suggested_edits": [
        "Correct lighting and exposure",
        "Optimize color balance",
        "Declutter visible surfaces",
        "Refine staging for the room",
        "Use neutral color balance and clean whites",
        "Keep decor minimal and modern",
        "Align furniture, clear cluttered surfaces"
      ],
      "mock_enhanced_url": "https://example.com/enhanced/img_1.jpg"
    },
    {
      "image_id": "img_2",
      "original_url": "https://example.com/kitchen.jpg",
      "room_type_hint": "kitchen",
      "suggested_edits": [
        "Correct lighting and exposure",
        "Optimize color balance",
        "Declutter visible surfaces",
        "Refine staging for the room",
        "Use neutral color balance and clean whites",
        "Keep decor minimal and modern",
        "Clear counters, enhance appliance finish"
      ],
      "mock_enhanced_url": "https://example.com/enhanced/img_2.jpg"
    }
  ],
  "zipcode_insights": {
    "community": {
      "summary": "Urban neighborhood with mixed residential and commercial blocks.",
      "highlights": [
        "Walkable streets and local shops",
        "Access to transit corridors",
        "Active neighborhood associations"
      ],
      "source": "mock_community_dataset_v1",
      "updated_at": "2026-01-01"
    },
    "climate": {
      "summary": "Mild climate with warm summers and cool winters.",
      "highlights": [
        "Warm summer afternoons",
        "Cool evenings in winter",
        "Low annual snowfall"
      ],
      "source": "mock_climate_dataset_v1",
      "updated_at": "2026-01-01"
    },
    "schools": {
      "summary": "Schools show mixed performance with a range of programs.",
      "highlights": [
        "Varied academic outcomes across schools",
        "STEM and arts programs available",
        "Some schools within walking distance"
      ],
      "source": "mock_school_dataset_v1",
      "updated_at": "2026-01-01"
    },
    "crime": {
      "summary": "Crime levels are moderate relative to nearby areas.",
      "risk_level": "Medium",
      "highlights": [
        "Property incidents are the most common",
        "Police presence around transit hubs",
        "Neighborhood watch activity reported"
      ],
      "source": "mock_crime_dataset_v1",
      "updated_at": "2026-01-01"
    }
  },
  "brief": {
    "highlights": [
      "Listing description: Bright open layout, renovated kitchen, large windows, good natural light.",
      "Planned image enhancements for 2 photos",
      "Community: Urban neighborhood with mixed residential and commercial blocks.",
      "Climate: Mild climate with warm summers and cool winters.",
      "Schools: Schools show mixed performance with a range of programs."
    ],
    "risk_flags": [
      "Crime risk level reported as Medium",
      "School performance appears variable across zones",
      "Climate notes include seasonal extremes or events"
    ],
    "confidence_notes": [
      "Zipcode insights are mock data and should be verified with local sources",
      "Image enhancement suggestions are stylistic guidelines, not executed edits"
    ],
    "narrative_markdown": "# Real Estate Analysis Report\n\n## Overview\nThe property features a bright open layout with a renovated kitchen and large windows that provide good natural light.\n\n## Image Enhancement Plan\n- img_1: living_room\n- img_2: kitchen\n\n## Images\n**img_1** (living_room)  \nOriginal: ![](https://example.com/living.jpg)  \nEnhanced (mock): ![](https://example.com/enhanced/img_1.jpg)\n\n**img_2** (kitchen)  \nOriginal: ![](https://example.com/kitchen.jpg)  \nEnhanced (mock): ![](https://example.com/enhanced/img_2.jpg)\n\n## Community\nThe property is located in an urban neighborhood characterized by mixed residential and commercial blocks. Highlights include:\n- Walkable streets and local shops\n- Access to transit corridors\n- Active neighborhood associations\n\n## Climate\nThe area enjoys a mild climate with warm summers and cool winters. Key features include:\n- Warm summer afternoons\n- Cool evenings in winter\n- Low annual snowfall\n\n## Schools\nSchools in the vicinity show mixed performance with a variety of programs available. Highlights include:\n- Varied academic outcomes across schools\n- STEM and arts programs available\n- Some schools within walking distance\n\n## Crime & Safety\nCrime levels in the area are moderate relative to nearby regions, with a risk level categorized as medium. Highlights include:\n- Property incidents are the most common\n- Police presence around transit hubs\n- Neighborhood watch activity reported\n\n## Risks / What to Verify\n- Crime risk level reported as Medium\n- School performance appears variable across zones\n- Climate notes include seasonal extremes or events"
  }
}
```



## My Trade off

- **Planning-first image enhancement (no real image generation yet)**: The code generates a high-quality enhancement prompt and a per-image edit plan, but uses mock_enhanced_url placeholders instead of running an actual enhancement model. This separates “what we want to do” from “how we render images,” enabling future model plug-in. This minimizes setup friction and makes it easy to demo, test, and iterate fast before committing to infrastructure.

- **Structured JSON output alongside Markdown**: The system returns both machine-readable structured fields and a human-readable report, trading slightly more code complexity for better extensibility into future UI rendering and analytics workflows.

  JSON supports future UI + automation, while Markdown is immediately readable for end users and internal review.



## **Extension Ideas**

- Tech:
  - We can extend this prototype by integrating our **own trained image enhancement model** to generate listing-quality property photos. 
  - Add caching for repeated zipcodes
  - When fetch zip code insights, can use live API and design completed fallback framework to optimize   the whole system.
- Business:
  - New users get limited free generations, while additional usage can be unlocked by contributing more photos or upgrading to a membership plan.
  - Membership users also unlock a premium, data-backed property report covering community, climate, schools, crime, plus deeper signals like renovation/repair history and sale/rental records for a more objective and easy-to-read decision brief.



