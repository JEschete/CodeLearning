# Implemented Changes

This document records player-facing changes present on `main` compared with the clean AzerothCore baseline in `upstream-sync`.

For current access paths, verification commands, per-feature playtests, and the
Ledger requirement coverage matrix, see `doc/ImplementedSystemsTestCompendium.md`.

## Progression and World Rules

### Dynamic Quest Scaling

- Quests display at the player's current level in gossip, quest lists, and the quest log. - Validated through playtest.
- Cached quest levels are refreshed when the player levels so quest colors remain current.  - Validated through playtest.
- Quest XP is calculated from the player's level rather than the quest template's static level.  - Validated through playtest.

### Expanded Professions

- The primary profession cap is raised from 2 to 12 by default.  - Validated through playtest.
- Learning costs scale upward as additional primary professions are acquired.  - Validated through playtest.
- Trainer prices and requirements refresh immediately after a profession is learned.  - Validated through playtest.
- The profession-point confirmation popup with hardcoded two-profession wording is suppressed.  - Validated through playtest.
- Merissa Stilwell is a Jack of All Trades trainer.  - Validated through playtest.
- The rare world-drop Profession Charter: Masterwork Seal grants one primary profession for free. - I've spawned the item, but never seen it drop. 
- The owner's Perky Pug opens a combined native profession trainer with normal costs and skill requirements.  - Validated through playtest.

### Challenge Modes

- Shrines of Challenge allow opt-in challenge selection and provide persistent visible status auras. - Validated through playtest.
- Implemented modes are Hardcore, Semi-Hardcore, Self-Crafted, Low-Quality Gear, Slow XP, Very Slow XP, Quest XP Only, and Iron Man. - Validated through playtest.
- A mode can be entered only at level 1, or level 55 for a Death Knight. An active mode can be left later at a shrine. - Validated through playtest.
- Slow XP and Very Slow XP award 50% and 25% experience respectively. Other mode rewards are configurable and empty by default. - Validated through playtest.

### Open-World Difficulty

- Open-world creatures scale toward the nearby reference player's level, lagging by 3 levels while remaining in the green difficulty band. - Validated through playtest.
- All creature ranks use the same defaults: 1.5x health, 1.25x melee damage, spell damage, healing, and mana, 1.135x armor, and 0.9x attack time. - Validated through playtest.
- Nearby creatures are refreshed every 3 seconds within 80 yards while out of combat. Level scaling is capped by the server maximum level rather than each creature template's original maximum. - Validated through playtest.

### Adventure Mode

- Adventure Mode is an independent, per-character solo ruleset selected at Shrines of Adventure in each starting area. - Validated through playtest, shrine placement in northshire is suspect. Others need to be validated. 
- By default, open-world outgoing damage is 60%, creature health is 150%, physical damage taken is 200%, spell damage taken is 150%, and healing done is 85%. - Validated through playtest.
- Kill XP is 50% and quest or other victimless XP is 200% by default. LFG, battleground, and arena queues are disabled while the mode is active. - Validated through playtest.
- Configurable level milestones can award titles, bonus talent points, items, and achievements. The shipped configuration grants three bonus talent points per level and milestone items from levels 10 through 80. - Validated through playtest.
- Existing characters import their former Challenge Mode selection once; the standalone module has no dependency on `mod-challenge-modes`. - Validated through playtest.

### Gathering Respawns

- Dynamic game-object respawn scaling is restricted to Mining and Herbalism gathering nodes, preventing unrelated objects from receiving accelerated respawns.

### Auto-Gather

- Every second, the player can automatically gather one nearby Mining or Herbalism node and skin one eligible corpse within 10 yards. - Validated through playtest.
- Auto-gathering works while mounted but not while flying, in a vehicle, casting, crowd-controlled, or in combat by default. - Validated through playtest.
- Required profession and skill checks still apply. A source is left intact when its loot cannot fit in the player's bags. - Validated through playtest.

### Profession Experience

- Gathering, crafting, fishing, cooking, First Aid, disenchanting, prospecting, milling, and lockpicking can award character experience. - Validated through playtest.
- The active values award 0.8% of the next character level per supported profession action, modified by recipe difficulty: grey 0%, green 75%, yellow 100%, and orange 125%. - Validated through playtest.
- Repeating the same action within 60 seconds reduces its XP by 15% per repetition to a 10% floor. - Validated through playtest.
- The active required-skill curve multiplier is 2.5x. - Validated through playtest.

### Solo Profession Skill Rates

- Successful crafting and supported gathering skill-ups grant 2x skill by default; failed core skill rolls still grant nothing. - Validated through playtest.
- Multiplication uses deterministic half-up rounding and a configurable cap of 10 skill points per action, with a hard cap of 50. - Validated through playtest.
- Profession-specific overrides are available. Fishing, resource quantity, and reagent storage are unchanged.

### Solo Gathering Yields

- Successful Herbalism, Mining, Skinning, and Fishing entries grant 2x resource quantity by default without changing native drop chances. - Validated through playtest.
- Generic chests and non-gathering loot stores are excluded; Mining and Herbalism require an exact lock-skill match on the source node. - Validated through playtest.
- Quest-needed entries are excluded by default, and extra count rolls have configurable and compile-time caps. - Validated through playtest.
- AutoGather preserves node/corpse provenance so it receives the same conservative classification as manual gathering. - Validated through playtest.

## Items and Affixes

### Random Item Enchants

- Newly stored poor through legendary weapons and armor can receive class-aware random stat affixes from world, crafted, dungeon, and raid sources. - Validated through playtest.
- Affix strength scales across 15 item-level brackets. - Validated through playtest.
- Quality caps are 1/2/3/4/5/5 affixes for poor/normal/uncommon/rare/epic/legendary items. - Validated through playtest.
- Stat pools account for class roles, including hybrid classes. - Validated through playtest.
- Existing property enchants are preserved instead of overwritten. Native ItemSet pieces receive at most two random stats by default.
- Top-bracket affixes work for everyone. The item level 300+ Haste, Hit, Dodge and Parry rolls used Jewelcrafting-350 gem enchantments and the 161-200 Haste roll used an Enchanting-400 one; `Player::ApplyEnchantment` returns early when the wearer lacks the skill, so the best random affixes in the game silently granted nothing to any character without that profession. Ungated equivalents `61100-61103` replace them, and `+16 Haste` moves to stock 3463.
- One stat per item, across every roll rather than within one. The roll hook fires on every store, so an item that kept empty affix slots was rolled again when it was mailed, traded or bought, and the second pass could place a stat the first had already applied; the copies then stacked. The used-stat set is now seeded from the affixes already on the item.
- Random bracket variance can move down one tier but never above the item's base item-level bracket.

### Arcane Affix Artificer

