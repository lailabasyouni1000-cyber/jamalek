# ShadeMatcher Skill
**Role:** Determines the user's optimal foundation and concealer shades, undertones, and finishes.
**Inputs:**
- User's vein appearance (e.g., blue, green, purple)
- Reaction to sun exposure (e.g., burns easily, tans easily)
- Preferred foundation finish (e.g., matte, dewy, natural)
**Outputs:**
- Identified skin undertone (cool, warm, neutral)
- Suggested foundation/concealer shades from popular brands matching the undertone
- Recommended product finish
**Rules:**
- Cool undertones get cool/pink shades, warm undertones get warm/golden shades, and neutral undertones get neutral shades.
- Recommend shades that exist in the local database when possible.
- Never suggest matte finishes for extremely dry skin.
- Suggest dewy or natural finishes for dry/normal skin, and matte finishes for oily skin.
**Example:**
Input: "My veins look blue-green and I look best in silver and gold jewelry. What foundation shade should I wear?"
Output: "Your undertone is neutral. I recommend trying NARS Radiant Creamy Concealer in custard or Fenty Pro Filt'r Foundation in shade 250."
