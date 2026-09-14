# Custom Solo Progression Compendium

This document compiles the custom class powers, Limit Breaks, and legendary weapon integrations discussed for the eight adapted classes.

## Design Decision: Archetypes

At level 40 a character commits to one **archetype**, built from a pair of its
class's three specs. Three specs give exactly three unordered pairs, so every
class has exactly three archetypes and the set is complete by construction. For
Druids, cat and bear are one spec (Feral), so the same three-pair rule holds.

Two rules follow from that, and they are the point of the system:

1. **A character who never chooses an archetype is capped at the nine core
   powers.** The remaining powers are archetype-gated and cannot be bought
   without one. Declining to choose is a valid path, but it is a ceiling, not a
   neutral option.
2. **Each archetype owns exactly one Limit Break, and no other archetype can
   reach it.** The Limit Break is the archetype's payoff rather than a class-wide
   capstone, so the choice at 40 decides how the character ends fights for the
   rest of its life.

Core powers occupy the levels below 40. Archetype powers occupy 40 and above, so
the choice always precedes the first power that depends on it.

### Archetype binds to the talent slot, not the talent points

An archetype is chosen per **talent specialisation slot**, so a character with
Dual Talent Specialisation holds two archetypes, one in each slot, and swaps
between them by swapping specs. Two of the three are reachable at once; the
third is not.

Dual Talent Specialisation unlocks at level 40, the same level the archetype
choice is made, so the two decisions land together rather than one stranding the
other.

**Resetting talent points does not change the archetype.** A respec redistributes
points inside the slot and leaves the archetype where it is. The two are
deliberately separated:

- Respeccing is cheap and frequent. It is how a character tunes a build.
- Switching an archetype is expensive and rare. It is how a character changes
  what it *is*.

Collapsing the two would make the archetype a free rider on every respec and
erase the weight the level 40 choice is supposed to carry. Keeping them apart
means a player can experiment with talents as often as they like without ever
touching the identity underneath.

**Powers bought under another archetype go dormant, not away.** A purchase is
permanent; its availability is not. A power whose archetype is not the one active
in the current talent slot is simply disabled, and switching back re-enables it
with nothing to re-buy. This matches how mod-paladin-powers and mod-mage-powers
already work -- an unlock is a row, and whether it does anything is a separate
question -- so it costs nothing new to build.

It also means the expensive part of switching is the switch itself, not the
rebuying. A player who changes their mind twice pays twice, but never loses
progress.

**Consequence: no archetype power may be permanent.** A dormant power has to be
able to stop working, which rules out anything that changes a character's state
once and leaves it changed. Call of the Crusader is the one power in the Paladin
list that currently does this -- it permanently allows a two-handed weapon
alongside a shield -- and it will have to become an active, revocable effect
before archetypes ship. Any future power that "permanently" does anything is
disqualified from an archetype tree for the same reason.

---

## Paladin (The Crusader)

### Core Powers

These nine are available to every Paladin regardless of archetype. Each one
hangs off Judgement, Seals, mana, or staying alive -- the parts of the class
that do not change with the choice made at level 40.

| Level | Power | Effect |
| ---: | --- | --- |
| 4 | Judgement Leech | Judgement restores 20% of your maximum health and 20% of your maximum mana. |
| 8 | Sacred Pursuit | Judgement grants 25% movement speed for 12 seconds. |
| 12 | Flow of the Naaru | Damage dealt to enemies restores mana equal to 5% of damage. |
| 16 | Seal Momentum | Judgement grants a stacking 18-second Holy damage bonus, up to 5 stacks. |
| 20 | Twin Seals | Casting a new Seal retains the previous Seal at 50% strength. |
| 24 | Crusader's Brand | Exorcism stores its damage as a 15-second brand. Judgement consumes the brand for equivalent bonus Holy damage. |
| 28 | Martyr's Ledger | Defers 30% of incoming damage for 5 seconds. Damage dealt before it comes due erases the oldest debt first. |
| 32 | Lay on Hands: Devotion | Every 10 Holy Light or Flash of Light casts resets Lay on Hands. |
| 36 | Unbroken Oath | Lethal damage leaves the Paladin at 1 health, drains mana, and grants Divine Protection for 6 seconds. Once every 10 minutes. |

### Archetypes

At level 40 a Paladin commits to one of three archetypes, each drawn from a pair
of the class's three specs. The pairs are the only three combinations of three
taken two at a time, so the set is complete by construction.

| Archetype | Specs | Identity |
| --- | --- | --- |
| Vindicator | Holy + Protection | Holds the line and heals through it. Blocking and overhealing are turned into offence and absorbs. |
| Crusader | Protection + Retribution | Shield and blade together. Defensive stats are converted into damage. |
| Inquisitor | Holy + Retribution | Offence that sustains itself. Damage pays for healing and mana pays for damage. |

#### Vindicator (Holy + Protection)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Guarded Light | Blocking or parrying stores up to 2 charges. Each charge reduces the next Holy Light or Flash of Light cast time and mana cost by 15%. |
| 44 | Sanctified Bulwark | Blocking heals you for 20% of the amount blocked and allies within 10 yards for 15% of it. |
| 48 | Radiant Bulwark | Converts 50% of true self-overhealing into a 15-second absorb capped at 30% maximum health. |
| 52 | Aegis Vow | Adds 50% of your shield block value to your healing done. Block rating becomes healing power. |
| 56 | Consecrated Ground | While standing in your own Consecration, damage taken is reduced by 15% and healing done is increased by 15%. |
| 60 | Interceding Light | When an ally within 30 yards drops below 35% health, your next Flash of Light is instant and free. 15-second cooldown. Healing an ally who is below 35% health -- not yourself -- also resets Avenger's Shield. |
| 64 | Light's Reprisal | Five blocks charge Judgement to damage enemies in a 10-yard frontal cone and heal the Paladin. |
| 68 | Shared Aegis | Your absorb shields also apply to the nearest ally at 50% strength. |
| 72 | Bulwark of the Faithful | An ally you heal takes 10% less damage for 6 seconds. Counts indirect healing as well as direct casts. |
| 76 | Shattered Aegis | When a Radiant Bulwark absorb is fully consumed it shatters, dealing Holy damage to enemies within 10 yards equal to the absorb's full value. You and nearby allies are healed for 50% of the damage dealt. |
| 80 | Aegis Eternal | While in combat your Radiant Bulwark absorb no longer expires on a timer, and its cap rises from 30% to 60% of maximum health. It can still be broken. Shattered Aegis additionally pulses every 3 seconds, consuming 20% of the current absorb and paying it out as damage and healing. |

The current mod-paladin-powers catalog contains all eleven Vindicator powers and
the Vindicator Limit Break. The design text remains the behavioral reference;
gameplay still needs in-game verification.

**Why these eight.** Three of them deepen powers already in the tree rather than
adding unrelated mechanics: Sanctified Bulwark and Aegis Vow both convert
blocking, and Shattered Aegis and Aegis Eternal both build on Radiant Bulwark.
Four point outward at allies, which is the only thing separating Holy plus
Protection from Crusader in play -- without them a Vindicator is a Crusader with
worse damage. Aegis Vow is deliberately the mirror of the Crusader's
Shieldbearer's Rebuke: the same input, block value, sent to the opposite output.

All eight are revocable, so none of them trip the no-permanent-powers rule.

**UI need.** Radiant Bulwark now has three powers hanging off it -- Shared Aegis
feeds it to an ally, Shattered Aegis pays out when it breaks, and Aegis Eternal
changes when it expires -- so its remaining absorb has to be visible. It needs a
bar in PPS_UI with its own mover, in the player HUD group alongside the Combat
Rhythm meters. Without one, Shattered Aegis in particular is a payoff the player
cannot see coming or aim.

#### Crusader (Protection + Retribution)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Call of the Crusader | Allows an eligible two-handed weapon to be equipped alongside a shield. |
| 44 | Bastion Strike | Blocking charges your next Crusader Strike for +25% damage. At 3 charges it also cleaves every enemy within 8 yards. |
| 48 | Crusader's Riposte | Parrying resets Crusader Strike and empowers its next hit by 50%. |
| 52 | Sanctuary's Edge | While Divine Protection is active your damage is increased by 50% and Crusader Strike has no cooldown. |
| 56 | Shieldbearer's Rebuke | Adds 100% of shield block value to Crusader Strike and Hammer of the Righteous damage. |
| 60 | Anvil of Wrath | Blocking reduces the remaining cooldown of Hammer of the Righteous by 1 second. Hammer of the Righteous strikes 3 additional targets and leaves them unable to parry for 6 seconds. |
| 64 | Zeal | Three Crusader Strikes within 12 seconds trigger Avenging Wrath. |
| 68 | Wrath Unyielding | While Avenging Wrath is active you cannot be disarmed, silenced or slowed, and 30% of damage taken is returned to the attacker as Holy damage. |
| 72 | Tempered Zeal | Every non-triggered Crusader Strike cast during Avenging Wrath extends it by 1 second, with no cap. |
| 76 | Shieldbreaker's Verdict | Damage you block during Avenging Wrath is banked. When Avenging Wrath ends the bank detonates for Holy damage to all enemies within 15 yards, and your block and parry chance are increased by 20% for 15 seconds. |
| 80 | Aegis of the Highlord | Shieldbearer's Rebuke adds 200% of shield block value instead of 100%, and your block value is increased by 50% of your Strength. |

The current mod-paladin-powers catalog contains all eleven Crusader powers and
the Crusader Limit Break. The design text remains the behavioral reference;
gameplay still needs in-game verification.

**Why these six.** The Crusader spends block on the enemy where the Vindicator
spends it on an ally, so nothing here heals -- self-sustain is the other
archetype's answer and duplicating it would blur both. Bastion Strike teaches the
same lesson at the same level as the Vindicator's Sanctified Bulwark, and Aegis
of the Highlord scales a mid-tree power the way Aegis Eternal does, so the two
trees rhyme without repeating. Zeal, Wrath Unyielding and Tempered Zeal form one
escalating Avenging Wrath chain at 64, 68 and 72, which Shieldbreaker's Verdict
at 76 pays out into.

Shieldbreaker's Verdict closes the archetype's loop rather than opening a new
one: defence becomes damage, and the damage buys back more defence.

Call of the Crusader sits at the choice point rather than at the end. It is the
power that makes a Crusader visibly a Crusader, so a character should hold it
from the moment it commits, not forty levels later. Its cost is that the other
two archetypes can never have it.

**Implementation status.** `Power::CallOfTheCrusader` is revocable: its
permission is active only in a Crusader slot, and the normal offhand
reconciliation handles a shield that can no longer remain beside a two-handed
weapon after switching archetypes or logging back in.