- Characters with at least 75 Enchanting can manually apply learned affixes to equipped or bagged weapons and armor. - Validated through playtest.
- Each stat has a submenu containing all 15 ranks. Individual ranks are permanently learned and gated by both Enchanting skill and player level.
- Learning costs scale with player level and increase by rank; application costs scale with item level and quality. - Validated through playtest.
- Any learned eligible rank can be selected when applying an affix; the system no longer silently substitutes only the current maximum rank. - Validated through playtest.
- Critical Strike affixes raise spell and ranged critical strike, not only melee. Ranks 1 and 2 used a stock enchant carrying `ITEM_MOD_CRIT_MELEE_RATING` rather than `ITEM_MOD_CRIT_RATING`, so a caster who bought "+2 Critical Strike" moved only their melee crit and the tooltip, which takes its name from the DBC, never said so. Rank 1 is now +2 and rank 2 is +3, both school-neutral. The same substitution is made in the random-affix brackets for item levels 1-40, which shared the entry.
- All fifteen ranks of every stat are distinct, and none of them can be inert. The ladder was built entirely from stock `SpellItemEnchantment` rows, which cannot supply fifteen distinct ungated values for every rating, and it broke in three ways at once: Critical Strike ranks 1-2 granted melee crit only; six stats had adjacent ranks sharing one enchantment, so a paid rank-up changed nothing and an item on any of them resolved to the lowest; and rank 15 of Haste, Hit, Dodge and Parry used Jewelcrafting-350 gem enchantments while Haste ranks 9-10 used an Enchanting-400 one, granting nothing at all to a character without that profession. The gaps are now filled by module-owned enchantments `61000-61031`, carried to the client by the merged patch so tooltips resolve. Worldserver audits the whole ladder at startup and names any rank that is duplicated, gated, or grants a stat other than its column's.
- The rank already sitting in the chosen slot is shown as "(already on this slot)" and cannot be bought again. Re-applying it removed the enchantment and put back an identical one, so the stat did not move while the application fee was still charged. The menu hides the row and the apply path refuses it before any money changes hands, because the menu the client answers from can be a page older than the item.
- Up to five affixes can coexist. When all slots are occupied, the player chooses which affix to replace. - Validated through playtest.
- The Arcane Affix Artificer NPC and portable Artificer's Codex expose the same interface. - Validated through playtest.
- Add, replacement, and upgrade share the same item-level rank ceiling. Existing affixes upgrade one learned rank at a time; the default price starts at 200% of normal application and increases by that base amount per destination tier.

### Gambler

- Veyra Chance appears in all eight faction capitals, Shattrath, and Dalaran with 15 concrete equipment targets from Head through Trinket.
- Pools are curated from real loot, vendor, quest-reward, and custom-loot references, with explicit inclusion/exclusion/weight overrides. Structural, proficiency, armor-family, level, budget, bag, and vendor-loop checks still run before charging.
- Costs scale at 1x/2x/3x by target family. Pity persists per character and concrete target and resets only when that target receives an item-level upgrade.

### Extracted Item Powers

- A generated all-era catalog exposes 2,195 non-stat item abilities from Classic, Burning Crusade, Wrath, all level ranges, and custom module items. Only gear the player can wear is extractable, plus glyphs; recipes, consumables, keys and quest tokens are excluded even when they carry a triggered spell. Exact source abilities are learned by sacrificing the bagged source item at Power Curators in ten hubs.
- Supported native semantics include use, equip, chance-on-hit, soulstone-style use, on-obtain, and learn-spell bundles. Application chooses player-level or destination-item-level scaling while preserving native targeting, cooldown/category, and proc chance/PPM behavior.
- Extracted abilities may occupy any of the five random-property slots, so one item can carry several. The player picks the target slot and confirms before replacing an affix or another power, and there is no cap on how many powered items may be equipped. Stable generated markers and live strict-catalog validation catch source drift.

### Source Armor Sets

- A deterministic generator produces 609 eight-piece sets and 4,872 collectible pieces across 66 reviewed world zones, 64 LFG-authored dungeon identities, and 23 raids. Sources normally emit cloth, leather, mail, and plate; the Death Knight-only Scarlet Enclave emits only plate. Its 24 retired item IDs remain as inert compatibility templates so existing copies and Reliquary destinations are not orphaned.
- Non-gray world kills can roll the local set; native dungeon/raid bosses use map, level, and stable creature routing so shared-map wings remain distinct. Bonus Drops owns eligibility and Custom Loot Tables owns grouped selection.
- Every two/four threshold has a unique bounded program. The 1,218 programs combine reachable triggers, predicates, state models, two canonical actions, and meaningful target selection; structural and constants-inclusive hashes are globally unique.
- The Scarlet Enclave plate set is now Ebon Initiate's Battlegear and is class-restricted to Death Knights. Qualifying Humanoid, Undead, and Demon kills raise independent AI ghouls: one for 10 minutes with two pieces (cap 10), or two for 30 minutes with four pieces (cap 20). Ghoul kills intentionally chain, while assist-only targeting prevents independent pulls and lifecycle hooks clean the army on death, logout, map change, opt-out, or threshold loss. Completing The Light of Dawn (`12801`) registers all eight pieces with the Curator at once, with login backfill for existing Death Knights.

### Source Armor Sets: Eastern Kingdoms Authoring

- `doc/SetBonusFix.md` is authored zone-by-zone into `mod-source-item-sets`, replacing the random VM-generated bonus for that zone's four sets with the doc's actual name and 2/4-piece text. **Eastern Kingdoms (25 zones), Outland (7 zones), and Northrend (9 zones) are complete — 41 zones, 164 authored sets.** Kalimdor and the 64 dungeons are queued for later passes and still carry generated bonuses.
- Ninety-seven bonuses were reworded in `doc/SetBonusFix.md` with explicit approval (33 in Eastern Kingdoms, 27 in Outland, 37 in Northrend), each because it named a mechanic this client and core cannot express. They fall into four groups. **Cast-time and foreign-spell scaling** ("Mining a vein is 50% faster", "Leatherworking crafts complete instantly", "Well Fed lasts twice as long", "Potions are 25% more effective"): WotLK's spell-modifier system works through spell-family masks, and gathering, crafting, and consumable spells are `SPELLFAMILY_GENERIC` with no mask to hook. **Absent creature types**: "Aberrations" arrives in a later expansion. **Absent auras and hooks**: no aura modifies spell range, `PROC_HIT_INTERRUPT` is inert in this core and nothing reports an interrupt, and no aura mitigates by attacker creature type for anyone but the wearer. **Absent detection**: standing in fire or lava, line-shaped area damage, and closing distance on a target have no primitive behind them. Each reworded bonus keeps its zone's profession or combat identity; the rewrites move the effect onto gathering, crafting, loot, skill, or proc mechanics that the engine genuinely supports.
- Profession bonuses are backed by a gathering and crafting layer that reuses the seams `mod-solo-gathering-yields` already established: `GlobalScript::OnBeforeDropAddItem` for yields, classified by loot store and by the node's own Herbalism or Mining lock so an ordinary chest is never mistaken for a resource node, and `OnPlayerCreateItem` plus `OnPlayerUpdateCraftingSkill` for crafting, which fire only after an item is confirmed created so a failed craft never advances a counter.
- Gated proc triggers close the last structural gap in the proc tier. `spell_proc` can filter on hit result and damage school but knows nothing about creature types or how many enemies are nearby, so a proc may declare a gate; the generator then attaches `spell_source_set_gated_trigger` to that proc's trigger spell and the script re-checks the condition in `OnCheckCast` before the aura is allowed to land. This is what makes "critical strikes against Undead" and similar bonuses expressible without a core change, since no ScriptMgr hook carries critical-strike information.
- Two implementation choices are worth recording because the doc's wording does not map onto a stock mechanic one-for-one. "Cannot be dodged" (Prestor Houseguard) is delivered as a large temporary Expertise grant, which is the engine's own way of removing dodge, rather than a new combat-result flag. "Your next spell is instant" (Shattered Sun Invoker) is delivered as a 100% cast-speed charge; the accompanying damage half is exact.
- Authored bonuses come in three shapes. **Passive**: a real stock spell aura placed on the set's own equip spell, applied natively by AzerothCore's `ApplyEquipSpell` with zero runtime code. **Native proc**: a `spell_proc` row plus `SPELL_AURA_PROC_TRIGGER_SPELL` and a generated per-set trigger spell, so core's proc engine owns the trigger, hit filtering, and internal cooldown — this is what makes on-dodge, on-parry, on-block, and on-crit bonuses possible at all, since none of those outcomes fire a ScriptMgr hook. **Scripted**: the hand-written `AuthoredEffect` dispatch in `SourceSetPrograms.cpp`, reserved for what the first two cannot express.
- Scripted effects are written as parameterized families reused across zones rather than one bespoke case per set: creature-type damage/mitigation/kill payoffs, target-health-gated amplification, threshold-held auras (health or power), corpse and enemy-count proximity armor, consecutive-target ramps, positional (behind-target) amplification, low-health reactive shields and leech windows, and combat-state auras.
- The generator validates that every emitted row's value count matches its INSERT column list, and resolves aura durations from the client's own `SpellDuration.dbc` rather than hardcoded indices, so a missing duration fails generation instead of silently applying a permanent aura.
- Dun Morogh's two flagged design Notes were resolved rather than left ambiguous, and the doc text itself was left untouched (per the immutable-requirements rule): the Cloth 2-piece's "nearby enemies" slow is centered on the slain enemy with an 8-yard radius, matching the doc's dominant "within N yards" convention elsewhere; the Plate 2-piece is implemented as the Note's own suggested fix — 50% less Frost damage taken plus a 50%-shorter duration on snare effects applied to the wearer (`SPELL_AURA_MECHANIC_DURATION_MOD` on `MECHANIC_SNARE`), not the literal (contradictory) doc wording.
- A completed set's four armor-type lines in `doc/SetBonusFix.md` are marked `[Implemented]`; flavor, bonus, and Note text are never edited.

