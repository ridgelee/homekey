from __future__ import annotations

import json
import os
from typing import List, Optional

try:
    from openai import OpenAI  # type: ignore[import-not-found]
except ImportError:  # Allows file to load without the dependency installed.
    OpenAI = None


DEFAULT_LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _get_openai_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError(
            "openai package is not installed. Run: pip install openai"
        )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(api_key=api_key)


def build_enhancement_prompt(
    style: str, listing_description: str, room_type_hint: Optional[str]
) -> str:
    """Generate an enhancement prompt via LLM based on style and context."""
    client = _get_openai_client()

    style_phrases = {
        "Modern Neutral": "bright, clean, minimal, neutral colors, modern staging",
        "Luxury": "upscale materials feel, balanced contrast, premium staging, polished look",
        "Bright Daytime": "daylight feel, brighter exposure, crisp whites, natural shadows",
        "Warm Cozy": "warmer temperature, inviting tone, soft lighting, cozy staging",
    }
    style_phrase = style_phrases.get(style, "balanced, realistic, tasteful staging")

    system_prompt = (
        "You write concise, production-ready image enhancement prompts for real estate photos. "
        "Only use the provided inputs. Do not invent property details."
    )
    user_prompt = (
        "Create one enhancement prompt. Requirements:\n"
        "- Must include: lighting correction, color optimization, declutter, staging improvements.\n"
        "- Do NOT alter architecture, add fake windows, or change room layout drastically.\n"
        f"- Style direction: {style_phrase}.\n"
        f"- Listing context: {listing_description or 'No listing description provided.'}\n"
        f"- Room type hint: {room_type_hint or 'none'}\n"
        "Return only the final prompt as plain text."
    )

    response = client.chat.completions.create(
        model=DEFAULT_LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def mock_fetch_community(zipcode: str) -> dict:
    data = {
        "95112": {
            "summary": "Urban neighborhood with mixed residential and commercial blocks.",
            "highlights": [
                "Walkable streets and local shops",
                "Access to transit corridors",
                "Active neighborhood associations",
            ],
        }
    }
    entry = data.get(
        zipcode,
        {
            "summary": "General community profile for the area.",
            "highlights": ["Local amenities nearby", "Mixed housing types", "Community events"],
        },
    )
    return {
        "summary": entry["summary"],
        "highlights": entry["highlights"],
        "source": "mock_community_dataset_v1",
        "updated_at": "2026-01-01",
    }


def mock_fetch_climate(zipcode: str) -> dict:
    data = {
        "95112": {
            "summary": "Mild climate with warm summers and cool winters.",
            "highlights": [
                "Warm summer afternoons",
                "Cool evenings in winter",
                "Low annual snowfall",
            ],
        }
    }
    entry = data.get(
        zipcode,
        {
            "summary": "Typical regional climate patterns.",
            "highlights": ["Seasonal temperature variation", "Occasional rain", "Moderate humidity"],
        },
    )
    return {
        "summary": entry["summary"],
        "highlights": entry["highlights"],
        "source": "mock_climate_dataset_v1",
        "updated_at": "2026-01-01",
    }


def mock_fetch_schools(zipcode: str) -> dict:
    data = {
        "95112": {
            "summary": "Schools show mixed performance with a range of programs.",
            "highlights": [
                "Varied academic outcomes across schools",
                "STEM and arts programs available",
                "Some schools within walking distance",
            ],
        }
    }
    entry = data.get(
        zipcode,
        {
            "summary": "School options vary by zone.",
            "highlights": ["Public and private options", "Enrollment varies", "Program availability differs"],
        },
    )
    return {
        "summary": entry["summary"],
        "highlights": entry["highlights"],
        "source": "mock_school_dataset_v1",
        "updated_at": "2026-01-01",
    }


def mock_fetch_crime(zipcode: str) -> dict:
    data = {
        "95112": {
            "summary": "Crime levels are moderate relative to nearby areas.",
            "risk_level": "Medium",
            "highlights": [
                "Property incidents are the most common",
                "Police presence around transit hubs",
                "Neighborhood watch activity reported",
            ],
        }
    }
    entry = data.get(
        zipcode,
        {
            "summary": "Crime profile varies within the area.",
            "risk_level": "Medium",
            "highlights": [
                "Mixed incident types reported",
                "Some streets are quieter than others",
                "Local safety initiatives exist",
            ],
        },
    )
    return {
        "summary": entry["summary"],
        "risk_level": entry["risk_level"],
        "highlights": entry["highlights"],
        "source": "mock_crime_dataset_v1",
        "updated_at": "2026-01-01",
    }


def fetch_zipcode_insights(zipcode: str) -> dict:
    return {
        "community": mock_fetch_community(zipcode),
        "climate": mock_fetch_climate(zipcode),
        "schools": mock_fetch_schools(zipcode),
        "crime": mock_fetch_crime(zipcode),
    }


def _style_suggested_edits(style: str) -> List[str]:
    edits = {
        "Modern Neutral": [
            "Use neutral color balance and clean whites",
            "Keep decor minimal and modern",
        ],
        "Luxury": [
            "Enhance material richness and balanced contrast",
            "Polish finishes for a premium look",
        ],
        "Bright Daytime": [
            "Increase exposure for a daylight feel",
            "Preserve natural shadows and crisp whites",
        ],
        "Warm Cozy": [
            "Warm the color temperature slightly",
            "Use soft lighting for an inviting tone",
        ],
    }
    return edits.get(style, ["Maintain a balanced, realistic presentation"])


def _room_suggested_edits(room_type_hint: Optional[str]) -> List[str]:
    if not room_type_hint:
        return ["Refine staging appropriate for the room"]
    room_map = {
        "living_room": "Align furniture, clear cluttered surfaces",
        "kitchen": "Clear counters, enhance appliance finish",
        "bedroom": "Straighten bedding, soften lighting",
        "bathroom": "Polish fixtures, clean mirror reflections",
        "dining_room": "Neaten table setting, balance lighting",
    }
    suggestion = room_map.get(room_type_hint, "Refine staging appropriate for the room")
    return [suggestion]


def build_brief(
    listing_description: str, zipcode_insights: dict, image_enhance_plan: List[dict]
) -> dict:
    highlights: List[str] = []
    if listing_description:
        highlights.append(f"Listing description: {listing_description}")
    highlights.append(f"Planned image enhancements for {len(image_enhance_plan)} photos")
    highlights.append(f"Community: {zipcode_insights['community']['summary']}")
    highlights.append(f"Climate: {zipcode_insights['climate']['summary']}")
    highlights.append(f"Schools: {zipcode_insights['schools']['summary']}")

    risk_flags: List[str] = []
    crime_risk = zipcode_insights["crime"]["risk_level"]
    if crime_risk in {"Medium", "High"}:
        risk_flags.append(f"Crime risk level reported as {crime_risk}")

    school_text = " ".join(zipcode_insights["schools"]["highlights"]).lower()
    if any(keyword in school_text for keyword in ["varied", "mixed", "uneven"]):
        risk_flags.append("School performance appears variable across zones")

    climate_text = " ".join(zipcode_insights["climate"]["highlights"]).lower()
    if any(keyword in climate_text for keyword in ["heat", "hot", "storm", "flood", "snow"]):
        risk_flags.append("Climate notes include seasonal extremes or events")

    if not listing_description:
        risk_flags.append("Listing description is missing or minimal")
    if not image_enhance_plan:
        risk_flags.append("No image enhancement plan generated")

    confidence_notes = [
        "Zipcode insights are mock data and should be verified with local sources",
        "Image enhancement suggestions are stylistic guidelines, not executed edits",
    ]

    image_plan_lines = [
        f"- {item['image_id']}: {item['room_type_hint'] or 'unspecified room'}"
        for item in image_enhance_plan
    ]
    image_markdown_blocks = [
        "\n".join(
            [
                f"**{item['image_id']}** ({item['room_type_hint'] or 'unspecified room'})",
                f"Original: ![]({item['original_url']})",
                f"Enhanced (mock): ![]({item['mock_enhanced_url']})",
            ]
        )
        for item in image_enhance_plan
    ]

    client = _get_openai_client()
    system_prompt = (
        "You are a senior real estate analyst. Produce a professional Markdown report. "
        "Use only the provided data. Do not invent facts."
    )
    user_payload = {
        "listing_description": listing_description,
        "zipcode_insights": zipcode_insights,
        "image_enhance_plan": image_enhance_plan,
        "image_plan_lines": image_plan_lines,
        "image_markdown_blocks": image_markdown_blocks,
        "risk_flags": risk_flags,
    }
    user_prompt = (
        "Create a Markdown report with these sections, in order:\n"
        "Overview\n"
        "Image Enhancement Plan\n"
        "Images\n"
        "Community\n"
        "Climate\n"
        "Schools\n"
        "Crime & Safety\n"
        "Risks / What to Verify\n\n"
        "Rules:\n"
        "- Use ONLY the provided data.\n"
        "- Keep it concise and professional.\n"
        "- For Images, use the provided image_markdown_blocks verbatim.\n"
        "- For Image Enhancement Plan, use image_plan_lines verbatim as bullets.\n"
        "- For Risks, use risk_flags; if empty, say no specific risks identified.\n\n"
        f"Data:\n{json.dumps(user_payload, indent=2)}"
    )

    response = client.chat.completions.create(
        model=DEFAULT_LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    narrative_markdown = response.choices[0].message.content.strip()

    return {
        "highlights": highlights[:5],
        "risk_flags": risk_flags,
        "confidence_notes": confidence_notes,
        "narrative_markdown": narrative_markdown,
    }


def generate_property_brief(
    images: List[dict],
    style: str,
    listing_description: str,
    zipcode: str,
) -> dict:
    room_types = [img.get("room_type_hint") for img in images if img.get("room_type_hint")]
    room_hint = ", ".join(sorted(set(room_types))) if room_types else None

    enhancement_prompt = build_enhancement_prompt(style, listing_description, room_hint)

    image_enhance_plan: List[dict] = []
    for image in images:
        room_type_hint = image.get("room_type_hint")
        suggested_edits = [
            "Correct lighting and exposure",
            "Optimize color balance",
            "Declutter visible surfaces",
            "Refine staging for the room",
        ]
        suggested_edits.extend(_style_suggested_edits(style))
        suggested_edits.extend(_room_suggested_edits(room_type_hint))

        image_enhance_plan.append(
            {
                "image_id": image.get("image_id", ""),
                "original_url": image.get("url", ""),
                "room_type_hint": room_type_hint,
                "suggested_edits": suggested_edits,
                "mock_enhanced_url": f"https://example.com/enhanced/{image.get('image_id','')}.jpg",
            }
        )

    zipcode_insights = fetch_zipcode_insights(zipcode)
    brief = build_brief(listing_description, zipcode_insights, image_enhance_plan)

    return {
        "enhancement_prompt": enhancement_prompt,
        "image_enhance_plan": image_enhance_plan,
        "zipcode_insights": zipcode_insights,
        "brief": brief,
    }


if __name__ == "__main__":
    images = [
        {
            "image_id": "img_1",
            "url": "https://example.com/living.jpg",
            "room_type_hint": "living_room",
        },
        {
            "image_id": "img_2",
            "url": "https://example.com/kitchen.jpg",
            "room_type_hint": "kitchen",
        },
    ]
    style = "Modern Neutral"
    listing_description = (
        "Bright open layout, renovated kitchen, large windows, good natural light."
    )
    zipcode = "95112"

    result = generate_property_brief(images, style, listing_description, zipcode)
    print(result["brief"]["narrative_markdown"])
    print("\n---\n")
    print(json.dumps(result, indent=2))
