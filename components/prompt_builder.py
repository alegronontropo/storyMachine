import time
import json
from .utils import summarize_characters

def build_prompt(db, chapter_id, layer_config=None):
    """Builds a compact hierarchical prompt from DB for a chapter.

    layer_config: dict of weights for layers (0-100)
    returns: (system_msg, user_msg, metadata)
    """
    if layer_config is None:
        layer_config = {}

    # defaults
    lw = {k: layer_config.get(k, 100) for k in [
        'system', 'world', 'style', 'scene', 'location', 'characters'
    ]}

    chapters = db.get('chapters', [])
    chapter = next((c for c in chapters if c.get('id') == chapter_id), None)
    if not chapter:
        chapter = {"name": "unknown", "beats": "", "chapter_goal": ""}

    # System (stable persona)
    system_msg = "You are a professional fiction writer. Produce dramatic, scene-focused prose."

    # World summary (very short)
    world = db.get('world', {})
    world_ctx = ""
    if world and lw['world'] > 0:
        world_ctx = f"World: {world.get('world_name','')}; Year: {world.get('year','')}; Rules: {world.get('tech_magic','') or 'N/A'}."

    # Style (reference by name)
    style = chapter.get('selected_style') or db.get('default_style') or "ללא"
    style_ctx = f"Style: {style}." if lw['style'] > 0 else ""

    # Scene directives
    scene_ctx = ""
    if lw['scene'] > 0:
        scene_ctx = f"Chapter: {chapter.get('name','')}. Goal: {chapter.get('chapter_goal','')}. Beats: {chapter.get('beats','')}."

    # Location
    location_ctx = ""
    if lw['location'] > 0 and chapter.get('location') and chapter.get('location') != 'כללי':
        locs = db.get('locations', {})
        loc = locs.get(chapter.get('location'), {})
        location_ctx = f"Location: {chapter.get('location')}. {loc.get('general_desc','')[:250]}"

    # Characters summary (compact)
    characters_ctx = ""
    if lw['characters'] > 0:
        chars = chapter.get('characters', [])
        characters_ctx = summarize_characters(db.get('characters', {}), chars)

    # Compose user message with only active segments
    parts = []
    if world_ctx: parts.append(world_ctx)
    if style_ctx: parts.append(style_ctx)
    if scene_ctx: parts.append(scene_ctx)
    if location_ctx: parts.append(location_ctx)
    if characters_ctx: parts.append(f"Characters: {characters_ctx}")

    user_msg = "\n\n".join(parts)

    metadata = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "chapter_id": chapter_id,
        "weights": lw,
        "parts_count": len(parts)
    }

    return system_msg, user_msg, metadata