### Source Armor Sets: Kalimdor and Dungeon Authoring

- Authoring is complete: **124 of the document's 125 zone and dungeon entries, 496 of 500 sets.** Kalimdor added 19 zones / 76 sets; the dungeon pass added all 64 instances / 256 sets. Every remaining generated placeholder belongs to the 5 special world zones the document deliberately skipped and to the one entry named below; the sixth, the Scarlet Enclave, now has its separately approved Death Knight design.
- Dungeon sets key on `(source_kind=1, LFG dungeon id, armor subclass)`, not a zone id. The ids come from `LFGDungeons.dbc` through `load_sources`, so they are the same values the generated `mod_source_item_set_v2` rows already carry, and a set cannot be authored against a dungeon the generator does not emit.
- **The Headless Horseman is not implemented and cannot be without a decision.** The generator allows one source per map, and the Horseman's encounter shares map 189 with the four Scarlet Monastery wings, so no set exists for its four names to attach to. Authoring it means either a second source on a map that already carries four or special-casing the filter; both are design calls, so the entry is annotated in `SetBonusFix.md` and left alone.
- **Upper Blackrock Spire was added to the document rather than skipped.** The module generates a set for it that the original document never covered, so it would have been the one dungeon left with a random bonus. Its four names and eight bonuses were written to match the surrounding voice and are marked as added during implementation.
- A further 255 bonuses were reworded across Kalimdor and the dungeons on the same rule as the Eastern Kingdoms pass: the original named a mechanic this client and core cannot express. The dungeon rewrites cluster into groups the earlier pass did not hit. **Vehicle and mount combat** (the whole of The Oculus, plus jousting in Trial of the Champion): 3.3.5 vehicles cannot be driven from an item set. **Resurrection, transformation, and splitting** (Utgarde Keep, The Nexus, Culling of Stratholme, Forge of Souls): nothing reports that a creature has changed form or been raised. **Ally-targeted healing and interception** (Durnholde, Halls of Stone): no hook carries "damage dealt to an ally" to a third party. **Wave and objective counting** (Black Morass, Violet Hold): encounter progress is script-local and not visible to an item set. **Per-target internal cooldowns**: `spell_proc` holds one global cooldown per spell, never one per victim, so every "once every N sec per target" became a plain global cooldown.
- Three runtime families and two proc gates were added for this pass, each replacing what would have been several one-off handlers: `TickSwimmingAura` (an aura held while `IsInWater`), `LeaveCombatRepair` (a real `DurabilityRepairAll(false, 0.0f, false)` on the existing leave-combat hook, so the set pays the bill and no guild bank is touched), `TickLoneTargetAura` (the mirror of `TickEnemyCountAura`, holding an aura while *at most* N enemies are close, which is what duelling bosses reward), plus the `TargetCasting`, `TargetSummoned`, and `NoAlliesWithin` gates and the `Silenced`, `Slowed`, and `Summoned` target states. `TickArmorPerEnemy` was generalised to honour `AuraSpellId` so a crowd can now scale haste, spell power, attack power, or mitigation rather than only armor.
- Authoring is verified mechanically rather than by eye: a checker confirms all 256 dungeon set names match `SetBonusFix.md` exactly, that all 512 dungeon program rows carry a real `authored_effect` rather than 0, and that the `AuthoredEffect` ordinals in `SourceSetPrograms.cpp` agree one-for-one with the `AUTHORED_*` constants in the generator.

### Source Armor Sets: Eight Slots Per Set

- Every active set is **eight pieces instead of four** — head, shoulders, chest, wrists, hands, waist, legs, and feet. The initial expansion reached 4,896 pieces; retiring three unreachable Scarlet armor families leaves 4,872 collectible pieces while retaining their 24 old IDs as itemset-free compatibility templates. Thresholds stay at 2 and 4, so the extra slots add places to wear a set rather than extra power.
- `MAX_ITEM_SET_ITEMS` is 10 in this core and `itemset_dbc` already carried `ItemID_1` through `ItemID_12`, so eight fits natively with no core patch. `ItemSet.dbc` field 18 is `itemId[0]` and the array runs to field 27, so the client-patch records simply extend from fields 18-21 to 18-25.
- **The four original pieces keep their original item ids.** Slots 4-7 are allocated from a second band per source kind (`EXTENSION_ITEM_BASES`) rather than by widening the original stride. Widening it would have renumbered almost every one of the 2,448 existing items and orphaned any piece already sitting in a player's bags, bank, or mail. The new bands sit above each kind's original range, below the next kind's, and inside the 930000-1499999 window the generated SQL deletes, so a regenerate still cleans up after itself.
- Donor display ids, armor, and durability for the four new slots are real item-level 232 epics read out of `item_template`, so the eight pieces of a set sit on one armor curve. Leather wrists are the only derived value — no ilvl-232 leather bracer exists in the donors' display range, so its armor uses the family's wrist-to-chest ratio, which is 0.438 in all four armor classes.
- Loot needed no retuning. Pieces are emitted as `chance=0, group_id=1`, which is AzerothCore's equal-chance group roll: a group yields exactly one entry, so eight entries keep the drop *rate* identical and simply make each roll pick one of eight. A specific piece takes longer to find; completing any four of eight is faster.
- Two validators were added because the second id band makes a stride or base mistake possible: the generator now fails if any item id is duplicated, and fails if any lands outside the range its own SQL deletes.
- **One runtime change was needed after all.** `SourceSetPrograms.cpp` had a consistency assertion reading `itemToSet.size() != sets.size() * 4`. Nothing about piece loading assumes a count — the map is built from a plain query — but that check hardcoded four, so it began counting one rejection on every startup and would have `ABORT`ed the server outright under `StrictPrograms`. It now compares against a named `PiecesPerSet` that must track `PIECES_PER_SET` in the generator. Verified by boot: `loaded 612 sets, 1224 unique programs, and 4896 pieces (0 rejected)` with an empty `Errors.log`.