#### Inquisitor (Holy + Retribution)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | One With The Light | Toggle. While active, the Physical damage you deal is reduced by 35%. Crusader Strike and Divine Storm deal their damage as Holy instead, and gain spell power equal to 50% of your Strength. |
| 44 | Sanctified Strikes | Crusader Strike and Divine Storm heal you for 20% of the Holy damage they deal. |
| 48 | Hammerfall | Hammer of Wrath ricochets to 2 nearby enemies at 50% damage regardless of their health. |
| 52 | Zealot's Tithe | Above 80% mana, Judgement and Crusader Strike may spend 8% maximum mana to deal 40% bonus damage. |
| 56 | Divine Storm Leech | Divine Storm heals for 25% of its damage dealt. |
| 60 | Censure | Your Holy damage applies a stacking Censure. At 5 stacks your next Exorcism is instant, consumes them, and deals 100% additional damage. |
| 64 | Wrath of the Faithful | Avenging Wrath increases your Holy damage by 30% and the healing you take from your own Holy damage by a further 15%. |
| 68 | Deepened Oath | One With The Light may be deepened: Physical damage reduced by 70% instead of 35%, and Crusader Strike and Divine Storm gain spell power equal to 100% of your Strength instead of 50%. |
| 72 | Consecrated Storm | Divine Storm leaves a Consecration at the target for 6 seconds. Enemies standing in it take 15% additional Holy damage. |
| 76 | Reckoning of the Light | The Holy damage you deal is banked. Exorcism consumes the bank, detonating it for Holy damage to all enemies within 10 yards and healing you for 50% of the damage dealt. |
| 80 | Light Incarnate | One With The Light no longer reduces your Physical damage at all. Every point of the sacrifice is repaid; the Holy conversion and the Strength scaling remain. |

The current mod-paladin-powers catalog contains all eleven Inquisitor powers and
the Inquisitor Limit Break. The design text remains the behavioral reference;
gameplay still needs in-game verification.

**Why these eight.** One With The Light is the cornerstone and everything else
pays into it or off it, so the archetype is one idea taken to its end rather than
a list. The arc is the sacrifice itself: at 40 it costs 35% of your Physical
damage, at 68 you may choose to pay 70% for double the scaling, and at 80 the
cost is removed entirely while the conversion stays. A player spends forty levels
paying for something and the capstone is being handed it back.

Zealot's Tithe moved from 40 to 52. It is a resource conversion, which belongs in
the middle of a tree rather than at the door, and the door now belongs to the
power the archetype is built on.

Nothing here heals an ally. Self-sustain through damage is the Inquisitor's
answer where absorbs and group healing are the Vindicator's, and where the
Crusader buys defence back with damage. Sanctified Strikes at 44 teaches that
loop at the same level the other two trees teach theirs.

Deepened Oath is a toggle inside a toggle, which needs care in the UI: the player
has to be able to see which depth is active, and Light Incarnate at 80 changes
what the depth costs. It belongs on the same readout as the toggle itself.

**Every power here is revocable**, including the cornerstone -- One With The
Light is a toggle by design, which is what makes it legal under the
no-permanent-powers rule that dormancy created.

### Limit Breaks

One per archetype, and unreachable from the other two. A Paladin who never chose
an archetype has no Limit Break at all -- it is the second half of the same
decision, not a separate unlock.

#### Vindicator: Aegis of the Naaru

Deals 100% maximum health as Holy damage to enemies within 20 yards and heals
you and every ally in that radius for the same amount. For the next 10 seconds
every point of overhealing you cause becomes a Radiant Bulwark absorb with no
cap, and blocking refreshes the duration. The Vindicator's payoff is that the
harder the fight hits, the larger the shield it leaves behind.

#### Crusader: Judgment of the Highlord

*Reworked from the previous class-wide Limit Break; its Judgement and Hammer of
Wrath loop is already the Protection-plus-Retribution rotation, so it belongs to
the archetype that lives in it.*

Deals 150% maximum health to the primary target and 60% to enemies within 20
yards as Holy-Physical damage. Instantly restores you to 100% health and mana.
For the next 10 seconds the cooldown of Judgement is reduced to 1 second, every
Judgement triggers a free Hammer of Wrath regardless of the target's health, and
your shield block value is added to every Crusader Strike.

#### Inquisitor: Verdict of the Faithless

Marks every enemy within 30 yards. For the next 10 seconds all of your damage is
duplicated as Holy damage against the marked, and every point of that duplicated
damage heals you -- there is no cap and no diminishing return. When the effect
ends each surviving mark detonates for 50% of the damage it absorbed. The
Inquisitor's payoff is that the wider the pull, the harder it sustains.

This is One With The Light with the sacrifice inverted. The toggle spends
Physical damage to buy Holy; for ten seconds the Limit Break stops charging and
pays out both at once. It should be readable as the same power at its ceiling,
so it duplicates rather than converts -- if it merely converted, a player who had
taken Light Incarnate at 80 would feel nothing change.

### Legendary Capstones

**The Light's Vengeance (Requires Ashbringer):**
Replaces Divine Storm with Wake of Ashes (20-yard golden fire wave that disarms enemies). Exorcism becomes Turn to Ash (instantly disintegrates enemies below 25% health, dropping holy orbs for 100% crit chance). Righteous Aegis converts Shieldbearer's Rebuke damage into pure Holy damage.

