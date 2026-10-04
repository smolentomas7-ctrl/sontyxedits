# Realm Breach — Character & Object Bible (LOCKED)

These specs are locked. Every shot builds characters through the same code
(`scenes/lib/rb_warrior.py`, `rb_god.py`, `rb_enemies.py`) so nothing is
redesigned between shots. Units: metres. Characters face −Y, Z is up.

---

## THE WARRIOR — "the Breach Runner"

| Attribute | Locked value |
|---|---|
| Height | 1.90 m to helm crest. Broad shoulders (≈0.62 m across pauldrons), heavy and grounded, slightly forward stance |
| Build | Rigid plate pieces parented to an FK armature (real plate armour does not deform). Chainmail and leather under-layer bridge the joints |
| Armour | Blackened steel plate over chainmail and dark leather. Edges worn to bare metal (vertex-baked convexity mask), soot, dried mud on lower legs, dents (seeded displacement) |
| Cuirass | Medial-ridged breastplate + backplate, gorget at the neck, 3 lames of faulds at the waist, two 3-lame tassets over the thighs |
| Pauldrons | Layered: dome + 4 descending lames. **Left is larger (×1.18) with a cracked, notched rolled rim**; right is standard |
| Arms | Rerebrace tubes, cupped couters with side wings, tapered vambraces |
| Gauntlets | Flared cuff, back-of-hand plate, segmented finger lames (3 per finger), thumb plate |
| Legs | Cuisses, cupped poleyns with wings, calf-shaped greaves, 5-lame sabatons |
| Helmet | Closed great helm, flat-topped with a vertical front ridge, **narrow T-shaped visor slit** (horizontal eye slit + vertical breath slit), rivet band. Two ember eyes (#FF6A1A) glow inside the slit, with an internal ember point light. Close-ups of "his eyes" are close-ups of this slit |
| Cape | Long, tattered crimson-black (#3A0607 → #120203) heavy wool, hangs from under the pauldrons to the calves, torn hem (seeded jagged lengths + alpha-clipped holes). Bone-chain driven with procedural follow-through/sway (deterministic, no sim) |
| Weapon | **Greatsword**, black steel, 1.75 m overall (blade 1.38 m), diamond section with fuller, curved crossguard, leather grip, wheel pommel. A thin ember-orange crack runs along the blade; its glow is a keyed property (`crack_glow`) that rises when he attacks. **Always in his right hand** |
| Rings | From Phase 4 on only: 4 Great Rings on the **left** gauntlet's fingers, each softly glowing (mythic red, morbidious green, god white-gold, fallen-equip blue). None before Phase 4 |
| Abilities | Q Fireball = orange-red fire. E Lightning = white-blue forks. R God Attack = golden-white blast (#FFE9A8 → white) |
| Motion | Slow, heavy, deliberate, unstoppable. 6–8 frame anticipation before every swing, cape follow-through |
| Poses | walk, stop, stand, raise sword, point sword, charge, swing, clash, block, fall, kneel, rise, cast, god attack, exhausted stand, walk away |

### Early look (Phase 1 only)
Plain worn grey iron (lighter grey, rougher, no blackening), simple single-dome
pauldrons, **leather hood** over an open iron skullcap (face lost in hood
shadow), **plain short sword** (0.9 m), **no cape, no rings, no glow**.

---

## THE FALLEN GOD

| Attribute | Locked value |
|---|---|
| Height | 5.70 m (3× the warrior) |
| Body | Cracked pale stone (#B9B4AA, rough, chipped), black void visible through the cracks; cold blue light (#6FA8FF) leaks from cracks and eyes. Crack glow ignites bottom→top on a keyed `ignite` height |
| Head | Statue-like stern face (deep eye sockets, heavy brow, straight nose, closed mouth), cracked; eyes are blue-white emissive |
| Halo | Broken halo ring floating behind the head: three arcs with jagged gaps, blue-white emissive, slow rotation. Shattered in the ending |
| Robes | Long tattered dark robes (#0E1116 → #1B2230), open at the chest to show cracked stone, ragged hem dragging on the floor |
| Weapon | Massive two-handed obsidian blade (≈4.3 m), faceted volcanic glass, near-black, glossy, faint blue edge glow |
| Camera | Always shot from a low angle until he falls |
| Motion | Still, slow, monumental; every move feels inevitable |

---

## ENEMIES (one silhouette + one glow each)

| Enemy | Silhouette | Glow |
|---|---|---|
| Skeleton | Gaunt human skeleton, rusted blade, tattered loincloth | Bone white body, ember eye sockets (#FF6A1A) |
| Ghost | Hooded, legless wraith with trailing wisps and long clawed hands | Translucent pale blue (#9CC8FF) |
| Bad angel | Gaunt humanoid with black, broken feathered wings, cracked halo | Red (#FF2A2A) eyes and halo |
| Evil | Tall horned shadow, smoke-edged, hunched | Purple (#A04DFF) eyes and chest core |
| Morbidious | Bloated, hulking mass with pustules and a small head | Toxic green (#6BFF4A) pustules |

---

## LOOT & UI OBJECTS

- **Loot drop**: a weapon/ring silhouette on the floor inside a vertical light pillar of its rarity colour:
  common #9A9A9A · rare #3D7BFF · epic #A04DFF · mythic #FF3B3B · legendary #FF9A1A · morbidious #6BFF4A · god #FFE9A8 · fallen equip #1B2A4A body with #6FA8FF glow.
- **Life orbs**: three ember-red glass orbs (#FF3B3B core) in a small iron frame; a lost life goes dark (glass stays, core dies to smoke).
- **REBIRTH button**: carved obsidian plaque, "REBIRTH" in Cinzel, ember-gold glow pulse.

## TYPOGRAPHY
Cinzel (SIL Open Font License 1.1), off-white #EDE6DA, tracking +18%, faint
ember glow. Used only for "FLOOR" numbers, the title and the final line.