### Source Armor Sets: Per-Magnitude Support Spells

- Every support-spell buff tooltip read the wrong number. One spell is shared by many sets at different magnitudes -- 307017 backs 10%, 15% and 20% shields -- so its `Spell.dbc` row carries zero base points and the runtime supplies the real value through `SPELLVALUE_BASE_POINT0`. The client renders tooltips locally from the DBC and never sees that value, so all 61 support spells displayed `$s1` as **1** (`SpellInfo` adds one to the stored zero). Confirmed in game: Light's Ward read "Absorbs 1 to 0 damage" while the combat log showed `(39 Absorbed)` on a ~390 health mage, exactly the authored 10%.
- The generator now emits a clone of each support spell per magnitude it is actually used at -- 138 of them -- with the number written into the description and stored in `EffectBasePoints_1`. The variant id encodes the magnitude rather than an index, `VARIANT_SPELL_BASE + (support - 307000) * 1000 + magnitude`, so `TunedSpellFor()` in `SourceSetPrograms.cpp` derives it arithmetically. No lookup table, no new column, and no change to any program row.
- A missing variant falls back to the shared spell, so a gap is a cosmetic problem rather than a lost buff.
- **Two classes of value needed different treatment.** Where the applied amount *is* the tuning value (percent modifiers), the base spell's `$s1` is replaced with the number and the tooltip becomes exact. Where the amount is computed from the wearer -- absorbs and heals worth a share of maximum health -- no static number can be right, so those carry literal text instead ("Absorbs damage equal to 10% of your maximum health") and `ApplyTimedAura` takes an explicit `tuning` argument, because the applied 39 must not be what the tooltip looks up. Seven call sites pass it.
- **Light's Ward reapplied instantly when broken.** `TickLightShield` left its accumulator parked at the threshold once reached, so the tick after an enemy broke the shield put it straight back -- standing still was an unbreakable shield rather than one that has to be re-established. The accumulator now resets when the shield is applied, so renewing it costs another three seconds of standing still. The bonus text was corrected to match in both the generator and `SetBonusFix.md`.
- Absorb amounts cannot be shown on unit frames at all in 3.3.5. `UnitGetTotalAbsorbs()` arrives in 5.x and `SMSG_AURA_UPDATE` carries no effect values, which is the same reason the tooltip could not read the real number. No ElvUI build for this client can draw an absorb bar without the server pushing the value over an addon channel.

### Source Armor Sets: Stat Budget By Item Level

- Piece stats were `required_level // 8` for the primary stat and `required_level // 10` for stamina. Neither scales with item level, and integer division flattened the whole 1-80 range into 1-10 and 1-8, so a level 80 piece carried **+10 primary and +8 stamina** where stock gear at the same item level carries about **+48 and +45**. Armor was never affected -- it was already derived from item level and measured 182 against stock's 183 at matched item level -- so the sets read as correct defensively and near-worthless offensively, leaving the set bonuses to do all the work.
- Stats are now budgeted the way the game does it: item level times a per-slot share. The shares are WoW's canonical table (1.0 head/chest/legs, 0.75 shoulders/waist/feet/hands, 0.5625 wrists), which stock armor at item level 160-200 independently measures within a few percent of -- head 0.95, chest 1.00, legs 0.98, shoulders 0.73, waist 0.70, feet 0.73, hands 0.73, wrists 0.55.
- The points-per-item-level coefficients (0.37 primary, 0.38 stamina) were measured from stock rare and epic armor over the same band rather than invented. A level 80 chest now carries 70 primary and 72 stamina against stock's 73.0 and 74.1; wrists carry 40 and 41 against 39.9 and 40.3. A level 1 piece carries 4 and 5.
- A set piece therefore matches real gear on the two stats it carries while still lacking the secondary stats -- crit, haste, spell power -- that stock gear spreads its remaining budget across, so the sets sit slightly under equivalent gear overall rather than above it. Scaling `PRIMARY_POINTS_PER_ILEVEL` and `STAMINA_POINTS_PER_ILEVEL` moves the whole catalogue together.
- Verified by re-deriving the budget for all 4,896 generated rows and comparing against the emitted values: zero disagreements, 612 rows per slot. Generator-only change; no runtime and no client patch, since item stats come from the server.

### Loot Infrastructure

- Named custom loot tables support validated grouped and independent item rolls for feature modules.
- Bonus Drops provides capped independent or multiplier-equivalent rolls with tap and looter eligibility checks.
- Combat Rhythm converts its combined Overkill, Multi-pull, and Flow loot multiplier into independent rolls of the killed creature's native loot template.

## Native Solo Progression Modules

### Zone Identity Perks

- Twenty kills independently master one of 61 major outdoor leveling zones and unlock its passive aura and themed kill bonus while in that zone.
- Westfall grants extra coin, Stranglethorn Vale can grant additional hide-themed coin, and Eastern Plaguelands can grant bonus XP.
- Other seeded zones use conservative coin or XP rewards and client-known stock auras from database-driven definitions.
- Zone Identity has no Hunting dependency and contributes its own discovered Adventurer's Codex section.

### Portal and Service Network

- Tasha's Teleportation Tome records only inns physically visited by the player. Each innkeeper can teach only its own exact location.
- Learned inns are organized by continent, zone, and inn. Travel has distance-based costs, a 10-minute cooldown, and combat, mount, taxi, vehicle, and teleport-state restrictions.
- Tasha sells the unique bind-on-pickup tome from eight first-town inns. Nexus, its legacy free destination network, and Mobile Forge have been removed so town services require returning to town.

### Bounties and Progress Tracking

- Town Bounty Boards generate procedural daily kill contracts with live progress and rewards.
- Wanted Poster Boards select a daily server-wide elite target from the world database.
- The Adventurer's Codex provides a unified dashboard for progression systems and learned professions.
- Zone perks, learned-inn travel, daily bounties, and wanted bounties are independent native modules with their own persistence and configuration.

## Paladin Features

### Core Paladin Rules

- Blessing of Might, Wisdom, Kings, and Sanctuary, including their Greater versions, last one hour.
- Blessing Permanence was removed as a purchasable Crusader Power. Its one-hour duration behavior is now a core paladin rule; blessings are not made mutually stackable by this change.