**Limit Break (Miracle at Light's Hope):** 150% max HP as pure Holy damage in 30 yards. 10-second damage immunity; attackers are blinded and take 10% of their own max health as Holy damage.

**Whispers of the Scarlet Lord (Requires Corrupted Ashbringer):**
Replaces Avenging Wrath with Shadow of the Highlord (converts Holy to Shadow damage, changes Zealot's Tithe to drain current health for 120% bonus damage). Hammer of the Righteous becomes Scarlet Retribution (detaches enemy shadows at 5 stacks to fight their owners). Radiant Bulwark becomes Blood Debt (stores overhealing to unleash in a massive Shadow blast via Judgement).

**Limit Break (The Scarlet Crusade):** Drains your health to 1 HP. Deals Shadow damage to the entire screen equal to 1000% of the health drained, spawning 5 Scarlet Crusade phantoms to taunt enemies.

---

## Mage (The Battlemage)

### Core Powers

These nine are available to every Mage regardless of archetype. Each one hangs
off movement, mana, Blink, or staying alive -- the parts of the class that do not
change with the choice made at level 40. None of them is bound to a single
school, so none of them can belong to a pair of schools.

| Level | Power | Effect |
| ---: | --- | --- |
| 4 | Leyline Attunement | Standing still builds up to 5 stacks of 4% spell power, one stack every 2 seconds. Any movement removes all stacks. |
| 8 | Polymorphic Instability | When Polymorph ends, a harmless animal form and 20% outgoing-damage reduction linger for 6 seconds. |
| 12 | Conjurer's Tithe | Conjuring food, water or a gem banks an Ember, up to 3. Eating, drinking or using a gem spends them all: 4% maximum mana and 2% spell power each, for 20 seconds. |
| 16 | Unmaking | An enemy your spells kill bursts for 10% of its own maximum health, in the school that killed it, within 8 yards. |
| 20 | Arcane Afterimage | Blink leaves a cloned illusion that taunts nearby non-boss enemies for 2 seconds, then explodes. |
| 24 | Refreshing Heat | Your periodic damage heals you for 30% of it, capped each second at 15% of your maximum health. |
| 28 | Arcane Aegis | Mana Shield absorbs 3x as much per point of mana, and while it holds 10% of the damage you deal heals you. Healing past full becomes mana instead. |
| 32 | Arcane Recursion | Every fifth direct Mage spell with a base cast time repeats for 50% resolved damage at no mana cost. |
| 36 | Temporal Shatter | Five critical direct spell hits make the next spell instant/free and heal for 50% of its damage. |

Arcane Afterimage sits after level 20 because Blink is learned there, and
Polymorphic Instability after 8 for the same reason.

Refreshing Heat is core rather than archetype-owned despite reading as a Fire
power. It is what makes a Mage able to solo at all -- it was the difference in a
level 22 Deadmines clear -- and a sustain floor that load-bearing cannot sit
behind a level 40 choice.

**Four powers were replaced after play.** Elemental Cadence was core on the
argument that rewarding rotation through all three schools "belongs to the
unspecialised class or to nobody"; nobody was the right answer, because
Controlled Burn, Permafrost and Cinderbrand all pay a Mage for staying in one
school, so the core line was arguing with every archetype at once. Unmaking took
its level and reads the school of the killing blow instead of asking for a
sequence, so it has no opinion about a rotation. Runic Recall's only interface
was typing a command. Displacement Ward moved the Mage, which is the half of a
panic button that goes wrong -- Arcane Aegis mitigates instead, and rescues Mana
Shield, whose stock mana-per-damage ratio makes it a trap. Controlled Burn was a
cast-speed ramp with a mana tax and stated nothing about the Archon; Wildfire
opens the tree by feeding the Ignite loop that Flashover cashes out at 56.

Wildfire's share is taken from each critical rather than from the burning pool.
A pool-relative percentage compounds -- every crit raises the base the next one
multiplies -- and with no window to expire in it would double until Flashover
detonated more than the encounter had health. Against the crit it is linear and
bounded by what the Mage can actually hit for, which is why it needs no cap.

The four replacements kept the enum bits of the powers they replaced, so a
character who bought the old power owns the new one at the same level and price.

### Archetypes

At level 40 a Mage commits to one of three archetypes, each drawn from a pair of
the class's three schools. The pairs are the only three combinations of three
taken two at a time, so the set is complete by construction.

| Archetype | Schools | Identity |
| --- | --- | --- |
| Archon | Arcane + Fire | Escalation. Damage compounds on itself and mana is fuel to be spent, not conserved. |
| Chronomancer | Arcane + Frost | Control. Time, stasis and illusion -- damage is deferred, stored, and collected later. |
| Elementalist | Fire + Frost | Conversion. Heat and cold traded against each other, each one paying for the other. |

#### Archon (Arcane + Fire)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Wildfire | Every Fire critical feeds the target's Ignite 10% of the damage that crit dealt. No cap and no window. |
| 44 | Ray of Destruction | Replaces Arcane Missiles with a channelled beam of fire. The beam is still Arcane and keeps every proc and interaction Arcane Missiles had; while it channels, the target pulses Fire damage to all enemies within 8 yards. |
| 48 | Cinderbrand | Blast Wave and Flamestrike also apply a native Ignite worth 75% of the hit, spread over its ticks. Any Ignite already burning is rolled into it rather than replaced. |
| 52 | Arcane Accelerant | Arcane Explosion increases the remaining damage of every Ignite it hits by 20% and refreshes its duration. |
| 56 | Flashover | Fire Blast consumes nearby Ignites and immediately deals each Ignite's exact remaining damage. |
| 60 | Chain Reaction | Flashover's detonation leaves a fresh Ignite on every target it hit, worth 40% of the damage it dealt there. |
| 64 | Ley Furnace | Your spell damage increases by 1% for every 4% of maximum mana you are missing, to a maximum of 20% at empty. |
| 68 | Archmage's Paradox | At or below 15% mana, direct spells are paid for with health at 1x the mana cost and deal 150% damage. |
| 72 | Emberblood | While Archmage's Paradox is active, Refreshing Heat heals for 50% of your periodic damage instead of 30%, and its per-second cap is removed. |
| 76 | Prismatic Detonation | Casting a spell banks a charge of its school, up to 5 per school, each charge remembering the damage its spell dealt. Casting a spell of the other school releases every charge held by the first, detonating for 25% of their combined damage in a 10-yard burst of that school. |
| 80 | Ascendant Flame | Archmage's Paradox triggers at or below 40% mana instead of 15%, and Ley Furnace's ceiling rises from 20% to 40%. While Paradox is active you are attended by the Cinderlord, a knee-high Firelord summoned as a guardian. |

The current mod-mage-powers catalog contains all eleven Archon powers and the
Archon Limit Break. The design text remains the behavioral reference; gameplay
still needs in-game verification.

**Why these seven.** The archetype already had a build-and-detonate loop and an
Arcane power that rewards running dry. What it did not have was a reason those
two ideas belong to the same character. The additions are the connective tissue:
an Arcane spell that is physically made of fire (Ray of Destruction), Arcane
casts feeding the fire already burning (Arcane Accelerant), and a detonation that
restarts the ramp instead of ending it (Chain Reaction).

Ray of Destruction stays Arcane on purpose. Reskinning Arcane Missiles as fire
and moving it to the Fire school would break every Arcane interaction it has --
Missile Barrage above all -- and turn a fusion into a replacement. Keeping the
beam Arcane while its *pulses* deal Fire damage is what makes it belong to this
archetype and no other: it is one cast that is both schools at once. The pulses
being Fire damage also means they can crit into a native Ignite, which Arcane
Accelerant extends four levels later and Flashover cashes four after that.

For Prismatic Detonation at 76 it banks a single Arcane charge, because charges
are per cast and the pulses are damage rather than casts. One channel does not
fill and empty the bank by itself.

**The visual.** Two candidates, both buildable from stock 3.3.5 assets:

1. *A recoloured drain beam.* The Warlock drain channels are the only
   continuous beams the client already draws between caster and target, so the
   geometry is solved and only the colour changes. Safe, and it will read
   correctly at any framerate.
2. *Pyroblast on a fast loop.* Pyroblast is a projectile, so looping it tightly
   is not a stuttering beam -- it is a continuous stream of fireballs crossing
   the gap, which is a better picture of the spell than a solid beam and is
   unmistakably this Mage's. It costs nothing to try because it reuses a visual
   whole rather than editing one.

Option 2 is the more distinctive and is worth attempting first; option 1 is the
fallback if the projectile spacing looks wrong at range. The pulse itself wants a
separate ground-level fire burst so the splash is legible to the player standing
in it.

The arc is fuel. Ley Furnace at 64 makes an empty bar a damage stat, Archmage's
Paradox at 68 makes it a resource, Emberblood at 72 makes it survivable, and
Ascendant Flame at 80 widens the window it all happens in -- the threshold nearly
triples and the damage ceiling doubles.

**The health cost never goes away.** Removing it at 80 would have deleted the
archetype's only real risk and made Emberblood at 72 decorative; the capstone
instead pays out in reach and in damage, and the Mage still bleeds for it. That
is also why the Cinderlord is a *guardian* and not a pet -- it has no pet bar, no
commands and no stay/follow. It is an aggressive Fire Elemental-model combat
guardian that follows the Mage's target, despawning with Paradox rather than on
a timer. A controllable pet would be a second health bar to hide behind, which
is the same mistake as removing the cost. The name echoes Cinderbrand at 48
deliberately.

Emberblood is deliberately written against a core power rather than a new one.
Refreshing Heat is the Mage's sustain floor, and the Archon's problem at 68 is
that it starts paying for spells in health; the fix is to widen the valve that is
already there. That also means Emberblood does nothing for a Mage who has not
reached Paradox, which is correct -- it is the answer to a question the archetype
asks four levels earlier.

Prismatic Detonation is the only power here that punishes leaning on one school,
and it does it without a button of its own. Charges only ever leave the bank when
the *other* school is cast, so a Mage who casts nothing but Fire banks five
charges and never sees them again. Switching is the trigger, which makes the
detonation a consequence of playing both schools rather than a reward announced
afterwards. It is the clearest statement in the tree that this is Arcane **and**
Fire rather than Fire with an Arcane accessory.

It also resolves a dangling reference: the Mage legendary capstone already
promises that every spell triggers Prismatic Detonation, and until now the doc
never said what that was.

Arcane Accelerant is deliberately narrowed to Arcane Explosion rather than every
Arcane spell. As a passive on all Arcane casts it was free value that happened to
you; on one button it is a decision -- step into melee range of everything you
have set on fire, and pay for the extension in position.

#### Chronomancer (Arcane + Frost)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Permafrost | Consecutive Frostbolts progressively slow, then root the target on the fourth hit. |
| 44 | Temporal Anchor | Records your current health. For the next 30 seconds you may spend the Anchor to return to that value. It only ever heals. 30-second cooldown. |
| 48 | Time Dilation | While a target is slowed or frozen by your spells, time runs faster for you against it: your cast time on that target is reduced by 30% and your damage to it increased by 30%. |
| 52 | Stolen Hours | Each enemy your spells slow or root grants 3% spell haste for 45 seconds, stacking to 15%. |
| 56 | Mirror Tutor | Mirror Images last 44.5 seconds; each active image contributes 40% bonus damage and the original visual. |
| 60 | Second Hand | Each active Mirror Image recasts the last spell you cast one second after you cast it, for 60% of its damage. |
| 64 | Cold Storage | Ice Block records up to 5 nearby enemies and launches Ice Lance at valid targets when it ends. |
| 68 | Time Stop | Halts every enemy within 15 yards for 5 seconds. They cannot act or move, and damage does not break it. 2-minute cooldown. |
| 72 | Chronal Inversion | Enemies you damage are slowed by a percentage equal to your current spell haste. The speed you gain is the speed you take. |
| 76 | Hoarded Seconds | Every full second of slow or root you inflict banks 0.2 seconds, up to 30. Icy Veins consumes the bank and extends its own duration by that much. |
| 80 | Rewind | Lethal damage instead rewinds you to the health and mana you had 10 seconds ago and freezes every enemy within 15 yards for 4 seconds. Once every 5 minutes. |

Permafrost, Mirror Tutor and Cold Storage exist in mod-mage-powers today, and
Mirror Tutor's row is a retune -- shipped code gives each image 20%, not 40%.
Everything else is a proposal.

**Winter's Debt is deleted, not moved.** It deferred 30% of your damage against
frozen targets and returned 30%: the same total, later, for nothing. Adding
interest would have papered over the real problem, which is that the power's
whole idea is *your damage arriving later*, and there is no version of that a
player wants. It also had a failure mode with no upside -- kill the target early
and the deferred damage simply evaporated. A power that punishes killing things
is not a Mage power.

Time Dilation replaces it by inverting the premise. Instead of freezing a target
and waiting, freezing a target is what lets you go faster: 30% off your cast time
and 30% onto your damage, immediately, for as long as the slow holds. Same slot,
same trigger, opposite direction, and nothing is ever lost.

**The archetype is one loop.** Arcane speeds you up, Frost slows them down, and
the two feed each other: Stolen Hours turns enemies you have slowed into haste
that lasts 45 seconds, and Chronal Inversion at 72 turns that haste back into
slows on everything you hit. Slow one target, gain speed, and that speed slows
the next -- which pays back into Stolen Hours. Both ends are capped (15% haste,
and the slow can never exceed your haste), so the loop accelerates into a ceiling
rather than running away.

Chronal Inversion sits at 72 because that is the slot where a direct upgrade
would have been the lazy answer. Widening Temporal Anchor's window and adding
mana to it was exactly that -- a bigger number on a power you already had, with
no new decision. Inversion instead is the only power in the tree that requires
both schools to function at all: with no haste it does nothing, and what it does
with haste is Frost.

Temporal Anchor takes 30 seconds to come back, so it is a real cooldown you spend
rather than a state you maintain. Rewind at 80 is unconditional and needs no
setup -- it reads your health from ten seconds ago, which the fight is already
generating for you. A capstone should not be able to be *wasted* by forgetting to
arm it; that is a trap disguised as depth, and the earlier draft had exactly that
trap in it.

Time Stop is the archetype's one hard cooldown and does not protect its targets.
Five seconds of held enemies while Time Dilation is granting 30% and Stolen Hours
is stacking off every one of them is a burst window, not a defensive pause.

#### Elementalist (Fire + Frost)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Spell Prism | Every 2s in combat, a school you have not used gains a stack, up to 5. The next spell of that school deals 6% more damage per stack, up to 30%. |
| 44 | Thermal Shock | A Fire spell cast immediately after a Frost spell, or a Frost spell after a Fire spell, deals 25% of its damage again as a burst of the opposite school. Two casts of the same school in a row trigger nothing. |
| 48 | Glacial Mirror | The first direct spell to break each Ice Barrier is reflected for equivalent same-school damage. |
| 52 | Overload | Arcane Recursion's free repeat is recast in the opposite school to the spell that triggered it -- a Fireball repeats as a Frostbolt -- and its damage rises from 50% to 100%. |
| 56 | Crossfire | Every critical strike launches a bolt of the opposite school at the same target for 25% of the crit's damage. |
| 60 | Rolling Storm | Each alternation between Fire and Frost adds a stack of Storm, up to 10, increasing Thermal Shock's burst by 10% per stack. Casting two spells of the same school in a row empties it. |
| 64 | Frostfire Mastery | Frostfire Bolt counts as both schools at once: it alternates with the spell before it and the spell after it, always triggers Thermal Shock, and can never break Rolling Storm. Every fifth alternation makes your next Frostfire Bolt instant and free. |
| 68 | Runaway Reaction | Thermal Shock's burst has a 30% chance to leap to another enemy within 10 yards and detonate again. There is no limit to the chain; each jump loses 20% of the damage. |
| 72 | The Firemind | For 12 seconds every Fire spell you cast also casts its Frost counterpart at 50% damage, and every Frost spell its Fire counterpart -- Fireball with Frostbolt, Flamestrike with Blizzard, Fire Blast with Ice Lance. 2-minute cooldown. |
| 76 | Runaway Escalation | Runaway Reaction's chain no longer decays. Each jump deals 15% *more* than the last, and the chain continues until a 25% roll fails. |
| 80 | Phoenix Clause | Lethal damage triggers a 6-second Greater Fire Elemental form, fire pulses, and 20% health restoration. |

The current mod-mage-powers catalog contains all eleven Chronomancer powers and
the Chronomancer Limit Break. The design text remains the behavioral reference;
gameplay still needs in-game verification.

**Why these eight.** The brief was Izzet -- red and blue, Niv-Mizzet -- and what
makes that colour pair work in Magic is not that it plays two colours, it is that
the payoff *is* the switching. Niv-Mizzet does not reward you for drawing cards
or for dealing damage; it turns each one into the other until the loop runs
itself. So the Elementalist's engine is the alternation, and every power here
either triggers on a switch or makes the next switch bigger.

Thermal Shock at 44 is the trigger, deliberately the simplest power in the tree
and deliberately punishing: two casts of one school in a row and it does nothing
at all. Rolling Storm at 60 is the escalator -- ten alternations make that burst
twice the size, and one lazy double-Fireball empties the whole stack. Runaway
Reaction at 68 is the chain, uncapped on purpose, because an engine that can in
principle run away is the point of the colour pair. It decays 20% a jump, so a
big pull produces a long visible cascade rather than an unbounded one.

Overload at 52 is written against a core power rather than a new one, the same
way the Archon's Emberblood is. Arcane Recursion already repeats every fifth
spell for half damage; Overload makes the repeat come out the *other* school and
at full damage. That single change turns a passive the whole class has into the
archetype's most reliable alternation, because the copy switches schools for you.

Frostfire Mastery at 64 is the keystone, and it works because 3.3.5 already
shipped the card this archetype needed: Frostfire Bolt is canonically both
schools. Treating it as both for alternation purposes gives the Elementalist a
signature spell that can be cast at any point in any sequence without ever
costing you a stack. It is the release valve for a tree whose every other power
punishes casting the wrong thing twice.

The Firemind at 72 is the Niv-Mizzet card, name and all -- twelve seconds where
every spell is both schools at once.

Runaway Escalation at 76 inverts its own prerequisite. Runaway Reaction chains at
30% and loses a fifth of its damage each jump, so it fizzles out visibly;
Escalation makes each jump hit 15% harder and ends the chain only on a failed 25%
roll. The expected length is short and the tail is not, which is the correct
shape for this colour pair: most casts do nothing unusual and occasionally the
room detonates.

#### Counterparts

The Firemind mirrors by role, and only these pairs mirror. A spell not on this
list is cast normally with no counterpart.

| Fire | Frost | Role |
| --- | --- | --- |
| Fireball | Frostbolt | primary nuke |
| Fire Blast | Ice Lance | instant filler |
| Scorch | Frostfire Bolt | fast cast |
| Pyroblast | Deep Freeze | heavy single target |
| Flamestrike | Blizzard | ground AoE |
| Blast Wave | Cone of Cold | close AoE |
| Dragon's Breath | Frost Nova | control burst |
| Combustion | Icy Veins | cooldown |

Living Bomb has no counterpart because Frost has no damage-over-time, and
inventing one for twelve seconds a fight is not worth the rules surface.

#### Interactions

These four powers all generate extra damage events, so the order of operations
has to be stated or the tree will not behave the way it reads.

**The chain remembers only what you cast.** Thermal Shock and Rolling Storm track
the school of spells *you* cast. Copies and procs -- Overload's repeat,
Crossfire's bolt, The Firemind's counterparts, Runaway Reaction's jumps -- trigger
effects but never update that memory.

That is the rule that makes Overload safe. Its repeat comes out the opposite
school, so if copies counted, casting Fireball would leave you "on Frost" and
your next Frostbolt would break the chain -- the power would sabotage the engine
it belongs to. Because copies do not count, **Overload can only ever add**.

**Overload's repeat always triggers Thermal Shock**, because it is opposite-school
by definition and alternation is its trigger. Every fifth spell therefore carries
a guaranteed extra burst on top of its own damage.

**Crits double Thermal Shock's burst.** This is the one multiplication point in
the tree and it is deliberate -- it is where the Izzet feeling of a cascade
suddenly getting out of hand comes from. Crossfire fires off the same crit, so a
critical alternation produces the spell, a doubled burst, and an opposite-school
bolt from a single cast. Runaway Reaction then chains the *doubled* burst, and at
76 that chain escalates.

**Crossfire cannot trigger itself.** Its bolt can crit, and its crit is worth
having, but a Crossfire bolt never spawns a second Crossfire. One hop, always.
Without that limit a lucky crit string is an unbounded loop rather than a big
moment, and Runaway Reaction is already the tree's designated runaway.

### Distribution

Forty-two Mage powers: nine core, available to everyone, and thirty-three split
across the three archetypes at eleven levels each. With the three Limit Breaks
that is forty-five entries, the same shape as the Paladin.

*This paragraph previously read "thirty-two" and "twenty-three split across the
three archetypes", which contradicted the tables above it — three trees of
eleven is thirty-three, not twenty-three. The tables are authoritative and the
counts here now follow them.*

The current mod-mage-powers catalog contains all forty-two regular powers and
three archetype Limit Breaks. Mirror Tutor is a retune from 20% to 40%, and the
shipped Winter's Debt power was deleted during the migration.

### Limit Breaks

One per archetype, and unreachable from the other two. A Mage who never chose an
archetype has no Limit Break at all.

#### Archon: Sunfall

*Reworked from the class-wide Chrono-Cataclysm, which named Flashover, Archmage's
Paradox and Winter's Debt together -- powers no single Mage can now hold. Its
Fire and mana half became this; its time half became Zero Hour.*

Deals 150% maximum health to the primary target and 60% to enemies within 20
yards as Fire damage. For the next 10 seconds Archmage's Paradox is active
regardless of your mana and costs no health, Ley Furnace is pinned at its
ceiling, and every Fire spell detonates Prismatic Detonation whether or not the
banks are balanced. The Cinderlord, if you have it, burns at full size for the
duration.

The one window in which the Archon's sacrifice is free -- and the reason the
capstone at 80 does not simply grant that permanently.

#### Chronomancer: Zero Hour

Deals 150% maximum health to the primary target and 60% to enemies within 20
yards as Frost damage, and stops every enemy within 30 yards for the full 10
seconds under Time Stop rules -- damage does not break it. Stolen Hours is pinned
at maximum and Chronal Inversion applies its slow at that pinned value. When the
10 seconds end you are returned to the health and mana you had when it began.

The Limit Break is itself a rewind: everything inside the window is free, because
the window is undone.

#### Elementalist: Thermal Runaway

Deals 150% maximum health to the primary target and 60% to enemies within 20
yards, split evenly between Fire and Frost. For the next 10 seconds every spell
you cast counts as both schools, so Thermal Shock triggers on every cast and
every burst is doubled as though it had critically struck. Rolling Storm is
pinned at 10 and cannot empty, and Runaway Reaction's chain cannot fail -- each
burst leaps to every enemy within 10 yards and escalates 15% a jump.

The engine with the brakes off. Everything the archetype spends forty levels
learning to sustain happens at once, and the only limit left is how many enemies
are standing close enough to conduct.

### Legendary Capstone

**Mantle of the Guardian (Requires Atiesh, Greatstaff of the Guardian):**
Replaces Blink with Flight of the Raven (dissolve into Arcane ravens with 3 charges, damaging enemies and applying Cinderbrand and Time Dilation). Blizzard/Flamestrike become Ley-Rift (a gravity well that duplicates direct spells cast into it to all trapped enemies). Evocation becomes Echoes of Karazhan (summons Shade of Nielas Aran for 15s; locks mana at 100% to absorb Archmage's Paradox penalty).

**Limit Break (The Guardian's Edict):** 150% max HP Chaos damage orbital strike. For 10 seconds, you gain max movement-immune Leyline/Cadence stacks, and every spell automatically triggers Prismatic Detonation.

---

## Warrior (The Arsenal Master)

### Core Powers

These nine are available to every Warrior regardless of archetype. Each one
hangs off Rage, stances, shouts, or staying alive -- the parts of the class
that do not change with the choice made at level 40.

| Level | Power | Effect |
| ---: | --- | --- |
| 4 | Warmaster's Stance | Abilities no longer have Stance requirements. Changing stances retains 100% of your Rage. |
| 8 | Sundering Force | Sunder Armor instantly applies 5 stacks, deals 50% weapon damage, and generates 10 Rage. |
| 12 | Fluid Stance | Changing stances or weapon sets generates 10 Rage. This effect has a 3-second internal cooldown. |
| 16 | Blood Price | You generate double Rage from taking damage. Generating Rage heals you for 1% of your maximum health per 5 Rage generated. |
| 20 | Defiance in Death | Lethal damage drops you to 1 HP, clears all debuffs, and automatically triggers Shield Wall and Recklessness. Once every 10 minutes. |
| 24 | Boiling Point | Rage generated while you are at maximum Rage (100) converts into a physical absorb shield, capped at 30% of your maximum health. |
| 28 | Unbridled Wrath | Battle Shout and Commanding Shout cost no Rage, generate 20 Rage, and their duration becomes infinite. |
| 32 | Harpoon | Heroic Throw physically pulls the target to you, roots them for 2 seconds, and resets the cooldown of Charge. |
| 36 | Berserker's Paradox | While you are below 35% health, your abilities cost 0 Rage and your critical strike damage is increased by 50%. |

**Why these nine.** Warmaster's Stance at 4 removes the primary UI friction of the WotLK Warrior, while Fluid Stance and Blood Price ensure the Warrior has a self-sustain floor in a solo environment (generating Rage literally generates health). Boiling Point solves the "overcapping" problem that plagues high-end Fury/Arms Warriors by turning wasted resources into an engine of survival. 

### Archetypes

At level 40 a Warrior commits to one of three archetypes, each drawn from a pair
of the class's three specs.

| Archetype | Specs | Identity |
| --- | --- | --- |
| Warmaster | Arms + Protection | The Arsenal. Mastering the UI. Swapping weapons dynamically mid-combat to bank and stack distinct combat buffs. |
| Bloodrager | Arms + Fury | Exsanguination. Crits drive bleeds, bleeds drive healing, and both drive AoE detonations. |
| Juggernaut | Fury + Protection | Unstoppable momentum. Dual-wielding shields, massive shockwaves, and converting incoming pain into offensive power. |

#### Warmaster (Arms + Protection)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Arsenal Mastery | Weapon swapping triggers no global cooldown. Casting two abilities with a specific weapon type grants its Arsenal Buff for 20 seconds. |
| 44 | Arsenal: Crushing | *(Maces/Fists)* Ignore 20% of enemy armor. Stunning or staggering a target heals you for 5% maximum health. |
| 48 | Arsenal: Slashing | *(Swords/Daggers)* 15% chance for all melee abilities to trigger a free, instant auto-attack swing. |
| 52 | Arsenal: Cleaving | *(Axes/Polearms)* +30% critical strike damage. Critical strikes bleed the target for 20% of the damage dealt over 4 seconds. |
| 56 | Arsenal: Bulwark | *(Shields)* Grants a physical absorb shield equal to 200% of your Block Value and reflects 15% of direct damage taken. |
| 60 | Relentless Arsenal | Critical ability casts count as two casts toward triggering your next Arsenal Buff. |
| 64 | Adaptability | The damage of your next Overpower or Revenge is increased by 40% per distinct Arsenal Buff currently active. |
| 68 | Arsenal Overload | While you have 3 or more distinct Arsenal Buffs active, you gain immunity to crowd control and 20% movement speed. |
| 72 | Weaponmaster's Parry | Parrying with a Two-Handed weapon triggers the Bulwark buff at 50% efficiency. Blocking with a Shield triggers your main-hand weapon's Arsenal Buff. |
| 76 | Grandmaster's Execution | Execute consumes all active Arsenal Buffs, dealing 30% bonus damage and refunding 20 Rage per buff consumed. |
| 80 | Master's Repertoire | Maintaining all four Arsenal Buffs simultaneously grants 50% increased damage dealt and reduces damage taken by 30%. |

**Why these eleven.** The Warmaster is a love letter to the "stance-dancing, weapon-swapping" macro-heavy tryhard Warrior of early WoW. Arsenal Mastery at 40 is the cornerstone, and 44 through 56 define the toolkit. A Warmaster's entire loop is equipping an Axe, casting Mortal Strike + Cleave to gain *Arsenal: Cleaving*, instantly swapping to Sword + Board for Shield Slam + Revenge to gain *Arsenal: Bulwark*, and so on. Master's Repertoire at 80 rewards flawless APM execution with god-like stats.

#### Bloodrager (Arms + Fury)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Serrated Steel | Rend and Deep Wounds tick 50% faster. Critically striking a bleeding target generates 5 Rage. |
| 44 | Exsanguinate | Thunder Clap consumes Rend and Deep Wounds on all targets hit, dealing 100% of their remaining damage instantly. |
| 48 | Vampiric Steel | Cleave, Whirlwind, and Bladestorm heal you for 10% of the damage they deal. |
| 52 | Flay | Instant cast. Replaces Slam. Applies Rend to the target and splashes all existing bleeds from the primary target to 2 nearby enemies. |
| 56 | Gore | Mortal Strike and Bloodthirst refresh the duration of all your bleeds on the target and force them to tick once instantly. |
| 60 | Carnage | For each bleeding target within 10 yards, you gain 5% Haste, stacking up to 25%. |
| 64 | Endless Rage | Your maximum Rage is increased from 100 to 200. |
| 68 | Blood Frenzy | Overhealing received from Blood Price or Vampiric Steel is converted into Attack Power at a 50% ratio for 10 seconds. |
| 72 | Rupture | Execute deals 5% more damage per active bleed on the target, and causes the target to hemorrhage 50% of the damage dealt over 6 seconds. |
| 76 | Boiling Blood | While any Enrage effect is active, your bleeds critically strike for 200% damage. |
| 80 | Crimson Bladestorm | Bladestorm hurls blood blades at nearby targets, automatically applying Rend and Deep Wounds. Its cooldown is reduced by 1 second every time a bleed critically strikes. |

**Why these eleven.** Bloodrager solves the historical issue where Arms bleeds felt like passive maintenance rather than active weapons. Serrated Steel sets up the engine, and Exsanguinate is the detonator. You spread bleeds with Flay, accelerate them with Gore, and cash them out with Thunder Clap (Exsanguinate). Crimson Bladestorm at 80 is the ultimate payoff—because bleeds reduce its cooldown, jumping into a pack of bleeding mobs means almost permanent Bladestorm uptime.

#### Juggernaut (Fury + Protection)

| Level | Power | Effect |
| ---: | --- | --- |
| 40 | Titan's Bulwark | You may dual-wield two Shields, or equip a Two-Handed weapon and a Shield. Shield Slam hits with both shields if dual-wielding. |
| 44 | Momentum | Charge, Intercept, and Intervene share no cooldown and gain 2 charges each. Moving generates Rage. |
| 48 | Unyielding Rampage | Rampage now also heals you for 15% of your maximum health and triggers Shield Block. |
| 52 | Shockwave Cascade | Shockwave sends out three consecutive cones. Enemies hit by all three are staggered, taking double damage from your next Shield Slam. |
| 56 | Kinetic Transfer | Taking unmitigated Physical damage increases the damage of your next Cleave or Heroic Strike by an equal amount, up to 50% of your max HP. |
| 60 | Meat Cleaver | Cleave hits all enemies in a 180-degree frontal arc. |
| 64 | Battering Ram | Shield Slam knocks the target back 5 yards. If they collide with terrain, they are stunned for 3s and take massive physical damage. |
| 68 | Ignored Pain | Converts 50% of all incoming damage into a DoT over 10 seconds. Dealing damage with Shield Slam instantly clears the DoT. |
| 72 | Juggernaut's Momentum | While above 80% health, you are immune to movement-impairing effects. Shield Slam critical strikes reset the cooldown of Charge and Intercept. |
| 76 | Cratering | Heroic Leap and Thunder Clap damage increases by 10% for every yard traveled before striking. |
| 80 | The Living Avalanche | Every time you Charge, Intercept, or Intervene, you gain 5% physical size and 10% damage dealt for 10 seconds. Stacks up to 10 times. Moving extends the duration. |

**Why these eleven.** Dual-wielding shields is a legendary community meme that actually makes for phenomenal gameplay. Titan's Bulwark at 40 allows the Juggernaut to act like a Fury warrior using Protection tools. The entire loop is about movement: Charging into a pack (gaining Avalanche stats), using Battering Ram to slam enemies into walls, and using Ignored Pain + Shield Slam to completely delete incoming damage.

#### UI Needs
The Warmaster requires a custom UI element in the `PPS_UI` HUD group to track the 4 Arsenal Buffs. Because *Master's Repertoire* requires maintaining all 4, the UI needs four distinct runes or icons (Mace, Sword, Axe, Shield) that light up and show their 20-second drain timers so the player knows exactly which weapon they need to swap to next.

### Limit Breaks

One per archetype, and unreachable from the other two. 

#### Warmaster: Omnistrike
Consumes full Limit Break charge. You strike all enemies within 10 yards with every melee weapon currently in your bags, dealing massive physical damage per weapon and instantly applying all four unlocked Arsenal Buffs at their maximum duration.

#### Bloodrager: Rivers of Blood
Deals 150% maximum health as Physical damage to the primary target and 60% to enemies within 20 yards. For 10 seconds, all attacks apply a stacking hemorrhage that deals true damage. You gain 100% lifesteal, and all bleeds tick every 0.1 seconds.

#### Juggernaut: Unstoppable Force
Deals 150% maximum health as Physical damage to all nearby enemies. For 10 seconds, your physical size increases by 300%. Moving through enemies physically knocks them into the air and deals massive damage. You cannot be stopped, slowed, rooted, or damaged for the duration.

### Legendary Capstone

**Legacy of the Windseeker (Requires Thunderfury, Blessed Blade of the Windseeker):**
Replaces Whirlwind with Cyclone Strike (a 15-yard wandering tornado that deals Nature damage and slows enemy attack speed). Thunder Clap becomes Static Detonation (fires Chain Lightning at 10 targets, cauterizing active bleeds for unmitigated Nature damage). Tempest Arsenal passive consumes active Arsenal Buffs upon equipping Thunderfury, increasing its Chain Lightning proc chance by 25% per buff.

**Limit Break (Wrath of Thunderaan):** 150% max HP Nature damage strike. A 10-second hurricane grants projectile and root immunity, reduces your Global Cooldown to 0.5s, grants infinite Rage, and causes every Heroic Strike or Cleave cast to summon Thunderaan's projection for a colossal lightning slam on your target.
---

## Hunter (The Apex Warden)

### Class Powers

| Power | Effect |
| --- | --- |
| Point Blank | Ranged weapons have no minimum range requirement. |
| Alpha's Command | Kill Command has no cooldown (costs 10% mana), instantly teleporting active pets to the target. |
| Trap Launcher | Traps can be fired up to 30 yards away and arm instantly. |
| Blood Scent | Hunter's Mark applies to all enemies within 10 yards. Pets deal 20% splash damage to marked targets. |
| Packlord | Summon a second pet from your stable (shares Spirit Bond/Bestial Wrath, deals 60% damage). |
| Aspect of the Chimera | Combines the attack power, movement speed, and mana regen of Hawk, Cheetah, and Viper. |
| Flanking Strike | Raptor Strike/Mongoose Bite makes your next ranged shot instant, free, and deal 50% bonus damage. |
| Survivalist's Bounty | Kills/Overkills drop scraps that heal you and your pets for 15% max health when walked over. |
| Chain Reaction | Triggering an Explosive Trap instantly resets Frost and Nature trap cooldowns. |
| Venomous Barbs | Multi-Shot and Volley instantly apply Serpent Sting to all targets hit. |
| Trapper's Net | Freezing Trap roots enemies within 8 yards and increases their physical damage taken by 20%. |
| Rexxar's Legacy | Dual-wielding melee weapons grants 20% ranged haste; 2H weapons grant 30% ranged crit damage. |
| Spirit Bond Override | Damage is split evenly between you and active pets; overhealing is shared bidirectionally. |
| Wyvern's Torment | Wyvern Sting deals heavy Nature damage every time the target is struck instead of sleeping them. |
| Stampeding Retreat | Disengage summons 3 spectral beasts that charge forward to damage and knock down enemies. |
| Beast Whisperer | Tame Beast is instant/usable in combat. Tamed beasts keep elite health/damage modifiers for 60s. |
| Wildfire | Explosive/Immolation traps ignite the ground, granting pets +30% attack speed and adding Fire damage to shots. |
| Apex Predator | Killing marked enemies resets the cooldown of Disengage, Kill Shot, and Bestial Wrath. |
| Camouflage | Standing still 3s out of combat grants stealth. First attack from stealth is a guaranteed crit and applies Mark. |
| Chimera's Evolution | Dealing elemental damage grants pets a matching elemental aura that damages nearby enemies. |

### Limit Break: The Apex Hunt

Deals 150% max HP as Physical/Nature damage to the primary target and 60% to surrounding enemies. Instantly summons three additional pets from the stable for 10 seconds, triggering free Kill Commands from the entire pack. Grants Bestial Wrath to all pets and yourself, removes Trap Launcher's cooldown/mana cost, and makes all casted shots instant.

### Legendary Capstone

**Legacy of the Sunwell (Requires Thori'dal, the Stars' Fury):**
Auto-Shots deal unmitigated Arcane damage. Steady Shot becomes Solar Pierce (40-yard Arcane piercing beam). Explosive Trap becomes Sunwell Singularity (gravity well that traps enemies; shooting it duplicates the shot to all trapped targets). Constellation Pack passive converts pets to astral forms dealing Arcane/Fire damage that teleport to targets hit by your Arcane arrows.

**Limit Break (Fury of the Stars):** 150% max HP Arcane/Fire orbital strike. 10-second eclipse merges pets into an invincible Celestial Spirit, grants levitation (move while casting), 200% ranged haste, and causes every arrow to call down a delayed Fire meteor on the target.

---

## Death Knight (The Lich King)

*Note: This section is design-only. Unlike Paladin and Mage, there is no shipped `mod-deathknight-powers` catalog yet; the design text stands as the behavioral reference.*

### Core Powers

These nine are available to every Death Knight regardless of archetype. Each one
hangs off runes, Runic Power, Death Grip, Presences, or staying alive -- the parts
of the class that do not change with the choice made at level 64. 

| Level | Power | Effect |
| ---: | --- | --- |
| 55 | Master of Death | Spending one rune from each base slot type -- Blood, Frost, and Unholy -- within 10 seconds completes a Rune Trinity. The three spent slots return as Death Runes when they refresh. A Death Rune still counts as its slot's base type for Trinity and later powers. Spending one of the three converted runes reduces the cooldown of the other two by 1 second. |
| 56 | Grip of the Citadel | Death Grip pulls 3 additional enemies. Cooldown resets when an enemy dies near you. |
| 57 | Plaguebringer | Applying Blood Plague or Frost Fever instantly applies both. Icy Touch against a target carrying both forces Blood Plague to tick and spreads it to the nearest uninfected enemy; Plague Strike does the same with Frost Fever. Triggered ticks cannot trigger Plaguebringer again. |
| 58 | Defiling Aura | Death and Decay is an aura that attaches to you and moves as you move. |
| 59 | Runeblade's Hunger | Death Runes generate double Runic Power. Spending 40 Runic Power immediately finishes the cooldown of your oldest depleted Death Rune; excess Runic Power spent carries toward the next refresh. |
| 60 | Trinity of Anguish | Teaches Trinity Presence, a fourth Presence. It is one active Presence aura that grants the complete effects of Blood, Frost, and Unholy Presence simultaneously, including the matching Improved Presence talents and Subversion's Presence-based threat reduction. |
| 61 | Sate the Blade | Death Strike always heals for at least 15% of maximum health. True overhealing is stored in your runeblade, up to 30% of maximum health; the next Runic Power spender that damages an enemy consumes the store to deal that much Shadow damage split among enemies within 10 yards. Other Runic Power spending does not discard it. |
| 62 | Winter's Ward | Anti-Magic Shell absorbs 100% of incoming magic damage and records the amount absorbed, up to 100% of your maximum health. When it ends, the recorded amount becomes a physical absorb shield for 10 seconds. |
| 63 | Ascension of the Damned | Lethal damage instead leaves you at 1 health and entombs you in Icebound Fortitude for 6 seconds. You cannot act or be healed. If an enemy dies near you during the entombment, you break free at 50% health; otherwise the deferred death resolves when it ends. Once every 10 minutes. |

**Why these nine.** Master of Death preserves the rune puzzle instead of deleting
it. The reward comes from spending all three base types in a short sequence, and
Runeblade's Hunger then turns the resulting Death Runes into an acceleration
engine. Trinity of Anguish is core by the exact argument Elemental Cadence is for
Mages: it rewards all three specs at once, so it belongs to the unspecialised
class or to nobody. It is a fourth composite Presence rather than three native
Presence states; activating it replaces the current Presence exactly as any
other Presence cast does. Winter's Ward is core despite the Frost name because
Anti-Magic Shell is baseline to every Death Knight. Sate the Blade is the solo
sustain floor, but its overhealing is also ammunition, so choosing when to spend
Runic Power changes the next pull rather than merely producing a larger heal.

### Archetypes

At level 64 a Death Knight commits to one of three archetypes, each drawn from a
pair of the class's three specs. The pairs are the only three combinations of
three taken two at a time, so the set is complete by construction.

| Archetype | Specs | Identity |
| --- | --- | --- |
| Rimeguard | Blood + Frost | Attrition. Damage taken becomes inert Rime; active defenses plate it, strikes shape it, and Death Grip releases it as an Avalanche. |
| San'layn | Blood + Unholy | The harvest. Ghouls are a consumable resource — raised, fed on, sacrificed, re-raised. |
| Deathbringer | Frost + Unholy | Detonation. Diseases bank Doom; Howling Blast is the match. Kills yield Souls. |

#### Rimeguard (Blood + Frost)

| Level | Power | Effect |
| ---: | --- | --- |
| 64 | Rimeshell | 30% of unmitigated direct damage taken is banked as inert Rime, capped at 50% of your maximum health. Rime does not absorb damage until another power explicitly plates or spends it. |
| 65 | Blood of the Damned | Activating Vampiric Blood, Unbreakable Armor, or Icebound Fortitude activates all three and starts the longest of their cooldowns as a shared cooldown. |
| 66 | Glacial Advance | Chains of Ice also chains every enemy within 10 yards. Non-boss enemies are rooted for 2 seconds; bosses become Brittle for the same duration. Your first melee strike against each rooted or Brittle target shatters the effect for Frost damage to enemies within 8 yards. |
| 68 | Mirror of Ice | Dancing Rune Weapon duplicates your non-triggered Death Knight spells alongside melee strikes. Its copies cost no resources, cannot generate resources, and cannot trigger another power copy. |
| 69 | Frigid Plating | Icebound Fortitude plates you in your current Rime for its duration, turning the bank into a 1:1 absorb. Damage absorbed is stored as retaliation; your next Rune Strike consumes it to deal the exact value as Frost damage in a 10-yard cone. Unspent Rime returns to the inert bank when Icebound Fortitude ends. |
| 70 | Subzero Strikes | Frost Strike consumes 10% of current Rime to send a frontal wave dealing twice the amount consumed as Frost damage. Rune Strike instead consumes 10% to heal for the amount consumed and freeze the attacker's attack and casting speed by 30% for 6 seconds. Neither strike consumes Rime below 5% of maximum health. |
| 72 | Blood-Caked Ice | Death Strike consumes 20% of your current Rimeshell, adding that exact value to both its healing and its physical damage. |
| 74 | Frozen Marrow | Frigid Plating divides its stored retaliation into Frozen Marrow shards worth up to 5% of maximum health each, capped at 6 shards. Rune Strike launches every shard in its cone; Icy Touch launches one at a single target; Death Strike consumes all shards to add their value to its healing and returns half that value to inert Rime. |
| 76 | Avalanche | Reaching the Rimeshell cap Primes it instead of shattering automatically. Primed Rimeshell is reserved and cannot be spent by any other power. Your next Death Grip consumes the full bank, pulls all gripped enemies to its primary target, and deals the consumed value as Frost damage to enemies within 15 yards. |
| 78 | Permafrost | Glacial Advance leaves a 10-second ice trail between you and each target it shatters. Enemies crossing a trail are rooted for 2 seconds. Triggering Avalanche collapses every active trail into its target, repeating 50% of that trail's shatter damage before the Rimeshell payout. |
| 80 | Citadel's Bastion | Rimeshell's cap rises to 100% of maximum health. Reaching 50% forms a moving ice citadel that remains until Rime is empty or Primed. Each base-slot rune ability consumes Rime equal to 5% of maximum health: Blood heals you and nearby allies for 10%, Frost deals the same as cleave damage, and Unholy raises an 8-second skeletal defender that explodes for the same amount, up to 3 defenders. Further defenders refresh the oldest. |

**Why these eleven.** The archetype is attrition, but the bank is not passive
armor. Rimeshell catches the memory of incoming damage and presents competing
ways to spend it: Icebound Fortitude plates it, Frost Strike turns it into area
damage, Rune Strike turns it into recovery and control, Death Strike spends a
larger share on one decisive hit, and Death Grip cashes out a full bank as
Avalanche. Priming at the cap is deliberate rather than automatic, so a player
can position a pack and choose the detonation. Frozen Marrow makes lost Bone
Shield charges another split decision, while Permafrost makes the route through
a pull matter. Citadel's Bastion is the endpoint: base rune types that Master of
Death taught the player to sequence now choose what the stored damage becomes.

#### San'layn (Blood + Unholy)

| Level | Power | Effect |
| ---: | --- | --- |
| 64 | Scourge Commander | Raise Dead requires no corpse, has no duration, and musters 3 Ghouls. One may occupy the native controllable pet slot; the others are AI guardians that follow its target and the Death Knight's commands. |
| 65 | Fodder to the Flame | Death Pact has no cooldown and sacrifices a Ripe Ghoul first, then the lowest-health Ghoul, restoring 30% health. A Scourge Commander Ghoul sacrificed this way begins a 10-second respawn timer. |
| 66 | Corpse Explosion Overload | When Ghouls die, are sacrificed, or expire, they auto-cast Corpse Explosion. |
| 68 | Blood Beast | Blood Strike causes all active Ghouls to frenzy, increasing their attack speed by 50% and causing their next 3 strikes to heal you. |
| 69 | Crimson Harvest | True self-overhealing is divided among your injured Ghouls. A Ghoul restored to full this way becomes Ripe for 15 seconds; sacrificing a Ripe Ghoul doubles its Corpse Explosion and immediately refreshes one depleted rune. |
| 70 | Dark Transformation | Sacrificing a Ghoul grants the remaining Ghouls 20% increased size and damage for 15 seconds. Stacks up to 3 times. |
| 72 | Vampiric Communion | Fifteen percent of Physical and Shadow damage dealt by you and your Ghouls fills a shared Blood Chalice, capped at 50% of your maximum health. Blood Boil empties the Chalice to heal the Ghoul pack; Death Strike empties it into its target, adding the stored value to both damage and healing. |
| 74 | Army of the Damned | Army of the Dead is instant, costs no runes, and summons 15 Ghouls for 20 seconds. |
| 76 | Meat Shield | Fatal damage is deferred while Ghouls remain. Ghouls sacrifice themselves one at a time, each erasing damage equal to 15% of your maximum health, until the hit is no longer fatal or none remain. These sacrifices trigger Corpse Explosion Overload and normal respawn timers, but not Fodder to the Flame's 30% heal. |
| 78 | Feast of Souls | Corpse Explosion Overload leaves a Feast at the corpse for 10 seconds, storing 50% of its damage dealt. Blood Boil consumes every Feast to immediately respawn missing Scourge Commander Ghouls; Death Strike consumes them instead to add the stored total to its healing. |
| 80 | Blood Queen's Blessing | Scourge Commander now musters 5 Ghouls. Fodder to the Flame grants a 15-second stack of the Blessing, increasing damage by 15% per stack, up to 20 stacks (300%). At 20 stacks you become the Blood Queen for their remaining duration: you hover, your attacks cleave enemies within 15 yards, and each attack raises a temporary Ghoul for 6 seconds, up to 20. Beyond that cap, an attack makes the oldest cast Corpse Explosion and reform at the target. |

San'layn is the canonical WoW name for vampiric undead, so Blood plus Unholy
names itself.

**Why these eleven.** The harvest. Ghouls are a consumable resource rather than
a pet you preserve forever, but the order and condition of the harvest matter.
Scourge Commander supplies the standing crop, Crimson Harvest rewards feeding a
Ghoul until it is Ripe, and Fodder harvests that Ghoul before falling back to the
weakest. Dark Transformation pays the survivors. Vampiric Communion adds a
second cash-out decision between Blood Boil for the pack and Death Strike for
the Death Knight. Meat Shield is an emergency consumer with explicit precedence,
while Feast of Souls lets the same explosions either replant the pack or heal
its commander. Blood Queen's Blessing keeps the requested extreme ceiling, but
20 stacks is a real, representable cap and reaching it changes form and attack
behavior rather than only making a number larger.

**Implementation note:** Scourge Commander gets the Call of the Crusader
treatment. "No duration" means the standing pack does not expire on a timer,
not that it is an irrevocable state change. If the archetype goes dormant, every
Ghoul despawns and its respawn timer is discarded. Only one Ghoul may use the
native pet slot and pet bar. The rest are module-owned AI guardians in the
owner's controlled set; they mirror the primary Ghoul's attack target, or the
Death Knight's current victim when no controllable Ghoul exists. All powers here
are revocable under the dormancy rule.

#### Deathbringer (Frost + Unholy)

| Level | Power | Effect |
| ---: | --- | --- |
| 64 | Bank of Doom | Damage dealt by Blood Plague and Frost Fever is banked as Doom on that target, capped at 100% of its maximum health. Doom is target-owned and unique to its Death Knight caster. |
| 65 | Shattered Blood | Howling Blast immediately deals the remaining damage of your diseases, removes them, and consumes all Doom on each target as bonus Shadowfrost damage. Triggered copies cannot bank Doom or trigger another Shattered Blood. |
| 66 | Inevitable Doom | While both diseases are active, each rune ability forces them to tick immediately at 50% strength. After 6 forced ticks, your next Obliterate cannot be avoided, costs no runes, and leaves both diseases in place. |
| 68 | Reaper of Souls | Death Coil costs no Runic Power against targets below 35% health and brands them for 5 seconds. If a branded target dies, your oldest depleted rune refreshes as a Death Rune; if none is depleted, the next rune you spend refreshes immediately as a Death Rune. If the target survives, the Death Coil's damage is added to its Doom instead. |
| 69 | Crown of Domination | Obliterate or Scourge Strike crowns the target for 8 seconds. Auto-attacks against the crowned target send a 15-yard Shadowfrost wave. Death Grip used on it instead pulls you to the target and grants movement-impairment immunity for 4 seconds. |
| 70 | Endless Night | Summon Gargoyle lasts indefinitely while draining 5 Runic Power per second. |
| 72 | Souls of the Damned | Killing an enemy, or detonating Doom worth at least 20% of its maximum health, grants one Soul. One death or detonation can grant at most one Soul, and you may hold up to 100. |
| 74 | Impending Doom | Icy Touch and Plague Strike each carve 10% of the target's current Doom into a floating Omen, reducing its bank by that amount. You may hold 4 Omens. Your next Runic Power spender releases them at its target as Shadowfrost damage, preserving banked damage when you switch targets. |
| 76 | Epidemic of Doom | Pestilence spreads your diseases and divides the source's current Doom evenly among every affected target, including the source. The total Doom before and after the spread is identical. |
| 78 | Soul Reaper's Scythe | Toggle. While drawn, Obliterate consumes up to 10 Souls and gains 5% additional Shadowfrost damage per Soul. If it kills the target, the consumed Souls return and the next Obliterate within 10 seconds costs no runes. While sheathed, Obliterate spends no Souls. |
| 80 | Herald of the Damned | Soul Reaper's Scythe becomes Soul Command, an off-global-cooldown spell with a 3-second cooldown that cycles Reap, Sustain, and Detonate. Reap enables the Scythe. Sustain lets Endless Night drain 1 Soul per second only while Runic Power is empty. Detonate lets the next Shattered Blood consume up to 25 Souls for 2% additional Doom detonation per Soul, then returns to Reap. Only the selected mode may spend Souls. |

**Why these eleven.** Detonation. Diseases are no longer just DoTs; they are
timers feeding Doom, and every button asks what to do with the timer. Rune
abilities accelerate it, Howling Blast detonates it, Icy Touch and Plague Strike
make part of it portable, and Pestilence trades one large bomb for a conserved
field of smaller ones. Nothing duplicates the bank. Reaper of Souls turns the
execute window into a wager rather than free damage: kill the brand to refresh a
Death Rune, or fail and feed Doom. Souls begin four levels later and become a
deliberate Obliterate resource at 78. At 80 Soul Command makes the choice
explicit: Reap spends through Obliterate, Sustain spends only after the Gargoyle
empties Runic Power, and Detonate arms one large disease explosion. Remorseless
Winter locks Runic Power rather than Souls, so even Sustain mode keeps the
stockpile intact during the Limit Break.

#### UI Needs
Each tree introduces authoritative state that has to be visible in `PPS_UI`.
Rune Trinity's three marks, Runeblade's Hunger progress, Rimeshell, Frozen
Marrow, the Blood Chalice, standing and respawning Ghouls, Blood Queen's
Blessing, Sate the Blade's store, Omens, Souls, Soul Command's mode, and
Frostmourne's stored Shades are player-owned readouts with independent movers
in the player HUD group. Doom, Inevitable Doom's forced tick count, and
Frostmourne's active Shade belong to the selected target and therefore use
independent movers in the target HUD group. The server owns every value; the
addon observes them through `mod-ui-bridge` rather than reconstructing banks
from the combat log.

### Limit Breaks

One per archetype, and unreachable from the other two. A Death Knight who never
chose an archetype has no Limit Break at all.

#### Rimeguard: Killing Frost
Deals 150% maximum health as Frost damage to the primary target and 60% to
enemies within 20 yards. Blood of the Damned triggers, Rimeshell's cap rises to
300% of maximum health for 10 seconds, and the bank is immediately filled and
locked: normal powers cannot spend it and Avalanche cannot trigger early. Every
direct hit splinters the locked shell without reducing it, dealing 10% of the
hit as Frost damage to enemies within 10 yards. When Killing Frost ends, the
shell unlocks and immediately triggers Avalanche at its full remaining value,
centered on your current target without requiring Death Grip.

#### San'layn: Pact of the Darkfallen
Deals 150% maximum health as Shadow damage to the primary target and 60% to
enemies within 20 yards. For 10 seconds, you drain 10% maximum health per second
from all enemies within 30 yards. Every tick of drain from every enemy raises a
temporary AI Ghoul at that enemy, up to 30 Limit Break Ghouls at once. Beyond
the cap, each new spawn causes the oldest to cast Corpse Explosion and reforms
it at the new target with a fresh duration. Death Pact has no global cooldown
for the duration, and sacrifices always choose temporary Ghouls before the
standing Scourge Commander pack. The harvest moves through the room instead of
growing without bound.

#### Deathbringer: Remorseless Winter
Deals 150% max HP as Shadowfrost damage to the primary target and 60% to enemies
within 20 yards. A 30-yard blizzard freezes non-boss enemies for 10 seconds and
reduces bosses' movement, attack, and casting speed by 50%; damage breaks neither
effect. Runic Power is locked at 100, so even Sustain mode never reaches its
Soul-payment fallback. Endless Night's Gargoyle casts 100% faster, every melee
strike calls a spectral Val'kyr, and every forced disease tick banks twice its
damage as Doom. The final second casts Shattered Blood without consuming Souls.

### Legendary Capstone

**Dominion of Frostmourne (Requires Frostmourne):**
Death Grip becomes Soul Harvest: it keeps its normal movement behavior and tears
a hostile Shade from the primary target for 15 seconds, limited to one active
Shade per target; harvesting it again refreshes the Shade. It attacks its owner
and repeats 30% of the damage you deal to that owner. If the owner dies while
its Shade exists, Frostmourne stores the Shade, up to 20. Shade repeats use a
dedicated combat-log spell, can critically strike, and cannot trigger another
copy or any power except the archetype behavior explicitly defined below.

Obliterate becomes Soulrend. When Frostmourne holds a Shade, Soulrend spends one
to repeat 50% of the strike against every enemy within 15 yards; if it kills its
primary target, the spent Shade returns to Frostmourne. Army of the Dead becomes
Halls of Reflection: it is instant and consumes every stored Shade to release
them as AI guardians for 20 seconds. They do not return when the guardians die
or expire. Soulrend's repeated strikes cannot generate resources or trigger
power procs.

The Shades learn from the active archetype. Rimeguard Shades add 30% of their
damage to Rimeshell. San'layn Shades count as temporary Ghouls for Blood Beast,
Dark Transformation, Corpse Explosion Overload, and Feast of Souls, and Death
Pact chooses them before the standing pack. Deathbringer Shades force Blood
Plague and Frost Fever to tick when they strike, banking the tick as Doom without
generating Souls. With no archetype active, Shades retain only their base attacks.
Stored Shades persist between combats while Frostmourne remains equipped;
unequipping it releases all stored and active Shades.

**Limit Break (Fury of Frostmourne):** Deals 150% maximum health as Shadowfrost
damage to the primary target and 60% to enemies within 30 yards, then tears and
immediately stores one Shade from every enemy hit until Frostmourne reaches its
20-Shade cap. For 10 seconds all stored Shades manifest without being consumed,
one Shade repeats each rune or Runic Power ability at 50% effect, and Soulrend
spends no Shades. These repeats cost and generate no resources and cannot trigger
another copy. When the window ends, every surviving Shade strikes its owner, or
your current target if its owner died, then returns to Frostmourne.

---

## Druid (The Primalist)

### Class Powers

| Power | Effect |
| --- | --- |
| Fluid Shapeshifter | Shapeshifting triggers no GCD, costs no mana, and generates 20 Energy or 10 Rage. |
| Nature's Arsenal | Cast Healing Touch, Rejuvenation, and Lifebloom in Cat or Bear form. |
| Lunar Claws | Mangle/Shred deal bonus Arcane damage based on Spell Power. Combo points restore 1% max mana. |
| Ursine Storm | Swipe (Bear) and Lacerate call down Hurricane bolts on targets struck. |
| Eclipse Momentum | Shifting into Cat grants Solar Eclipse; shifting into Bear grants Lunar Eclipse (6s duration). |
| Blood of the Earth | Taking direct damage in Bear form has a 50% chance to apply Lifebloom to yourself. |
| Sunfire Bite | Ferocious Bite consumes Moonfire/Insect Swarm for an instant AoE Fire blast. |
| Grasping Roots | Entangling Roots becomes an aura, rooting enemies within 10 yards every 3s and causing a Nature bleed. |
| Symbiotic Strikes | Melee crits have a 20% chance to cast a free, instant Wrath or Starfire. |
| Barkskin Overload | Barkskin explodes, knocking back enemies and dropping an Efflorescence healing patch. |
| Typhoon Pounce | Feral Charge triggers a Typhoon on impact, isolating the primary target. |
| Wild Growth Spores | Physical bleed ticks have a 15% chance to release spores that heal you for the tick's damage. |
| Cyclone Vortex | Cyclone suspends targets but breaks if they lose 20% of their maximum health. |
| Tidal Roar | Savage/Demoralizing Roar cast a mobile Tranquility on you for 4 seconds. |
| Moonkin's Fortitude | Moonkin form grants the armor multiplier and parry chance of Bear form. |
| Apex Predator | Cat finishing moves reset the cooldown of Mangle (Bear), Enrage, and Charge. |
| Astral Swipe | Swipe (Cat) deals unmitigated Arcane damage and restores 5 Energy per target hit. |
| Fungal Bloom | Enemies dying with Insect Swarm explode into toxic mushrooms that heal you and damage enemies. |
| Chimera's Wrath | Starfall is usable in any form. While active, physical attacks ignore 50% armor. |
| Heart of the Wild | Permanently retain passive benefits of all forms (Armor, AP, Spell Power, Healing) simultaneously. |

### Limit Break: The Emerald Cataclysm

Deals 150% max HP as Astral (Arcane/Nature) damage via ethereal roots. Overgrows the 30-yard area with thorns that damage and silence moving enemies. Transforms you into Avatar of Ysera for 10 seconds: 0 resource costs, 0 cast times, and all DoTs/Bleeds tick every 0.5 seconds.

### Legendary Capstone

**Defiance of the Forest Lord (Requires Axe of Cenarius):**
Permits 2H Axes. Swipe becomes Broxigar's Cleave (20-yard frontal cone applying Astral Hemorrhage DoT). Shred/Mangle become Emerald Severance (ignores 100% armor, unblockable/unparryable, interrupts and locks out spellcasting). Heart of the World Tree passive plants Treant seeds on melee crits that emerge to fight and cast free Healing Touches.

**Limit Break (Wrath of the Ancients):** 150% max HP Astral strike. Massive roots suspend enemies for 10s. Transforms you into Avatar of Broxigar (humanoid, 200% melee haste) where every Axe strike on a rooted enemy triggers an AoE Starfire explosion.

---

## Rogue (The Phantom)

### Class Powers

| Power | Effect |
| --- | --- |
| Phantom's Ledger | Combo points are stored on you, not the target, and do not drop on target switch. +20% Energy regen. |
| Twin Venoms | Applying Deadly/Instant Poison automatically applies Wound/Mind-Numbing Poison. |
| Shadowstep Chain | Killing within 5s of Shadowstep resets its cooldown and refunds 30 Energy. |
| Crimson Tempest | Fan of Knives consumes combo points to apply a massive, stacking physical AoE bleed. |
| Acrobatic Deflection | Evasion grants 100% Parry; parrying automatically fires a free throwing knife at the attacker. |
| Assassinate | Ambush is usable out of stealth on targets below 35% health (generates 2 combo points). |
| Toxic Fumes | Rupture releases toxic gas dealing AoE Nature damage within 8 yards. |
| Blade Vortex | Blade Flurry becomes a toggled aura (drains 10 Energy/sec) that cleaves 4 nearby enemies. |
| Vampiric Toxins | Envenom heals you for 50% of the Nature damage it deals. |
| Smoke Bomb | Vanish drops a 10-yard smoke cloud for 6s; you remain stealthed inside while dealing damage. |
| Expose Weakness | Expose Armor applies 5 stacks instantly and increases poison/bleed damage taken by 15%. |
| Cheat Death Override | Cheat Death grants 100% Leech for its 3-second duration. |
| Preparation's Reward | Preparation grants 10 seconds of 0 Energy / 0 Combo Point finishing moves. |
| Nightmare Strike | Hemorrhage deals Shadow damage; increases next finisher damage by 10% per active combo point. |
| Sleight of Hand | Pick Pocket (usable in combat) interrupts spellcasting and steals one beneficial buff. |
| Shadow Dance Mastery | Entering Stealth/Shadow Dance guarantees next attack is a crit that ignores 100% armor. |
| Cloak of Shadows Overload | Expires in a violent explosion dealing Shadow damage equal to the magic damage absorbed. |
| Lethality | Eviscerate crits for 300% damage; killing a target makes your next ability free. |
| Blade Cascade | Killing Spree drops a static clone that casts its own Killing Spree on a secondary target. |
| The Unseen Hand | At 5 combo points, auto-attacks have a 20% chance to trigger a free 5-point Eviscerate. |

### Limit Break: Murder of Crows

Deals 150% max HP Physical/Shadow damage. You vanish into a damage-immune eclipse for 5 seconds while 10 shadow-clones rapidly teleport and spam Ambush/Fan of Knives on all enemies. Reappear with 100% Energy and 5 combo points.

### Legendary Capstone

**Legacy of the Betrayer (Requires Warglaives of Azzinoth):**
Sinister Strike/Hemorrhage become Fel Cleave (arcs to 2 extra enemies, 50% unresistable Fire damage). Deadly Throw/Fan of Knives become Twin Glaive Toss (20-yard spinning boomerang arc). Slice and Dice becomes Flames of Azzinoth (summons Fel fire elementals that pulse AoE Fire damage and hold aggro).

**Limit Break (Metamorphosis):** 150% max HP Chaos damage eruption. Transform into Illidan's demonic form for 10s: permanent Sprint, CC immunity, 100% Leech, 15-yard ranged Fel auto-attacks, and kills/crits reset Shadowstep and Twin Glaive Toss.

---

## Shaman (The Stormweaver)

### Class Powers

| Power | Effect |
| --- | --- |
| Totemic Aura | Totems are permanent, damage-immune auras that orbit and move with you. |
| Elemental Weaving | Melee crits increase next spell damage by 50%. Spell crits grant +30% melee haste for 2 swings. |
| Storm's Embrace | Lightning, Water, and Earth Shields run simultaneously and never lose charges. |
| Crash of Thunder | Stormstrike detonates active Flame Shocks as AoE Fire damage and reapplies Earth Shock. |
| Earthen Bulwark | Earth Shock grants a physical absorb shield equal to 100% of damage dealt. |
| Lava Lash Overload | Consumes Fire Totem power to grant melee attacks 100% Fire splash damage for 6s. |
| Tidal Surge | Riptide has no cooldown. Self-casting grants 10% stacking melee/spell haste (up to 30%). |
| Maelstrom Nexus | Maelstrom stacks to 10. At 10 stacks, Lightning Bolt/Chain Lightning is instant, free, and casts twice. |
| Chain Reaction | Chain Lightning has no cooldown and damage *increases* by 15% per jump. |
| Vampiric Tides | Healing Stream Totem heals you for 50% of all Nature and Frost damage dealt. |
| Ancestral Guardian | Feral Spirit wolves are permanent and echo your self-heals with restorative waves. |
| Frostbrand's Bite | Frostbrand freezes targets for 3s; hitting frozen targets with Fire spells shatters them for AoE damage. |
| Magma Eruption | Earth/Fire spell casts cause Magma Totem to erupt, knocking enemies up for AoE damage. |
| Windfury Hurricane | Windfury triggers off offensive spell casts, firing phantom melee strikes. |
| Lava Burst Ricochet | Lava Burst automatically chains to all secondary targets afflicted by Flame Shock. |
| Grounded Lightning | Grounding Totem absorbs spells for 4s, firing a supercharged Lightning Bolt equal to absorbed damage. |
| Bloodlust Momentum | Lasts 15s (2min CD, no Sated); every kill extends duration by 1s. |
| Astral Shift Override | Dropping below 30% HP enters the spirit world for 4s (physical immunity, heals 10% max HP/sec). |
| Thunderstorm Singularity | Violently pulls all enemies within 30 yards to your location, roots them, and applies a Nature bleed. |
| Avatar of the Elements | Fire/Earth Elementals can be active simultaneously alongside your Totemic Aura. |

### Limit Break: Ascendance

Deals 150% max HP Elemental damage amidst a localized hurricane/earthquake. Transform into an Ascendant for 10 seconds: complete CC immunity, 30-yard melee reach throwing wind/fire blades, and every melee strike triggers a free uncapped Chain Lightning on all engaged enemies.

### Legendary Capstone

**Legacy of the Firelord (Requires Sulfuras, Hand of Ragnaros):**
Stormstrike becomes Sulfuron Smash (250% weapon Fire damage, leaving a 10-yard magma crater that slows/damages). Feral Spirit becomes Sons of Flame (4 fire elementals that seek Flame Shock targets and explode). Windfury's Ignition changes Windfury to guarantee the next Lava Burst is instant, free, and fires alongside the melee swing.

**Limit Break (By Fire Be Purged!):** 150% max HP Fire damage lava eruption. Battlefield becomes a magma caldera (Fire/Physical immunity). Grow to raid-boss size with 40-yard melee reach; Sulfuron Smash has no cooldown and launches traveling walls of fire across the arena.
