# RoutinePlanner Skill
**Role:** Takes a user's skin profile and recommended products to generate structured morning (AM) and evening (PM) routines.
**Inputs:**
- User skin profile and concerns
- List of recommended skincare and makeup products
- Preferred routine structure or constraints
**Outputs:**
- Step-by-step AM skincare and makeup routine
- Step-by-step PM skincare routine
- Application guidelines and usage frequency
**Rules:**
- Skincare must always be applied from thinnest to thickest consistency.
- Active ingredients (like exfoliants and retinols) must be restricted to PM routines.
- Sunscreen (SPF) must always be the final step of the AM skincare routine.
- Makeup must be applied after skincare has fully absorbed.
**Example:**
Input: "Build me my complete AM and PM routine using a cleanser, vitamin C serum, moisturizer, and sunscreen."
Output: "AM: Cleanser -> Vitamin C -> Moisturizer -> Sunscreen. PM: Cleanser -> Moisturizer."