### Archetype Paladin Powers

Paladin Powers now follow the level-40 archetype model in `FuturePowerMods.md`.
Each dual-spec talent slot stores its own Vindicator, Crusader, or Inquisitor
commitment independently from talent points. Core unlocks remain active in every
slot. Purchased powers from another archetype remain owned but become dormant;
switching back reactivates them without repurchase. The first commitment in each
slot is free and later changes use a configurable gold cost.

The nine core powers occupy levels 4-36: Judgement Leech, Sacred Pursuit, Flow of
the Naaru, Seal Momentum, Twin Seals, Crusader's Brand, Martyr's Ledger, Lay on
Hands: Devotion, and Unbroken Oath. Sacred Pursuit uses its intended 12-second
duration, true custom healing enters the normal healing pipeline, and Martyr's
Ledger debt cannot be erased by disabling the power.

| Archetype | Levels 40-80 | Combat Rhythm Limit Break |
|---|---|---|
| Vindicator | Guarded Light, Sanctified Bulwark, Radiant Bulwark, Aegis Vow, Consecrated Ground, Interceding Light, Light's Reprisal, Shared Aegis, Bulwark of the Faithful, Shattered Aegis, Aegis Eternal | Aegis of the Naaru |
| Crusader | Call of the Crusader, Bastion Strike, Crusader's Riposte, Sanctuary's Edge, Shieldbearer's Rebuke, Anvil of Wrath, Zeal, Wrath Unyielding, Tempered Zeal, Shieldbreaker's Verdict, Aegis of the Highlord | Judgment of the Highlord |
| Inquisitor | One With The Light, Sanctified Strikes, Hammerfall, Zealot's Tithe, Divine Storm Leech, Censure, Wrath of the Faithful, Deepened Oath, Consecrated Storm, Reckoning of the Light, Light Incarnate | Verdict of the Faithless |

Call of the Crusader is revocable. Its spellbook permission follows the active
Crusader slot, and withdrawing it runs normal offhand reconciliation so an illegal
two-hand/shield pairing cannot survive dormancy. One With The Light uses a visible
off/sworn/deepened toggle, globally pays its Physical-damage sacrifice, converts
Crusader Strike and Divine Storm to Holy, preserves their downstream healing, and
removes the sacrifice at Light Incarnate.

The three Limit Breaks are no longer mentor purchases or independent ten-minute
buttons. A full Combat Rhythm Limit meter resolves the active talent slot's
archetype and dispatches its authored effect. A Paladin without an archetype has no
Paladin Limit Break. Verdict pauses Limit charge during its echo window and tracks
each marked target independently through its end detonation.

Paladins receive starter Crusader Strike `302135` at level 1 for 50% weapon damage.
Learning normal Retribution spell `35395` removes it; login, talent removal, and
dual-spec changes reconcile both spells. The starter strike participates in Call,
Sanctuary, Censure conversion, and every other Crusader Strike interaction.

The optional UI provider publishes authoritative active masks, archetype, Radiant
Bulwark amount/cap, and oath depth. PPS_UI owns independent movers and options for
active-power icons, the Bulwark bar, Bulwark text, and the oath readout. Codex rows
distinguish on, off, dormant, and meter-spent Limit Break states.

## Mage Features

### Archetype Mage Powers

Mage Powers now follow the level-40 archetype model in `FuturePowerMods.md`, on the
same shape as the Paladin: nine core powers, three archetypes of eleven, and one
Limit Break per archetype. Each dual-spec talent slot stores its own Archon,
Chronomancer, or Elementalist commitment independently from talent points. Core
unlocks remain active in every slot. Purchased powers from another archetype remain
owned but become dormant; switching back reactivates them without repurchase. The
first commitment in each slot is free and later changes use a configurable gold cost.

The nine core powers occupy levels 4-36: Leyline Attunement, Polymorphic Instability,
Runic Recall, Elemental Cadence, Arcane Afterimage, Refreshing Heat, Displacement
Ward, Arcane Recursion, and Temporal Shatter. None of them is bound to a single
school, so none can belong to a pair of schools. Refreshing Heat is core despite
reading as a Fire power because it is the Mage's sustain floor, and Elemental Cadence
is core for the opposite reason: it rewards rotating through all three schools, which
is precisely what no archetype does.

| Archetype | Schools | Levels 40-80 | Combat Rhythm Limit Break |
|---|---|---|---|
| Archon | Arcane + Fire | Controlled Burn, Ray of Destruction, Cinderbrand, Arcane Accelerant, Flashover, Chain Reaction, Ley Furnace, Archmage's Paradox, Emberblood, Prismatic Detonation, Ascendant Flame | Sunfall |
| Chronomancer | Arcane + Frost | Permafrost, Temporal Anchor, Time Dilation, Stolen Hours, Mirror Tutor, Second Hand, Cold Storage, Time Stop, Chronal Inversion, Hoarded Seconds, Rewind | Zero Hour |
| Elementalist | Fire + Frost | Spell Prism, Thermal Shock, Glacial Mirror, Overload, Crossfire, Rolling Storm, Frostfire Mastery, Runaway Reaction, The Firemind, Runaway Escalation, Phoenix Clause | Thermal Runaway |

Winter's Debt is deleted rather than moved. It deferred 30% of your damage against
frozen targets and returned 30% — the same total, later, for nothing — and evaporated
entirely if the target died early. Time Dilation takes its slot and inverts the
premise: freezing a target reduces your cast time against it by 30% and raises your
damage to it by 30%, immediately, for as long as the slow holds. Mirror Tutor is
retuned from 20% to 40% bonus damage per active image.

Existing unlocks are migrated rather than reset. Removing Winter's Debt from the
middle of the unlock mask renumbers every power above it, so the module records the
shipped bit order and remaps each owned bit exactly once, stamped with a schema
version so the migration can neither re-run nor be skipped. Recorded Runic Recall
departure points are untouched.

The Elementalist tree runs on alternation. Thermal Shock triggers on a switch between
Fire and Frost, Rolling Storm escalates the burst by 10% per alternation to ten,
Frostfire Bolt counts as both schools once Frostfire Mastery is owned and can never
break the chain, and Runaway Reaction leaps the burst between enemies. Copies and
procs — Overload's opposite-school repeat, Crossfire's bolt, The Firemind's
counterparts, Runaway's jumps — trigger effects but never advance the alternation
memory, and Crossfire never spawns a second Crossfire. Those rules are enforced by an
event-provenance model rather than one flag per feature, because the number of ways an
event can be generated here is large enough that per-feature guards would miss a
combination.

Three archetype powers are real spellbook buttons granted and revoked with the
archetype: Temporal Anchor, Time Stop, and The Firemind. Their cooldowns are applied
from the module configuration rather than carried in the spell record, so a config edit
is the only place a cooldown is written. Ascendant Flame summons the Cinderlord as a
guardian while Archmage's Paradox is active — no pet bar, no commands, and it leaves
when Paradox does, because the Archon's health cost is deliberately never removed.

The three Limit Breaks are not mentor purchases or independent buttons. A full Combat
Rhythm Limit meter resolves the active talent slot's archetype and dispatches its
authored effect. A Mage without an archetype has no Mage Limit Break. Each one pins
several of its archetype's systems at once for ten seconds rather than being a burst:
Sunfall makes Archmage's Paradox free and pins Ley Furnace at its ceiling, Zero Hour
holds every enemy within 30 yards and returns the Mage to the health and mana the
window began with, and Thermal Runaway makes every spell both schools with the chain
unable to fail.

