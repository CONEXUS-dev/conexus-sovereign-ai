# Vargas Memory Schemas

## Collections

### vargas_identity
Explicit user facts — name, story, preferences, corrections.
- `content`: The memory text
- `category`: e.g. "name", "preference", "story", "correction"
- `confidence`: 0.0–1.0
- `created_at`: ISO timestamp
- `corrected_at`: ISO timestamp (if corrected)
- `emoji_vector_id`: Optional linked emoji vector

### vargas_behavioral
Engagement patterns — decision tendencies, pressure tolerance, communication style.
- `content`: The memory text
- `pattern_type`: e.g. "decision_style", "pressure_response", "communication_preference"
- `frequency`: How often this pattern has been observed
- `confidence`: 0.0–1.0
- `created_at`: ISO timestamp
- `emoji_vector_id`: Optional linked emoji vector

### vargas_attunement
Tone, cadence, emotional calibration — how to be with the user.
- `content`: The memory text
- `attunement_type`: e.g. "tone_preference", "cadence_preference", "challenge_tolerance", "silence_comfort"
- `confidence`: 0.0–1.0
- `created_at`: ISO timestamp
- `emoji_vector_id`: Optional linked emoji vector

## Rules

- Memory informs posture, never narrates identity
- Memory is always corrigible — the user can correct or erase anything
- Memory never surfaces in output unless explicitly requested
- Emoji vectors operate latently as calibration substrate
- All writes are logged to `logs/memory_writes.log`