The optional UI provider publishes the authoritative archetype, active-power mask,
Rolling Storm stacks, Ley Furnace bonus, Paradox state, Prismatic banks, and the
Hoarded Seconds bank. Several of those have no aura the client could read — Ley
Furnace is derived from missing mana at the moment damage resolves — so the readout is
server-authoritative rather than inferred from the buff frame. PPS_UI owns independent
movers and options for the active-power icons and the archetype meters. Codex rows
distinguish on, off, dormant, and meter-spent Limit Break states.

- Ignite lasts 10 seconds as five 2-second ticks. Native Ignite, Cinderbrand, Chain
  Reaction, and Arcane Accelerant all divide contributions across all five ticks and
  roll whatever is already burning into the new application, so no contribution can
  ever lower the damage already on the target. Each contribution passes only its own
  delta to the core rollover, which carries the existing pool itself; adding the pool
  a second time turned Arcane Accelerant's 20% increase into roughly 120% and
  compounded it on every refresh.
- Archmage's Paradox pays for direct spells with health for the whole time it is
  active, not only for casts the remaining mana could not have covered, and the 150%
  damage is the other half of the same bargain. Sunfall keeps the damage and waives
  the cost.
- Arcane Recursion repeats by recasting the spell, so the repeat keeps its identity,
  rolls its own crit, fires its own procs, and works for ground-targeted spells.
  Overload changes which spell that recast is rather than how the original is scaled.
- Prismatic Detonation banks one charge per cast, not per hit, and records what the
  cast actually dealt across every target and every missile of it. Sunfall's forced
  release empties both banks rather than only the opposite one.
- Rewind and Zero Hour return the Mage to the recorded health and mana rather than
  topping up toward them. Temporal Anchor is the power that only ever heals.
- Stolen Hours and Hoarded Seconds count every slow or root the Mage lands, including
  Frostbolt's chill, Frost Nova, Cone of Cold and Blizzard, and credit only auras that
  actually applied.
- Flashover's payout and Chain Reaction's reseed are exempt from the Combat Rhythm
  damage modifiers, so "exact remaining damage" is exact.
- Switching away from Elementalist ends The Firemind's window and clears the
  alternation memory, so counterparts stop and casts made under another archetype
  cannot prime the first alternation on the way back.
- A character who owned Winter's Debt is refunded its purchase price during the
  one-time migration.
- `EnablePlayerSettings` is verified by the installer rather than announced, and a
  startup that finds missing spell records or the wrong Ignite timing stays disabled
  across a config reload.
- Refreshing Heat carries the fraction it used to discard. The heal is a percentage of
  a periodic tick, and `CalculatePct` truncates, so at low level every tick floored to
  the same 1 health no matter how hard it hit. The remainder now carries between ticks,
  so the rate holds at any damage size. The heal is deliberately not scaled a second
  time: it is derived from damage that anything reducing the player's damage done has
  already scaled once. Emberblood raises the rate to 50% and removes the per-second cap
  while Paradox is active.

## Capital Class Mentors

Each city has one uniquely named Paladin mentor and one uniquely named Mage mentor. All models use 1.15 scale.

| City | Paladin mentor and location | Mage mentor and location |
|---|---|---|
| Stormwind | Sir Aldren Lightward, Cathedral of Light | Magister Elowen Vale, Wizard's Sanctum |
| Ironforge | Thane Borin Dawnshield, Hall of Mysteries | Tilli Cogwhistle, Mystic Ward |
| Darnassus | Vindicator Saelira, Temple emissary court | Astalor Moonquill, Highborne terrace |
| Exodar | Vindicator Koruun, Vault of Lights | Arcanist Yalessa, Crystal Hall |
| Orgrimmar | Blood Knight Rethan, Valley of Honor | Arcanist Gor'mak, Valley of Spirits |
| Undercity | Blood Knight Vaelis, War Quarter embassy | Magus Mortana, Magic Quarter |
| Thunder Bluff | Blood Knight Selanar, Spirit Rise embassy | Sage-Magus Cloudglyph, Spirit Rise |
| Silvermoon | Arelion Dawnshield, Hall of Blood | Lysara Sunweave, Sunfury Spire |
| Shattrath | Vindicator Oros, Terrace of Light | Archmage Varendis, Terrace of Light |
| Dalaran | Crusader Edric Dawnwatch, Violet Gate plaza | Archmage Selwyn, Violet Gate plaza |

## Starting-Area Class Mentors

Each class-eligible racial tutorial area also has a uniquely named, race-appropriate mentor beside its normal class trainer. All models use 1.15 scale.

| Starting area | Paladin mentor | Mage mentor |
|---|---|---|
| Northshire Valley | Brother Alric Dawnmere | Arcanist Merrin Spellbrook |
| Coldridge Valley | Shieldthane Hilda Emberforge | Nixi Sparkcoil |
| Ammen Vale | Vindicator Ilyara | Arcanist Teluun |
| Sunstrider Isle | Blood Knight Aelthas | Thaelis Brightweave |
| Deathknell | Not available to Forsaken | Magus Velora Graves |
| Valley of Trials | Not available to Trolls | Zala Emberglyph |

## Combat Rhythm

Six opt-in systems that change how a fight feels minute to minute, from the "Combat rhythm" family in `Possible Features.md`. Each is taken up or set down independently per character at a Rhythm Warden, and nothing applies to a character that has not asked for it.

- **RISK** is a 0-100 meter built by offensive actions, gaining 3 points at most once every 800 milliseconds. Continuous curves reach +50% damage, +25% critical strike, +75% incoming damage, and -10% accuracy at full RISK; accuracy loss starts after 40. After 5 seconds without an offensive action it loses 1 point every second in combat or every 750 milliseconds out of combat. Players cannot freely vent RISK; the internal operation is reserved for future consumables.
- RISK applies critical-strike and accuracy changes as real rolls for melee and ranged attacks. Spells receive an expected-value damage adjustment because equivalent spell hooks are unavailable.
- **Stagger Build** fills on your target from landed hits, scaled to the target's max health so it reaches its threshold at roughly the same point in every fight. Filling it makes the target take +30% damage for 5 seconds, after which it cannot be staggered again for 20 seconds. It is a vulnerability window, never a stun.
- **Overkill** compares the largest single hit of a creature's life against its max health: a quarter of its health pays +50% experience and gold and doubles drop chance, while half its health pays +100% experience and gold and doubles drop chance. The earlier 50%/100% thresholds meant Massive Overkill required a single hit worth a creature's entire health bar, so the top tier never paid out in normal play; bosses remain effectively immune at the lower thresholds. Massive Overkill publishes a +1 rarity-tier reward, but the current random-affix system does not consume that reward yet. Largest-hit rather than killing-blow means damage-over-time classes are not excluded.
- **Multi-pull scaling** pays +15% to +100% on experience, gold and drop chance based on how many non-trivial enemies were engaged with you at the moment of the kill. Open world reaches those steps at 3, 5, 8 and 12 engaged, capped at 12. Instances use their own ladder at 2, 3, 4 and 6, capped at 6, because dungeons are authored in packs that cannot be kited together and the open-world counts are not survivable indoors. The payout ceiling is identical; only the counts that reach it differ.
- **Flow state** measures pace: kills inside a rolling 20-second window build four tiers granting up to +20% damage, +20% experience and +15% drop chance. Damage taken drains it in proportion to the fraction of your own health lost; letting the window lapse drops one tier at a time.
- **Limit breaks** charge from damage dealt and taken, both normalized against your own max health. At full charge, `.rhythm break` deals 150% of your maximum health to the primary target and 60% of your maximum health to engaged enemies within 20 yards, then starts a 30-second cooldown. Charge has no passive decay by default and resets on use, death, logout, or opting out.
- Trivial targets do not contribute to Stagger, Flow, Overkill, or multi-pull payouts. They can still build RISK and Limit Break charge.
- A single set of caps bounds the combined experience, gold, drop-chance, affix-tier, outgoing-damage and incoming-damage multipliers this module can produce.
- `.rhythm` reports every meter and what it is currently worth.
- Whether the rhythms follow you into dungeons, raids, battlegrounds and arenas is a per-character choice, off by default. It is changed in game at any Rhythm Warden or with `.rhythm instances`, is blocked in combat like every other rhythm toggle, and clears the live meters immediately when switched off inside an instance. `CombatRhythm.EnableInInstances` now seeds that choice for new characters rather than locking it server-wide.

## Combat Rhythm Wardens

- Rhythm Wardens stand in all eight faction capitals, in Shattrath and Dalaran, and in every starting area.
- Their compact gossip menu shows system names and ON/OFF state, with separate detail actions and bulk controls at the bottom.
- Choices persist per character. Individual and bulk toggles are blocked in combat. Setting a system down clears its meter immediately.

## Adventurer's Codex

- One readout for everything a character has switched on, opened from an item in the bag, from a Codex Keeper beside each capital Rhythm Warden, or with `.codex`.
- Sections: active Paladin powers, active Mage powers, active Rhythms, active Challenges, Adventure Mode, and Hunting profession stats. Each feature module registers its own section, so a disabled module contributes nothing and a druid is never shown a Mage row.
- A section is read inside the book, not in the chat log. Selecting one renders its body as a gossip page with a heading, the body lines, and navigation: previous and next section, previous and next page when the section runs past 24 lines, "Back to contents", and "Close". Neighbours are chosen only from sections that character can actually see, so stepping sideways never lands on an empty page, and a selection that no longer resolves returns to the contents page rather than closing the book.
- Replaces the always-on "this power is enabled" buff-frame indicators, which occupied a permanent icon each. Those auras are no longer applied and are stripped from characters still carrying them. Live state - charges, stacks, ready flags, cooldowns - still uses its own auras, because that is information needed mid-fight.
- New characters are mailed the configured starter items - the Codex and a Perky Pug by default - once, on first login.
- Any innkeeper replaces a lost Codex, free by default. The option only appears when it is actually missing, and a copy still sitting unread in the mailbox counts as having it. Innkeepers do not stock the Perky Pug; a summoned one is correctly recognised as still owned rather than lost.
- Every row in the book answers a click. A row a section cannot explain redraws its own page, which is what the client is waiting for; previously such a row encoded only its page number and not its section, so the handler had nothing to redraw from and replied with nothing at all. On See Zone Mastery, the one readout long enough to fill a page with those rows, the whole screen appeared to have stopped responding.
- See Zone Mastery rows are now explained rather than inert: selecting a zone reports the perk it grants and how many kills remain to master it.

## Instance Entrances

- Summoning stones teach Tasha's Teleportation Tome the way into an instance, and the tome travels to the instance **door**, never to the stone. For Blackrock Spire, Scarlet Monastery, Dire Maul and Molten Core the stone stands nowhere near the portal a group walks through, which is the point of teaching the door.
- A multi-wing instance offers one learn per wing from its single stone, and the tome takes you to that wing's own door: Scarlet Monastery's four wings resolve to four distinct courtyard doors, Dire Maul's three and Stratholme's two gates likewise.
- Travel is refused until the wing has been cleared at least once, and the check is retroactive. It reads the dungeon achievement first, then the per-wing kill criterion behind it -- classic achievements are per dungeon with one criterion per wing, so the criterion is the per-wing fact. Five wings have no criterion at all (Blackrock Depths - Prison, Dire Maul - West, both Maraudon crystal wings, Utgarde Keep); for those the module records the final boss kill itself, which it also does everywhere else as a backstop. A character who cleared a place months ago is credited without re-running it.
- 80 wings, covering dungeons and raids, generated by `tools/generate_entrances.py` from data worldserver already reads: LFGDungeons.dbc for the wing, `instance_encounters.lastEncounterDungeon` for its final boss, Achievement_Criteria.dbc for the gate, and `areatrigger_teleport` with AreaTrigger.dbc for the door. No coordinate is hand-measured.
- Eighteen instances never had a summoning stone and now have one, placed beside the entrance and offset along the door's own facing. They are real meeting stones carrying the instance's area and level range, so the native party summon works from them. Their height is taken from the entrance trigger and every one still needs an in-client placement check.
- Stones keep their party summon. `GameObject::Use` dispatches the gossip hook before its own type switch, so intercepting a stone replaces its behaviour outright; the summon is reproduced under the same conditions the core applies.
- Every tome and stone menu is paged at twelve rows with navigation before the body. `GossipMenu::AddMenuItem` ASSERTs above `GOSSIP_MAX_MENU_ITEMS`, which aborts worldserver rather than truncating a list, and the previous menus added one row per entry with no bound -- Northrend's 42 innkeeper spawns already approached it.

## Custom ID Map

- `302062`: Call of the Crusader.
- `302063-302066`: Light's Reprisal and Unbroken Oath functional/charge auras.
- `302100-302142`: Paladin core indicators, state auras, starter strike, and proc passives.
- `302143-302247`: Paladin archetype Limit Breaks, passives, visuals, Twin Seal displays, and dedicated runtime controllers and damage/heal carriers.
- `303000-303010`: Mage state and proc auras.
- `303100-303119`: Mage enabled-power indicators.
- `303120-303126`: Mage stack, target-state, debt, and recall indicators.
- `500109`: Arcane Afterimage creature.
- `500110-500119`: Paladin capital mentors.
- `500120-500129`: Mage capital mentors.
- `500130-500133`: Paladin starting-area mentors.
- `500134-500139`: Mage starting-area mentors.
- `304000-304006`: Combat Rhythm meter indicators (RISK stacks, vent lockout, Stagger Build, Staggered, Flow tier, limit-break charge and ready).
- `304007`: Limit Break combat-log damage spell.
- `500150-500152`: Rhythm Wardens.
- `500153`: Codex Keeper.
- `500190`: Veyra Chance (Gambler).
- `500191`: Maelis Runeveil (Power Curator).
- `306000-306005`: Extracted-power compatibility spells.
- `307000-307003`, `307010-307011`, `307014-307015`: Source-set support spells.
- `308001-308061`: free (Transformative spells; feature removed).
- `60000-60004`: Legacy extracted-power marker aliases; generated markers use stable IDs in `50000000-59999999`.
- `70001-70011`: free (Transformative ItemSet IDs; feature removed).
- `920000-920003`: free (Ability-granting gear; feature removed).
- `920104-920147`: free (Transformative class-set pieces; feature removed).
- Generated source-set item ranges begin at `930000`, `1130000`, and `1330000` for world, dungeon, and raid content.
- `61000-61099`: Affix Artificer rank enchantments (`SpellItemEnchantment`), authored where the stock table has no distinct ungated row for a rank.
- `61100-61199`: Random-affix top-bracket enchantments (`SpellItemEnchantment`), authored because the stock +34 ratings require Jewelcrafting 350.
- `900010`: Adventurer's Codex (item).
- `254606`: Shrine of Adventure.
- Creature guids `900000-900099` are reserved for Rhythm Warden spawns, `900100-900119` for Codex Keepers.
- Creature GUIDs `900190-900199` are reserved for Gamblers and `900200-900209` for Power Curators.
- Retired service entries `500107` and `500108` are removed by migration.

## Client Patch

The last fully verified installed `patch-Z.MPQ`, before the Paladin archetype update,
contained 1,365 custom `Spell.dbc` records, 622 `ItemSet.dbc` records, 21,073
`SpellItemEnchantment.dbc` records, the Hunting `SkillLine.dbc` record, and two
Paladin `SkillLineAbility.dbc` records for Call of the Crusader and starter Crusader
Strike. Current source manifests resolve 1,873 custom spell definitions. The new
merged archive has not yet crossed the build/install/client verification boundary;
that gap is tracked in `KnownIssues.md`. Separate feature MPQs must not overwrite the
same whole-table DBCs, and the server remains authoritative for gameplay behavior.

The archive name is load-bearing, not cosmetic. A 3.3.5a client only probes `Data/patch.MPQ` and `Data/patch-<single character>.MPQ`; it never opens anything else, and it reports no error when it skips one. The merged archive was previously emitted as `patch-PPS-merged.MPQ`, which the client ignored outright, so every custom record in it was invisible client-side while the server behaved correctly. `Z` sorts last, so the archive also wins load order against the client's other patches, which is what a whole-table override needs.

Clients that read loose files from `Data/DBFilesClient/` take those in preference to any archive. On such a client the loose copies are the installation that matters and must be refreshed alongside the archive, or the client keeps resolving an older generation of the tables.

`HelperScripts/launch_acore_servers.py` verifies all of this rather than leaving it to memory. Menu entry 9 and `--action check-patches` report archives the client will never open, custom spell ids the installed `Spell.dbc` cannot resolve, generated tables newer than the installed copies, and any module-owned addon whose installed files have drifted from source. Menu entry 10 and `--action sync-client-patch` install them: DBCs only when they are a strict superset of what the client already has, with backups, and addons mirrored and pruned inside their own folder so unrelated addons are untouched. The check also runs automatically before the game is launched.

## Player Interface

The `PPS_UI` addon renders eight readouts, each with its own ElvUI mover: the four Combat Rhythm meters (RISK, LIMIT, FLOW, STAGGER), the live class-power aura grid, and separate Adventure Mode, Zone Identity and Hunting readouts. There is no shared container frame — a single parent would collapse them into one draggable block and shift the layout whenever a readout appeared or disappeared. Placement uses ElvUI's native movers when ElvUI is loaded and standalone drag handles otherwise, and every readout is fully configurable from the ElvUI options tree under "PPS UI".

Combat Rhythm exposes per-meter bar and text visibility, width, height, font size, bar and text opacity, bar and text color, and dynamic RISK coloring. Class powers expose icon size, spacing, icons per row, maximum icon count, opacity, backdrop visibility, and independent size and color for the stack count and the player/target tag. Progression exposes width, row height, icon size, opacity, backdrop visibility, badge and Hunting font sizes, text and bar color, and per-readout visibility for Adventure Mode, Zone Identity and Hunting.

Nothing about size, position, font or color is hardcoded in a drawing module, and the class-power grid shrinks its movable footprint to the icons actually drawn.

The standalone PPS Ledger applies one saved `My faction` policy to every
faction-bearing catalog: quests and chains, Wayfinder inns and entrances,
dungeons and attunements, reputations and rewards, power sources, source-set
pieces, loot items and sources, and Realm Directory entries. Neutral content
remains visible. Inactive holiday quests are hidden
by default using live game-event IDs from `ledger-context`, while a separate
toggle exposes them for planning. Source-less retired quests are marked during
export and share the `Unavailable / retired` opt-in; quest `25290` is retained
as a generated-data regression anchor.

Routewright and Enemy Grimoire were removed completely, including their UI,
saved-state hooks, exporters, and 35 generated data addons. Power Grimoire now
groups the 7,834 approved source rows into 1,471 exact spell/trigger effects,
retains every source ability key for authoritative learned state, and provides
`All`, `Learned`, and `Unlearned` views with bounded rank details. Realm
Directory replaces the removed reference surface with 47 source-owned custom
NPC templates, 123 resolved static spawn locations, module ownership, faction,
and plain-language purpose; stale unowned templates are excluded explicitly.
Every static spawn now carries exact world X, Y, and Z. The detail
view selects one spawn at a time, cycles duplicates, and lets authorized GMs
execute the matching `.go xyz x y z` command directly.

Codex toggle execution now verifies the owning system reached the requested
postcondition before reporting success. Adventure Mode uses its authoritative
setter so aura, nearby creature health, talent reconciliation, initialization,
and persistence update immediately. Zone Mastery uses its reconcile path, while
Source Sets clears module-owned player/minion auras and cached program state on
disable and rebuilds equipped thresholds on enable. Combat Rhythm, class powers,
and Death Echo retain their existing module-owned setters; event-read toggles
remain direct settings because they have no immediate state to tear down.

Systems Inspector now correlates the live PPSQL provider handshake, module-owned
PPS UI capabilities and state payloads, applicable Adventurer's Codex option
state and lock reasons, stale or missing replies, and current character action
restrictions. Its Issues view reports blockers without treating an intentionally
disabled option as a fault, while Systems and Environment preserve the raw
evidence and link back to owning Ledger sections.

Realm Almanac now generates a load-on-demand reference from the canonical
implemented-changes baseline and READMEs/configuration owned by modules present
in the current configured build. It exposes 38 reviewed realm changes and 26
configured modules with searchable ownership, commands, config keys, owned IDs,
and UI/Codex integration; source-only work-in-progress modules are not presented
as live realm behavior.

The Ledger's `Adventure Codex` section presents every applicable Codex option
as a category-grouped live switch with enabled, disabled, and locked states,
then exposes contributed Codex status pages under `Readouts`. Both surfaces use
the same module-owned registry callbacks as item `900010`, Keeper gossip, and
`.codex`; those native paths remain intact. Loot Atlas GM grants now commit the
quantity currently typed in the edit box when `Create Item` is clicked, so a
focused value cannot fall back to the previously saved quantity of one.

## Server Support Changes

- Player settings are enabled by default.
- Database updates from all modules are allowed by default through `Updates.AllowedModules`.
- Custom database content adds the profession, challenge, PPS, affix, Crusader, and Mage service NPCs and items required by the systems above.
