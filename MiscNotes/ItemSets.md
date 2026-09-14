Status: 125 of 148 entries authored into mod-source-item-sets (500 of 592 sets).
--------------------
    Eastern Kingdoms  25/25    Outland   7/7    Northrend  9/9
    Kalimdor          19/19    Dungeons 64/65    Raids      1/23

The only source entry not authored is The Headless Horseman, which has no source
to attach to -- see the note on its entry. Upper Blackrock Spire was added during
implementation because the module generates a set for it that this document
never covered.

Molten Core is the first authored raid: its four sets are live in
AUTHORED_SETS, SourceSetPrograms.cpp, and the generated SQL. The remaining 22
raid sources, 88 sets, still carry generated placeholder names and bonuses.
The rest of the Raids section is the design for those future passes; its four
threshold model (2, 4, 6, and 8) is not yet emitted by the current generator.
Molten Core's 6- and 8-piece lines below are therefore design-only: its
[Implemented] marks cover the set names and currently emitted 2/4 bonuses.

Quality runs a step above ordinary loot, because these sets are the reward for a
whole source rather than one drop off one creature: world sets are rare,
dungeon sets epic, raid sets legendary. Item level follows quality, so at a
level-80 source that is 170 / 200 / 284 -- the world band, the dungeon blue band,
and Shadowmourne. The current generator emits two thresholds (2 and 4) for every
set; the four-threshold raid design is documented below for a future expansion.

Authored means the name and both bonuses are live in the module's AUTHORED_SETS
table, the generator emits them with no drift, and SourceSetPrograms.cpp
compiles. Everything not yet authored still carries a generated placeholder
bonus. The generator is the source of truth if it and this document disagree.

The [Implemented] mark is stricter than "authored": it is only added once the
change has also survived a full worldserver link, because five real bugs in this
work were found at the link and SQL boundaries after the module itself compiled
clean. The marks are generated from AUTHORED_SETS rather than edited by hand, so
the document and the generator cannot drift apart.

Nothing here has been verified in game yet -- only that it builds, links,
generates, and emits the intended SQL.

Some bonuses were reworded where the original named a mechanic WotLK cannot
express (cast-time changes, foreign-spell scaling, creature types that do not
exist in 3.3.5). Each rewrite is recorded in ImplementedChanges.md.

Eastern Kingdoms
--------------------
Dun Morogh - Levels: 1-10
- Cloth - New Tinkertown Refugee [Implemented]
    Flavor: "Everything they salvaged from Gnomeregan fit in one pack. The pack was, of course, larger on the inside."
    (2) Set: Killing an enemy slows the movement speed of all nearby enemies by 20% for 4 sec.
        - Note: Nearby what? The player or the enemy? What range is considered "nearby"?
    (4) Set: When your health drops below 20%, you are shielded for 15% of your maximum health. (Can only occur once every 60 sec.)
- Leather - Grizzlepaw Ridgerunner [Implemented]
    Flavor: "The ridge is faster than the road, if you do not mind the bears."
    (2) Set: Striking an enemy that hasn't noticed you deals 30% extra damage and reduces their chance to hit you by 20% for 3 sec.
    (4) Set: While moving, you gain 10% dodge chance and take 20% less damage from Beasts.
- Mail - Coldridge Trapper [Implemented]
    Flavor: "The Frostmane learned to watch the snow for wire. They never learned to watch the trees."
    (2) Set: You deal 15% more damage to Humanoids.
    (4) Set: Killing a Humanoid restores 10% of your maximum health.
- Plate - Kharanos Garrison [Implemented]
    Flavor: "Ale in the tankard, ice in the beard, and not one step back."
    (2) Set: Frost effects and movement-slowing spells affect you 50% less.
        - Note: Wording should be "You take 50% less damage from Frost effects and movement-slowing spells last 50% shorter."
    (4) Set: Each consecutive second you remain in melee combat increases your damage reduction by 2%, up to 20%.

Elwynn Forest - Levels: 1-10
- Cloth - Northshire Acolyte [Implemented]
    Flavor: "The Light answers those who stand still long enough to listen."
    (2) Set: After you kill an enemy, your next spell costs no mana.
    (4) Set: Stand still for 3 seconds and the Light shields you for 10% of your maximum health. Standing still another 3 seconds renews it.
- Leather - Fargodeep Poacher [Implemented]
    Flavor: "The kobolds never hear you coming. Neither did the deer."
    (2) Set: Striking an enemy that hasn't noticed you deals 30% extra damage.
    (4) Set: Killing an enemy grants 20% movement speed for 6 seconds.
- Mail - Eastvale Woodsman [Implemented]
    Flavor: "The loggers of Eastvale learned to fell more than trees."
    (2) Set: You deal 15% more damage to Beasts.
    (4) Set: Killing a Beast restores 10% of your maximum health.
- Plate - Westbrook Watch [Implemented]
    Flavor: "The Riverpaw test the bridge nightly. They have yet to cross it."
    (2) Set: Your first strike against an enemy deals 25% extra damage.
    (4) Set: While three or more enemies are within 8 yards, you take 15% less damage.

Eversong Woods - Levels: 1-10
- Cloth - Falthrien Adept [Implemented]
    Flavor: "The Academy's first lesson: magic taken is magic owed."
    (2) Set: Your spell criticals restore 3% of your maximum mana.
    (4) Set: Taking critical damage grants 15% increased spell damage for 6 sec.
- Leather - Farstrider Scout [Implemented]
    Flavor: "A Farstrider who is bleeding has already made a mistake."
    (2) Set: Dodging an attack increases your attack speed by 15% for 5 sec.
    (4) Set: While above 90% health, your critical strike chance is increased by 5%.
- Mail - Windrunner Handler [Implemented]
    Flavor: "Three sisters carried the name. Every hunter in Eversong still tries to earn it."
    (2) Set: Attacking an enemy below 20% health deals 20% additional damage.
    (4) Set: Your ranged attacks reduce the target's movement speed by 10% for 4 sec. Cannot occur more than once every 16 sec.
- Plate - Blood Knight Initiate [Implemented]
    Flavor: "The Light does not give. The Blood Knights simply stopped asking."
    (2) Set: Melee attacks against Undead heal you for 2% of your maximum health.
    (4) Set: Taking melee damage grants 2% increased armor for 5 sec, stacking up to 5 times.

Tirisfal Glades - Levels: 1-10
- Cloth - Deathknell Mourner [Implemented]
    Flavor: "You wept at this graveside once. Now you work it."
    (2) Set: When an enemy dies within 10 yards, you recover 3% of your maximum health and mana.
    (4) Set: Enemies that die within 10 yards erupt in plague, dealing Shadow damage to other enemies within 8 yards equal to 15% of the slain enemy's maximum health.
- Leather - Nightweb Stalker [Implemented]
    Flavor: "Patience first, then venom. The Hollow's spiders teach nothing else."
    (2) Set: Your melee attacks apply Venom, dealing Nature damage over 6 sec and stacking up to 5 times.
    (4) Set: An enemy at 5 stacks of Venom is webbed, reducing its movement speed by 50% and causing it to take 10% increased damage from you.
- Mail - Agamand Reaver [Implemented]
    Flavor: "The Agamands held this mill in life. Death did not loosen their grip."
    (2) Set: Each consecutive melee attack against the same target deals 5% more damage, up to 25%. Switching targets resets the bonus.
    (4) Set: Dropping below 35% health enrages you, increasing your melee damage by 20% for 8 sec. (Can only occur once every 45 sec.)
- Plate - Bulwark Deathguard [Implemented]
    Flavor: "Every Deathguard on this wall has died once already. The Scourge find them hard to impress."
    (2) Set: You deal 15% more damage to Undead and take 10% less damage from them.
    (4) Set: Your armor is increased by 5% for each enemy within 8 yards, up to 25%.

Ghostlands - Levels: 10-20
- Cloth - Banshee Keener [Implemented]
    Flavor: "The banshees of the Ghostlands wail for the lost and the damned alike."
    (2) Set: Your spells reduce healing received by the target by 25% for 8 sec.
    (4) Set: While below 50% mana, your spell damage is increased by 15%.
- Leather - Elrendar Ambusher [Implemented]
    Flavor: "Tread lightly. Half of what hunts the Ghostlands died before you arrived."
    (2) Set: Attacks made from behind your target deal 15% additional damage.
    (4) Set: Killing an enemy grants 10% dodge chance for 16 sec, stacking up to 3 times.
- Mail - Suncrown Skirmisher [Implemented]
    Flavor: "No Windrunner would be caught dead wearing this armor."
    (2) Set: Enemies you strike take 8% increased damage from all sources for 6 sec.
    (4) Set: While below 50% health, your attacks heal you for 15% of the damage dealt for 16 sec. (Can only occur once every 60 sec.)
- Plate - Tranquillien Deathwarden [Implemented]
    Flavor: "Deatholme sends its dead out each night. Tranquillien counts its living each morning."
    (2) Set: Dodging, parrying, or blocking grants 5% increased damage for 4 sec, stacking up to 4 times.
    (4) Set: While within 5 yards of a corpse, your armor is increased by 20%.

Loch Modan - Levels: 10-20
- Cloth - Thelsamar Panner [Implemented]
    Flavor: "Even the cloth in Loch Modan feels like tough jerky." 
    (2) Set: Mining skill increased by 15.
    (4) Set: Mining a vein restores 5% of your maximum health and mana.
- Leather - Stonesplinter Prospector [Implemented]
    Flavor: "The bears are the easy part. It is the mud that ruins good leather."
    (2) Set: Mining a vein grants 20% movement speed for 10 sec.
    (4) Set: Ore veins yield one additional ore.
- Mail - Ironband Forgehand [Implemented]
    Flavor: "Everything forged near the Loch smells of copper and lake water. You stop noticing by the second week."
    (2) Set: Blacksmithing skill increased by 10.
    (4) Set: Every fifth item you craft with Blacksmithing yields one additional item.
- Plate - Dun Algaz Smelter [Implemented]
    Flavor: "Wearing Plate armor in the Loch may find yourself at the bottom of the lake."
    (2) Set: Your Mining skill counts as 25 higher when determining what you may smelt.
    (4) Set: Smelting produces one additional bar for every five bars smelted.

Silverpine Forest - Levels: 10-20
- Cloth - Sepulcher Mistweaver [Implemented]
    Flavor: "The mists of Silverpine Forest cling to even the softest cloth."
    (2) Set: Your first spell against an enemy slows its casting speed by 20% for 10 sec.
    (4) Set: While fighting two or more enemies, your spell critical strikes restore 2% of your maximum health.
- Leather - Fenris Isle Skinner [Implemented]
    Flavor: "Skinned wet, tanned wet, worn wet. Silverpine has no dry season."
    (2) Set: Your attacks cause the target to bleed for 15% of the damage dealt over 6 sec.
    (4) Set: You are healed for 20% of the damage your bleed effects deal.
- Mail - Forsaken Rearguard [Implemented]
    Flavor: "Oil it nightly or the damp takes it. Silverpine rusts everything, living or otherwise."
    (2) Set: Enemies fleeing from you take 30% additional damage.
    (4) Set: Fear effects on you last 50% less, and breaking free grants 20% attack speed for 6 sec.
- Plate - Pyrewood Warden [Implemented]
    Flavor: "Plate will keep the worgen out. Nothing keeps out the smell of wet earth and old blood."
    (2) Set: Enemies within 8 yards of you have their movement speed reduced by 15%.
    (4) Set: Killing an enemy terrifies enemies within 10 yards for 2 sec. (Can only occur once every 30 sec.)

Westfall - Levels: 10-20
- Cloth - Saldean's Farmhand [Implemented]
    Flavor: "Cut from grain sacks and dyed with beet water. Westfall makes do."
    (2) Set: Cooking skill increased by 10.
    (4) Set: Meat you loot from Beasts is doubled.
- Leather - Moonbrook Angler [Implemented]
    Flavor: "Every hide in Westfall belonged to something a farmer could not afford to lose."
    (2) Set: Fishing skill increased by 15.
    (4) Set: Fishing catches yield one additional fish.
- Mail - Gold Coast Digger [Implemented]
    Flavor: "The dust works into every ring and stays there. Consider it part of the armor."
    (2) Set: First Aid skill increased by 10.
    (4) Set: Bandages you craft yield one additional bandage.
- Plate - Sentinel Hill Provisioner [Implemented]
    Flavor: "Who knew that there even was Plate armor in Westfall, yet here it is."
    (2) Set: Your health and mana regeneration is increased by 50%.
    (4) Set: Remaining still for 5 sec grants a shield absorbing 10% of your maximum health for 1 min.

Redridge Mountains - Levels: 15-25
- Cloth - Burning Steppes Kindler [Implemented]
    Flavor: "With the Burning Steppes to the North, Winter never comes."
    (2) Set: Your Fire damage is increased by 15%.
    (4) Set: Remaining within 8 yards of an enemy for 5 sec ignites it, dealing Fire damage over 6 sec.
- Leather - Galardell Gnollskinner [Implemented]
    Flavor: "The gnolls wear the same hides. Best not to wonder where they got theirs."
    (2) Set: Your attacks deal 10% additional damage to enemies affected by a snare or root.
    (4) Set: Every third attack against the same target reduces its movement speed by 40% for 3 sec.
- Mail - Lakeshire Volunteer [Implemented]
    Flavor: "Stonewatch fell wearing mail like this. Lakeshire is still asking for volunteers."
    (2) Set: Enemies you strike are prevented from fleeing for 4 sec.
    (4) Set: While three or more enemies are within 10 yards, your attacks strike a second nearby enemy for 30% of the damage.
- Plate - Stonewatch Dragonguard [Implemented]
    Flavor: "Some say there are Dragons in the Redridge Mountains, I'm sure they appreciate you providing the oven."
    (2) Set: Enemies that strike you in melee take Fire damage equal to 5% of your armor.
    (4) Set: Holding position without moving for 5 sec increases your block and parry chance by 15% until you move.

Duskwood - Levels: 18-30
- Cloth - Darkshire Shroudweaver [Implemented]
    Flavor: "The shadows of Duskwood cling close to the cloth, as if the forest itself is watching."
    (2) Set: Your Shadow damage is increased by 15%.
    (4) Set: While at or below 50% health, your spells have 20% increased critical strike chance.
- Leather - Tranquil Gardens Prowler [Implemented]
    Flavor: "Are those eyes in the bushes? You'd better hope they're friendly."
    (2) Set: You move 10% faster out of combat and 5% faster in combat.
    (4) Set: Attacking an enemy already engaged with someone else deals 25% additional damage.
- Mail - Night Watch Sentinel [Implemented]
    Flavor: "Mail doesn't arrive often in Duskwood, wait, this isn't mail, it's armor!"
    (2) Set: Your attacks reduce the target's damage dealt by 5% for 8 sec, stacking up to 3 times.
    (4) Set: When an enemy dies within 10 yards, you gain 5% attack power for 10 sec, stacking up to 5 times.
- Plate - Yorgen Gravebreaker [Implemented]
    Flavor: "Some say an abomination roams the Duskwood, I wonder how that came together?"
    (2) Set: You suffer 20% less damage from Undead.
    (4) Set: While below 40% health, all healing you receive is increased by 30%.

Hillsbrad Foothills - Levels: 20-30
- Cloth - Southshore Loyalist [Implemented]
    Flavor: "Southshore will stand forever! So there will always be plenty of cloth armor!"
    (2) Set: Your spells deal 20% additional damage to enemies below 35% health.
    (4) Set: Killing an enemy reduces your active spell cooldowns by 2 sec.
- Leather - Syndicate Turncoat [Implemented]
    Flavor: "The Syndicate were nobles once. Now they cut purses in the dark and call it politics."
    (2) Set: Your damage is increased by 10% while no allies are within 15 yards.
    (4) Set: Striking an enemy from behind grants 20% movement speed for 4 sec.
- Mail - Old Benji's Ward [Implemented]
    Flavor: "Old Benji is proud of this armor, and he hopes it serves you well."
    (2) Set: Your attacks against enemies of higher level than you deal 15% additional damage.
    (4) Set: For each enemy that has struck you in the last 10 sec, gain 3% attack power, up to 15%.
- Plate - Ashbringer's Vigil [Implemented]
    Flavor: "There is a legend that long ago, a dark crystal was infused with the light in Southshore, and thus began the Ashbringer."
    (2) Set: Your maximum health is increased by 10% while in combat with more than one enemy.
    (4) Set: When you fall below 50% health, you and allies within 10 yards gain 10% damage reduction for 8 sec. (Can only occur once every 45 sec.)

Wetlands - Levels: 20-30
- Cloth - Marshtide Conjurer [Implemented]
    Flavor: "The crocolisks love when adventurers wear cloth armor, as it makes them easier to chew."
    (2) Set: Your Frost and Nature damage is increased by 15%.
    (4) Set: Enemies you have slowed take 15% additional damage from your spells.
- Leather - Raptor Ridge Tracker [Implemented]
    Flavor: "Raptor hide holds up in the wet. The difficulty is separating the raptor from it."
    (2) Set: Dodging an attack causes your next attack to deal 30% additional damage.
    (4) Set: Killing an enemy restores 5% of your maximum health and removes one movement-impairing effect.
- Mail - Harborwatch Squire [Implemented]
    Flavor: "The young squires of the wetlands cannot afford plate armor, so mail is their best option."
    (2) Set: Movement-impairing effects on you are 40% less effective.
    (4) Set: While moving, you take 15% less damage from ranged attacks and spells.
- Plate - Menethil Harbor Guard [Implemented]
    Flavor: "Most of the plate armor made in Menethil Harbor used to be made to match that of Young Arthas Menethil, though none like to admit it." 
    (2) Set: Your armor is increased by 10% while below 60% health.
    (4) Set: Enemies that strike you are slowed by 20% for 4 sec.

Alterac Mountains - Levels: 30-40
- Cloth - Alterac Ruins Exile [Implemented]
    Flavor: "Alterac was a kingdom once. Now it is a cold place where nobody asks your name."
    (2) Set: Your Frost damage slows the target's attack speed by 15% for 6 sec.
    (4) Set: If you have not taken damage in the last 6 sec, your spell critical strike chance is increased by 15%.
- Leather - Frosthide Trapper [Implemented]
    Flavor: "Yeti hide is warm, thick, and appalling when it thaws. Two of those are worth having."
    (2) Set: Your critical strikes deal 15% additional damage.
    (4) Set: Killing an enemy makes you untrackable and grants 30% movement speed for 5 sec.
- Mail - Prestor Houseguard [Implemented]
    Flavor: "The Prestor family lived in the Alterac Mountains, Lady Prestor has recently began advising the young King Anduin Wrynn."
    (2) Set: You take 25% less damage from Frost effects.
    (4) Set: Every 8 sec, your next attack deals an additional 40% damage and cannot be dodged.
- Plate - Strahnbrad Sentinel [Implemented]
    Flavor: "Some say there is a small village teaming with invisible foes, making plate armor essential for survival in the Alterac Mountains."
    (2) Set: While above 80% health, you deal 10% additional damage.
    (4) Set: Being struck by three or more different enemies within 5 sec grants a shield absorbing 20% of your maximum health. (Can only occur once every 60 sec.)

Arathi Highlands - Levels: 30-40
- Cloth - Stromgarde Ashweaver [Implemented]
    Flavor: "Stromgarde's weavers have been dead three generations. Their work still turns up in the rubble."
    (2) Set: Your damage over time effects deal 20% additional damage.
    (4) Set: Enemies you strike with a spell take 10% additional damage from all sources for 6 sec.
- Leather - Refuge Pointe Ranger [Implemented]
    Flavor: "Refuge Pointe trades for whatever the highlands give back. Most of it has been worn before."
    (2) Set: Your attacks have 10% increased critical strike chance against Humanoids.
    (4) Set: Your critical strikes grant 25% attack speed for 6 sec. (Can only occur once every 8 sec.)
- Mail - Rustfall Scavenger [Implemented]
    Flavor: "It smells of old rain and ash, like everything dragged out of Stromgarde."
    (2) Set: You suffer 10% less damage from spells.
    (4) Set: After killing an enemy, your next attack within 8 sec deals 40% additional damage.
- Plate - Stromgarde Pretender [Implemented]
    Flavor: "The last King of Stromgarde was said to have worn this armor, or that's what the peddler claimed."
    (2) Set: Your maximum health is increased by 5%.
    (4) Set: While below 35% health, you take 25% less damage and deal 15% less damage.

Stranglethorn Vale - Levels: 30-45
- Cloth - Grope Street Tailor [Implemented]
    Flavor: "Silk rots through in a week here. Buy two."
    (2) Set: Skinning skill increased by 10.
    (4) Set: Beasts you skin yield one additional piece of leather.
- Leather - Nesingwary Tracker [Implemented]
    Flavor: "Nesingwary pays by the pelt and has never once asked how you got it."
    (2) Set: Skinning a beast grants 20% movement speed for 10 sec.
    (4) Set: Your Skinning skill counts as 25 higher when determining what you may skin.
- Mail - Bloodscalp Tanner [Implemented]
    Flavor: "Rust is the second most common cause of death in Stranglethorn. The first has stripes."
    (2) Set: Leatherworking skill increased by 10.
    (4) Set: Every fifth item you craft with Leatherworking yields one additional item.
- Plate - Gurubashi Bloodguard [Implemented]
    Flavor: "The Gurubashi Arena has no rules and one prize. Wear something thick."
    (2) Set: Beasts yield 25% more meat and hide when looted.
    (4) Set: Beasts are always tracked on your minimap.

Badlands - Levels: 35-45
- Cloth - Sunblind Adept [Implemented]
    Flavor: "There is no shade in the Badlands. The robes are not for modesty."
    (2) Set: Your spells ignore 10% of the target's resistances.
    (4) Set: Your spell critical strikes reduce the target's armor by 10% for 10 sec, stacking up to 3 times.
- Leather - Scorpid-hide Ranger [Implemented]
    Flavor: "Scorpid hide, mostly. The buzzards get whatever the scorpids leave."
    (2) Set: You take 20% less damage from area effects.
    (4) Set: After not taking damage for 5 sec, your next attack deals 60% additional damage.
- Mail - Uldaman Prospector [Implemented]
    Flavor: "The diggers came up from Uldaman with sunstroke and ruined lungs. The armor was the only part worth keeping."
    (2) Set: You deal 15% additional damage to Dragonkin.
    (4) Set: Killing a Dragonkin grants 15% increased armor for 20 sec.
- Plate - Lethlor Bonewarden [Implemented]
    Flavor: "Lethlor Ravine is dragonkin and bleached bone. Most of the bone wore armor once."
    (2) Set: Your attacks ignore 10% of the target's armor.
    (4) Set: While at or above 90% health, your attacks deal 20% additional damage.

Swamp of Sorrows - Levels: 35-45
- Cloth - Bogrot Adept [Implemented]
    Flavor: "Mildew took the hem before you bought it. The Swamp has never sold anything new."
    (2) Set: Enemies within 8 yards suffer Nature damage equal to 1% of their maximum health every 3 sec.
    (4) Set: Enemies damaged by your toxic aura are slowed by 20%.
- Leather - Crocscale Hunter [Implemented]
    Flavor: "Crocolisk hide, cured in swamp water. It smells precisely as you would expect."
    (2) Set: Your attacks against Undead deal 15% additional damage.
    (4) Set: Killing an Undead restores 8% of your maximum health and mana.
- Mail - Stonard Garrison [Implemented]
    Flavor: "Stonard issues it and the swamp reclaims it. Nobody has ever handed a set back."
    (2) Set: You are immune to disease effects and take 15% less Nature damage.
    (4) Set: Falling below 50% health releases a toxic cloud, dealing Nature damage to enemies within 8 yards. (Can only occur once every 45 sec.)
- Plate - Atal'ai Sunken Guard [Implemented]
    Flavor: "The Atal'ai drowned their offerings in the Temple. Armor sinks faster than faith."
    (2) Set: Your armor is increased by 8% and you are immune to slowing poisons.
    (4) Set: Enemies that strike you rot, suffering Nature damage equal to 3% of your armor.

The Hinterlands - Levels: 40-50
- Cloth - Aerie Peak Windweaver [Implemented]
    Flavor: "Aerie Peak weaves for altitude, not fashion. You will be grateful at three thousand feet."
    (2) Set: Your spell damage is increased by 10%.
    (4) Set: Enemies more than 20 yards from you take 15% additional damage from your spells.
- Leather - Owlbeast Plumehunter [Implemented]
    Flavor: "Owlbeast down makes fine lining. Collecting it makes a fine story, if you live to tell it."
    (2) Set: You take no falling damage.
    (4) Set: Attacks made from above your target deal 20% additional damage.
- Mail - Wildhammer Skyguard [Implemented]
    Flavor: "Wildhammer smiths cut it light. A gryphon does not care how brave you are, only what you weigh."
    (2) Set: Your ranged attacks and spells deal 12% additional damage.
    (4) Set: Every 6 sec, your next ranged attack or spell strikes an additional nearby enemy for 40% of the damage.
- Plate - Jintha'Alor Headtaker [Implemented]
    Flavor: "Jintha'Alor is a thousand steps lined with heads. Climb it in something solid."
    (2) Set: Your armor is increased by 15% while at or above 75% health.
    (4) Set: Entering combat grants a shield absorbing 10% of your maximum health for 6 sec. (Can only occur once every 20 sec.)

Blasted Lands - Levels: 45-55
- Cloth - Nethergarde Greycloak [Implemented]
    Flavor: "Nethergarde's mages stopped dyeing their robes. The Blasted Lands take the color out regardless."
    (2) Set: You deal 15% additional damage to Demons.
    (4) Set: Killing a Demon restores 10% of your maximum mana and grants 10% spell damage for 15 sec.
- Leather - Outland Driftskin [Implemented]
    Flavor: "Nothing here has had skin worth taking in twenty years. This came from somewhere else."
    (2) Set: You take 15% less damage from Demons.
    (4) Set: Your critical strikes against Demons reduce their damage dealt by 20% for 6 sec.
- Mail - Nethergarde Gatewarden [Implemented]
    Flavor: "Nethergarde has watched that gate for twenty years. The mail has the patina to prove it."
    (2) Set: Your attacks have 10% increased critical strike chance against enemies above 90% health.
    (4) Set: While below 60% health, your attacks against Demons deal 30% additional damage.
- Plate - Tainted Scar Bulwark [Implemented]
    Flavor: "The Tainted Scar still glows at night. Plate does not help with that. It helps with the rest."
    (2) Set: Shadow damage taken is reduced by 20%.
    (4) Set: While three or more Demons are within 10 yards, you take 20% less damage and deal 10% more.

Searing Gorge - Levels: 45-55
- Cloth - Cinderforge Tinkerer [Implemented]
    Flavor: "Wool is a death sentence in the Gorge. Whatever this is, it is not wool."
    (2) Set: Engineering skill increased by 10.
    (4) Set: Every fifth item you craft with Engineering yields one additional item.
- Leather - Slag Pit Blastworker [Implemented]
    Flavor: "Cured in the Slag Pit, which is faster than a tannery and considerably less pleasant."
    (2) Set: Your Fire damage is increased by 15%.
    (4) Set: Your Fire critical strikes reduce the target's Fire resistance by 25% for 10 sec.
- Mail - Thorium Brotherhood Forgeguard [Implemented]
    Flavor: "The Thorium Brotherhood forges better than the Dark Irons and will tell you so, at length."
    (2) Set: Your armor is increased by 12% while in combat.
    (4) Set: Taking Fire damage grants 10% attack power for 10 sec, stacking up to 3 times.
- Plate - Dark Iron Furnace-ward [Implemented]
    Flavor: "Dark Iron plate holds heat like a kettle. That is a feature to them and a problem for you."
    (2) Set: Your equipment does not lose durability.
    (4) Set: Each different enemy you strike increases your armor by 3% for 10 sec, stacking up to 5 times.

Burning Steppes - Levels: 50-58
- Cloth - Morgan's Vigil Ashmage [Implemented]
    Flavor: "Ash works into the weave and never leaves. Every mage at Morgan's Vigil wears grey now, whatever color they started in."
    (2) Set: You take 50% less Fire damage, and taking Fire damage grants 10% spell power for 5 sec.
    (4) Set: Your spell critical strikes reduce the target's Fire resistance by 25% for 10 sec.
- Leather - Cinderscale Tanner [Implemented]
    Flavor: "Dragonkin shed scales all over the Steppes. The tanners work fast and stay upwind."
    (2) Set: You take 20% less damage from Dragonkin.
    (4) Set: Dodging or resisting an attack grants 25% movement speed and 10% increased damage for 5 sec.
- Mail - Morgan's Vigil Nightwatch [Implemented]
    Flavor: "Morgan's Vigil sits in sight of Blackrock Mountain. The men there sleep in their mail."
    (2) Set: Your attacks against Dragonkin deal 20% additional damage.
    (4) Set: Killing any enemy grants 10% increased damage against Dragonkin for 30 sec, stacking up to 3 times.
- Plate - Blackrock Ironhide [Implemented]
    Flavor: "Blackrock breeds things that treat plate as seasoning."
    (2) Set: You take 15% less damage from Elementals and Dragonkin.
    (4) Set: Taking Fire damage grants a shield absorbing 15% of the damage taken for 10 sec.

Western Plaguelands - Levels: 50-58
- Cloth - Andorhal Herbalist [Implemented]
    Flavor: "The blight took the fields, the herds, and the people. It left the linen, which nobody wants."
    (2) Set: Herbalism skill increased by 10, and nearby herbs appear on your minimap.
    (4) Set: Gathering an herb restores 5% of your maximum mana.
- Leather - Felstone Forager [Implemented]
    Flavor: "Whatever this came off of died twice. The tanner did not ask which death took."
    (2) Set: Gathering an herb grants 20% movement speed for 10 sec.
    (4) Set: Herbs yield one additional herb.
- Mail - Chillwind Quartermaster [Implemented]
    Flavor: "Chillwind Camp buries more than it recruits. The quartermaster keeps the armor in rotation."
    (2) Set: Gathering an herb restores 5% of your maximum health.
    (4) Set: Every fifth batch of potions you brew yields one additional potion.
- Plate - Uther's Tomb Vigil [Implemented]
    Flavor: "They say Uther's Tomb is still holy ground. Everyone out here needs something to still be true."
    (2) Set: Alchemy skill increased by 15.
    (4) Set: Healing you receive is increased by 15% while below 50% health.

Eastern Plaguelands - Levels: 53-60
- Cloth - Argent Dawn Anointer [Implemented]
    Flavor: "The Argent Dawn stitches its own. There is nobody left in the Plaguelands to hire."
    (2) Set: Your Holy and Arcane damage is increased by 15%.
    (4) Set: Healing yourself or an ally grants 10% increased spell damage for 8 sec.
- Leather - Naxxramas Watcher [Implemented]
    Flavor: "Scouts here memorize the ground, because the sky is no help. Naxxramas moves."
    (2) Set: Your critical strikes against Undead cause them to cower, reducing their damage by 25% for 4 sec.
    (4) Set: Killing an Undead grants 20% critical strike chance against Undead for 15 sec.
- Mail - Light's Hope Interceptor [Implemented]
    Flavor: "Light's Hope has held against everything sent at it. The armor in its cellar has not always been so lucky."
    (2) Set: Your attacks against enemies that are casting deal 25% additional damage.
    (4) Set: Striking an enemy that is casting grants 20% attack power for 10 sec. (Can only occur once every 10 sec.)
- Plate - Darrowshire Vigilant [Implemented]
    Flavor: "One chapel on a dead continent, and it has never fallen. Stand where they tell you to stand."
    (2) Set: You take 20% less damage from Undead.
    (4) Set: While below 50% health, you and allies within 10 yards take 10% less damage.

Deadwind Pass - Levels: 55-60
- Cloth - Karazhan Archivist [Implemented]
    Flavor: "Karazhan's library burned for a month. Some of the pages were cloth."
    (2) Set: Your Arcane damage is increased by 20%.
    (4) Set: While no allies are within 20 yards, your spell damage is increased by 20%.
- Leather - Solitary Tanner [Implemented]
    Flavor: "Nobody lives in Deadwind Pass. Someone still tanned this."
    (2) Set: While no allies are within 20 yards, you take 15% less damage.
    (4) Set: Killing an enemy while no allies are within 20 yards restores 15% of your maximum health.
- Mail - Deadwind Wayfarer [Implemented]
    Flavor: "The road through Deadwind is maintained by no one and travelled by fools. Wear the mail."
    (2) Set: You deal 15% increased damage and take 15% increased damage.
    (4) Set: Every 12 sec, your next attack cannot miss and deals 60% additional damage.
- Plate - Medivh's Watchman [Implemented]
    Flavor: "The tower watches the pass. Whether Medivh is still in it depends on who you ask."
    (2) Set: Your armor is increased by 15% while no allies are within 20 yards.
    (4) Set: Fatal damage instead leaves you at 20% health and immune to damage for 3 sec. (Can only occur once every 10 min.)

Isle of Quel'Danas - Levels: 70-70
- Cloth - Shattered Sun Invoker [Implemented]
    Flavor: "The Shattered Sun issues robes to anyone who can still cast. Nobody asks which side you were on last year."
    (2) Set: Your spell critical strikes grant 5% spell haste for 6 sec, stacking up to 4 times.
    (4) Set: Every 20 sec, your next spell is instant and deals 40% additional damage.
- Leather - Tempest Keep Veteran [Implemented]
    Flavor: "A blood elf and a draenei share the same trench here. Neither of them mentions Tempest Keep."
    (2) Set: Your critical strike chance is increased by 5% and your critical strikes deal 10% additional damage.
    (4) Set: Killing an enemy grants 10% haste and 10% movement speed for 10 sec, stacking up to 3 times.
- Mail - Sunwell Marcher [Implemented]
    Flavor: "The Sunwell burns again at the far end of the isle. Everyone here is armored for the walk toward it."
    (2) Set: Your melee and ranged attacks restore 2% of your maximum mana.
    (4) Set: Your attacks against Demons restore 3% of your maximum health.
- Plate - Magisters' Terrace Warden [Implemented]
    Flavor: "This whole isle is one door with a demon behind it. Dress accordingly."
    (2) Set: Your maximum health is increased by 8% and healing you receive is increased by 10%.
    (4) Set: Falling below 35% health heals you for 25% of your maximum health and damages enemies within 8 yards. (Can only occur once every 3 min.)


Kalimdor
--------------------
Azuremyst Isle - Levels: 1-10
- Cloth - Exodar Loomkeeper [Implemented]
    Flavor: "The Exodar's looms survived the crash. Very little else did."
    (2) Set: Your mana regenerates at 15% of its normal rate while casting.
    (4) Set: While at full mana, your spell damage is increased by 12%.
- Leather - Ammen Vale Trapper [Implemented]
    Flavor: "Ammen Vale's owlkin went mad when the crystals fell. Their feathers still make good trim."
    (2) Set: You gain 8% dodge chance while at or above 90% health.
    (4) Set: Dodging an attack restores 3% of your maximum health.
- Mail - Draenei Exile Guard [Implemented]
    Flavor: "The draenei have been refugees longer than most races have had names. They pack light and they mend well."
    (2) Set: While within 20 yards of an ally, your critical strike chance is increased by 6%.
    (4) Set: While three or more allies are within 20 yards, your damage is increased by 12%.
- Plate - Vindicator's Vigil [Implemented]
    Flavor: "The Vindicators wore this before the crash, and during it. They have not taken it off since."
    (2) Set: Healing you receive from others is increased by 15%.
    (4) Set: Allies within 15 yards gain 5% increased armor.

Durotar - Levels: 1-10
- Cloth - Sen'jin Bonecaster [Implemented]
    Flavor: "Sen'jin's witch doctors weave with beads and bone. The beads are the decorative part."
    (2) Set: Your damage over time effects deal 15% additional damage to enemies below 50% health.
    (4) Set: Every 12 sec, your next spell deals 20% additional damage.
- Leather - Durotar Boarstalker [Implemented]
    Flavor: "Boar hide, because Durotar has boars and very little else."
    (2) Set: Landing an attack grants 2% attack speed for 6 sec, stacking up to 5 times.
    (4) Set: Every 10 sec, your next attack deals 50% additional damage.
- Mail - Razor Hill Salvager [Implemented]
    Flavor: "Razor Hill's smiths work with whatever the sea washes up. Some of it was Alliance once."
    (2) Set: Your attacks restore 2% of your maximum resource.
    (4) Set: For each 10% of health you are missing, your damage is increased by 3%.
- Plate - Durotar Spoil-Taker [Implemented]
    Flavor: "The Horde had no plate when it landed here. It has plenty now, taken the usual way."
    (2) Set: You are immune to fear effects while above 75% health.
    (4) Set: Your attacks cannot be dodged or parried while you are below 50% health.

Mulgore - Levels: 1-10
- Cloth - Earthmother's Provider [Implemented]
    Flavor: "Tauren cloth is dyed with earth and smoke. The Earthmother is not fond of bright colors."
    (2) Set: Meat and hide you loot from Beasts is doubled.
    (4) Set: Every fifth item you craft with Cooking yields one additional item.
- Leather - Kodohide Tanner [Implemented]
    Flavor: "Nothing on the plains is wasted. The kodo gave its hide, its horn, and its name to the family that took it."
    (2) Set: Every fifth item you craft with Leatherworking yields one additional item.
    (4) Set: Your Leatherworking skill counts as 25 higher.
- Mail - Mulgore Hearth-Smith [Implemented]
    Flavor: "Tauren smiths came late to metal and took to it slowly. What they make, they make once."
    (2) Set: Cooking crafts produce one additional item.
    (4) Set: First Aid skill increased by 25.
- Plate - Thunder Bluff Hauler [Implemented]
    Flavor: "Thunder Bluff sits on four mesas and trusts the wind. Heavy things go up by hand."
    (2) Set: Your health and mana regeneration is increased by 50%.
    (4) Set: Your maximum health is increased by 5%.

Teldrassil - Levels: 1-10
- Cloth - Moonwell Robeweaver [Implemented]
    Flavor: "Moonwell water sets the dye. It also means the robe glows faintly for the first month."
    (2) Set: Your Nature damage is increased by 15%.
    (4) Set: While standing still, your spell power is increased by 15%.
- Leather - Teldrassil Boughrunner [Implemented]
    Flavor: "Sentinels prefer leather because Teldrassil is mostly branches. A fall is likelier than a fight."
    (2) Set: Attacking from stealth or from behind grants 15% attack speed for 8 sec.
    (4) Set: Leaving combat restores 5% of your maximum health.
- Mail - Kaldorei Wildguard [Implemented]
    Flavor: "Ten thousand years of immortality ended recently. The night elves are still learning what armor is for."
    (2) Set: Your armor is increased by 10% while outdoors.
    (4) Set: While outdoors, your health regeneration is doubled.
- Plate - Teldrassil Ironbark [Implemented]
    Flavor: "Night elf plate is rare and strange. They spent an age believing the forest was armor enough."
    (2) Set: You cannot be critically struck while above 90% health.
    (4) Set: Killing an enemy restores 5% of your maximum health to you and allies within 10 yards.

Bloodmyst Isle - Levels: 10-20
- Cloth - Bloodmyst Crystalweaver [Implemented]
    Flavor: "The crystals turned the whole isle red. Nobody weaves in that color on purpose."
    (2) Set: Your spells deal 12% additional damage but you take 10% more damage.
    (4) Set: Every 15 sec, your next spell costs no mana and deals 25% additional damage.
- Leather - Bloodmyst Thickhide Stalker [Implemented]
    Flavor: "Everything on Bloodmyst grew wrong after the crash. The hides are thicker than they ought to be."
    (2) Set: Your critical strikes reduce damage you take by 10% for 4 sec.
    (4) Set: Taking damage grants 4% critical strike chance for 8 sec, stacking up to 4 times.
- Mail - Bloodmyst Purge Warden [Implemented]
    Flavor: "The Exodar's fall poisoned this isle. The patrols go out anyway, armored against something they cannot name."
    (2) Set: You deal 12% additional damage to Beasts and take 12% less damage from them.
    (4) Set: Killing a Beast grants 15% attack power for 15 sec.
- Plate - Vindicator's Penance [Implemented]
    Flavor: "Vindicators walk Bloodmyst because somebody has to. The isle is their fault, after a fashion."
    (2) Set: Your maximum health is increased by 6% and healing you receive is reduced by 5%.
    (4) Set: Damage exceeding 20% of your maximum health in a single hit is reduced by 30%.

Darkshore - Levels: 10-20
- Cloth - Auberdine Lamplighter [Implemented]
    Flavor: "Auberdine's weavers work by lamplight. The sun has not properly reached Darkshore in an age."
    (2) Set: You breathe underwater and swim 25% faster.
    (4) Set: Enemies killed by your spells leave a chilling mist, slowing enemies within 6 yards by 30% for 6 sec.
- Leather - Darkshore Driftrunner [Implemented]
    Flavor: "The shore gives up strange hides. Some of them washed in from somewhere with no name."
    (2) Set: You are immune to movement-slowing effects.
    (4) Set: Killing an enemy grants 15% increased critical strike damage for 12 sec.
- Mail - Darkshore Wreck-Warden [Implemented]
    Flavor: "Every wreck on this coast had a crew. The sentinels salvage what the sea gives back."
    (2) Set: You take 12% less damage from Elementals and Beasts.
    (4) Set: Killing an enemy grants 6% increased armor for 20 sec, stacking up to 4 times.
- Plate - Darkshore Shieldwreck [Implemented]
    Flavor: "Night elf plate here is salvage from ten thousand years of things going wrong on one beach."
    (2) Set: Your block value is increased by 20%.
    (4) Set: Blocking an attack grants 10% increased armor for 8 sec, stacking up to 3 times.

The Barrens - Levels: 10-25
- Cloth - Crossroads Quartermaster [Implemented]
    Flavor: "The Crossroads is attacked so often the tailors have stopped taking deposits."
    (2) Set: Your mana regeneration is increased by 50%.
    (4) Set: Your maximum mana is increased by 8%.
- Leather - Zhevra Stripehunter [Implemented]
    Flavor: "Zhevra hide is striped, which the hunters call camouflage. Nothing else in the Barrens has stripes."
    (2) Set: Your mounted movement speed is increased by 10%.
    (4) Set: Killing an enemy grants 30% movement speed for 8 sec.
- Mail - Crossroads Stalwart [Implemented]
    Flavor: "The Crossroads guard has heard every joke about the Barrens. They are still standing there."
    (2) Set: You suffer no durability loss when you die.
    (4) Set: Your movement speed is increased by 8%.
- Plate - Barrens Waymarcher [Implemented]
    Flavor: "It is a very long walk across the Barrens. Consider that before you put this on."
    (2) Set: Your health regenerates 50% faster while out of combat.
    (4) Set: Each 30 sec spent in combat grants 5% damage reduction, up to 20%.

Stonetalon Mountains - Levels: 15-27
- Cloth - Windshear Ashweaver [Implemented]
    Flavor: "Windshear Crag burns day and night. The ash settles on everything and the weavers charge extra."
    (2) Set: Your spells deal 15% additional damage to enemies below you in elevation.
    (4) Set: Your spells deal 20% additional damage to slowed or rooted enemies.
- Leather - Stonetalon Cliffdiver [Implemented]
    Flavor: "Harpy feathers make poor trim and worse company. The hides come from further down the mountain."
    (2) Set: You take no falling damage.
    (4) Set: Your critical strikes deal 20% additional damage.
- Mail - Sun Rock Warder [Implemented]
    Flavor: "Sun Rock Retreat holds a mountain against goblins with saws. Mail helps more than you would think."
    (2) Set: Your attacks deal 15% additional damage to snared enemies.
    (4) Set: Your critical strikes reduce the target's movement speed by 30% for 4 sec.
- Plate - Charred Vale Bulwark [Implemented]
    Flavor: "The Charred Vale used to be a forest. Somebody in armor let that happen."
    (2) Set: You cannot be stunned while above 70% health.
    (4) Set: Breaking free of a stun grants 20% increased damage for 10 sec.

Ashenvale - Levels: 18-30
- Cloth - Astranaar Moonweaver [Implemented]
    Flavor: "Astranaar's priestesses weave by moonlight. The trees permit nothing brighter."
    (2) Set: Your spells deal 15% additional damage to enemies above your level.
    (4) Set: Killing an elite enemy restores 15% of your maximum mana.
- Leather - Ashenvale Hidetanner [Implemented]
    Flavor: "The Warsong take trees. The Sentinels take Warsong. Somebody tans what is left."
    (2) Set: You deal 10% additional damage while an ally is within 10 yards.
    (4) Set: Killing an enemy grants you and allies within 10 yards 10% attack speed for 8 sec.
- Mail - Ashenvale Frontline Salvager [Implemented]
    Flavor: "Ashenvale has been a front line for years. This is second-hand, and the last owner was probably orcish."
    (2) Set: You take 12% less damage from enemies above your level.
    (4) Set: Every 15 sec, your next attack deals 60% additional damage.
- Plate - Silverwing Ironguard [Implemented]
    Flavor: "Warsong axes bite deep. Silverwing plate is thick for exactly one reason."
    (2) Set: Your damage against elite enemies is increased by 10%.
    (4) Set: While in combat, you heal for 2% of your maximum health every 5 sec.

Thousand Needles - Levels: 25-35
- Cloth - Bleached Flats Sprinter [Implemented]
    Flavor: "The Shimmering Flats bleach everything white inside a season. Consider it a uniform."
    (2) Set: Your movement speed is increased by 8% and cannot be reduced below normal.
    (4) Set: While moving, your spell damage is increased by 15%.
- Leather - Highperch Wyvernhunter [Implemented]
    Flavor: "Wyvern hide from Highperch, assuming you can reach Highperch. Most cannot."
    (2) Set: You gain 5% dodge chance while moving.
    (4) Set: Every 10 sec, your next attack deals 45% additional damage.
- Mail - Shimmering Flats Racer [Implemented]
    Flavor: "The Shimmering Flats racers wear mail. Not for the racing. For the landing."
    (2) Set: Your mounted movement speed is increased by 10%.
    (4) Set: Killing an enemy grants 20% increased damage for 6 sec.
- Plate - Thousand Needles Cliffbreaker [Implemented]
    Flavor: "Thousand Needles is mesas and long drops. Plate makes the drop shorter and far more final."
    (2) Set: Your movement speed is increased by 10%.
    (4) Set: Entering combat grants 15% increased damage for 6 sec.

Desolace - Levels: 30-40
- Cloth - Ashfield Drifter [Implemented]
    Flavor: "Desolace earns the name. There is nothing here to dye cloth with but ash and centaur blood."
    (2) Set: Your spells deal 15% additional damage to enemies with no allies within 15 yards.
    (4) Set: Killing an enemy reduces the mana cost of your next spell by 30%.
- Leather - Kodo Bonecarver [Implemented]
    Flavor: "The Kodo Graveyard is exactly what it sounds like. Desolace has never wanted for material."
    (2) Set: Your attacks against Humanoids restore 2% of your maximum resource.
    (4) Set: Each Humanoid you kill reduces damage you take by 6% for 30 sec, stacking up to 4 times.
- Mail - Nijel's Point Garrison [Implemented]
    Flavor: "Five centaur clans, one dead land, and no reinforcements coming. Mail is what Nijel's Point can afford."
    (2) Set: Your chance to hit is increased by 5%.
    (4) Set: Enemies below 30% health take 20% additional damage from you.
- Plate - Maraudon Deepguard [Implemented]
    Flavor: "Maraudon goes down a long way. What comes back up in plate is not always who went down in it."
    (2) Set: Your armor is increased by 10% and your movement speed reduced by 5%.
    (4) Set: You suffer 20% less damage from enemies you have already struck.

Dustwallow Marsh - Levels: 35-45
- Cloth - Theramore Battlemage [Implemented]
    Flavor: "Theramore's mages keep two sets. The marsh ruins one a season."
    (2) Set: Your spell critical strikes reduce the target's damage dealt by 10% for 6 sec.
    (4) Set: Every 15 sec, your next spell strikes all enemies within 8 yards for 50% of the damage.
- Leather - Brackenwall Tanner [Implemented]
    Flavor: "The Brackenwall tanners work fast. In Dustwallow, so does the rot."
    (2) Set: Your critical strike chance against Dragonkin is increased by 10%.
    (4) Set: Critical strikes against Dragonkin reduce their attack speed by 20% for 6 sec.
- Mail - Alcaz Island Watcher [Implemented]
    Flavor: "Theramore's guard watches the water. Something under Alcaz Island watches back."
    (2) Set: Your maximum health is increased by 12% while within 20 yards of an ally.
    (4) Set: Taking damage while below 40% health grants 20% damage reduction for 5 sec. (Can only occur once every 45 sec.)
- Plate - Marshveil Warder [Implemented]
    Flavor: "There is a hole in this marsh nobody advertises. Some who went in wore plate. Some of the plate came out."
    (2) Set: Your block and parry chance is increased by 8%.
    (4) Set: Parrying an attack grants 20% attack power for 6 sec.

Feralas - Levels: 40-50
- Cloth - Shen'dralar Archivist [Implemented]
    Flavor: "Dire Maul's libraries are ogre-occupied now. Whatever the Highborne wove, the Gordunni use as bedding."
    (2) Set: Your spells deal 15% additional damage to Giants.
    (4) Set: Killing a Giant restores 12% of your maximum mana.
- Leather - Dream Bough Skinner [Implemented]
    Flavor: "Hippogryph feathers are protected. Yeti hide is not, and there is a great deal of yeti."
    (2) Set: Giants you damage are slowed by 25% for 5 sec.
    (4) Set: Dodging a Giant's attack grants 25% attack speed for 6 sec.
- Mail - Feathermoon Mariner [Implemented]
    Flavor: "Feathermoon Stronghold is on an island for a reason. The mail is not for the swim."
    (2) Set: Your attacks against Giants deal 12% additional damage.
    (4) Set: Killing a Giant grants 20% increased damage for 15 sec.
- Plate - Gordunni Breaker [Implemented]
    Flavor: "The Gordunni wear stolen plate badly. They make up the difference with enthusiasm."
    (2) Set: Your armor is increased by 5% for each Giant or elite within 15 yards, up to 20%.
    (4) Set: Breaking free of a stun grants 25% increased damage for 8 sec. (Can only occur once every 30 sec.)

Tanaris - Levels: 40-50
- Cloth - Gadgetzan Angler [Implemented]
    Flavor: "Gadgetzan sells robes by the yard and water by the mouthful. Guess which costs more."
    (2) Set: Fishing skill increased by 20.
    (4) Set: Fishing yields one additional fish per catch.
- Leather - Steamwheedle Rigger [Implemented]
    Flavor: "Silithid chitin does not tan. It is glued, and Gadgetzan does not guarantee the glue."
    (2) Set: Engineering crafts produce one additional item.
    (4) Set: Your Engineering skill counts as 25 higher.
- Mail - Gadgetzan Foundryhand [Implemented]
    Flavor: "Steel in Tanaris gets hot enough to brand. The Steamwheedle sell a liner for that, naturally."
    (2) Set: Your Fire damage is increased by 12%.
    (4) Set: Your movement speed is increased by 8%.
- Plate - Caverns of Time Sentinel [Implemented]
    Flavor: "The Caverns of Time have swallowed better-armored fools than you. Gadgetzan does not offer refunds."
    (2) Set: Your equipment does not lose durability.
    (4) Set: Your maximum health is increased by 6%.

Azshara - Levels: 45-55
- Cloth - Eldarath Silkweaver [Implemented]
    Flavor: "Eldarath's Highborne wove this pattern ten thousand years ago. The naga in the ruins still remember the fashion."
    (2) Set: Enchanting skill increased by 10.
    (4) Set: Disenchanting yields one additional material.
- Leather - Satyrhide Currier [Implemented]
    Flavor: "Azshara's satyrs were night elves once. Their hides tan like nothing else and the tanners do not discuss it."
    (2) Set: Your Enchanting skill counts as 25 higher.
    (4) Set: Disenchanting yields one additional material every fifth attempt.
- Mail - Azuregos Keeper [Implemented]
    Flavor: "Azuregos does not care what you are wearing. That is the only comfort Azshara offers."
    (2) Set: Your Arcane damage is increased by 12%.
    (4) Set: Your spell damage is increased by 8%.
- Plate - Bay of Storms Bulwark [Implemented]
    Flavor: "The naga come out of the Bay of Storms at night. Plate will not help you swim, but it helps on the sand."
    (2) Set: Arcane damage you take is reduced by 20%.
    (4) Set: Resisting a spell grants 10% spell resistance for 10 sec, stacking up to 3 times.

Felwood - Levels: 48-55
- Cloth - Cenarion Cleanser [Implemented]
    Flavor: "Felwood's air stains cloth green and it will not wash out. The Cenarion Circle stopped trying."
    (2) Set: Dispelling or curing an effect restores 4% of your maximum mana.
    (4) Set: Dispelling or curing an effect grants 10% spell power for 8 sec.
- Leather - Jadefire Corruptedhide [Implemented]
    Flavor: "Everything in Felwood is corrupted, including whatever this used to be. Wear it, but do not name it."
    (2) Set: Nature and Shadow damage you take is reduced by 20%.
    (4) Set: Killing an enemy grants 15% movement speed for 6 sec.
- Mail - Timbermaw Confidant [Implemented]
    Flavor: "Timbermaw Hold trades mail to those who earn it. Earning it outlasts most tempers."
    (2) Set: Your attacks reduce the target's damage dealt by 8% for 10 sec.
    (4) Set: Your critical strikes grant 12% attack power for 8 sec.
- Plate - Emerald Sanctuary Warden [Implemented]
    Flavor: "The Emerald Sanctuary is one clean grove in a poisoned forest. Someone in plate stands at every way in."
    (2) Set: You are immune to disease and poison effects.
    (4) Set: Your armor is increased by 3% for each 10% of health you are missing, up to 24%.

Un'Goro Crater - Levels: 48-55
- Cloth - Fire Plume Lapidary [Implemented]
    Flavor: "Un'Goro's crystals hum. So does anything you carry them in, after about a week."
    (2) Set: Jewelcrafting skill increased by 10.
    (4) Set: Every fifth item you craft with Jewelcrafting yields one additional item.
- Leather - Devilsaur Prospector [Implemented]
    Flavor: "Devilsaur hide is worth a fortune. Collecting it is why the fortune is necessary."
    (2) Set: Your Jewelcrafting skill counts as 25 higher.
    (4) Set: Jewelcrafting crafts produce one additional item.
- Mail - Marshal's Refuge Vanguard [Implemented]
    Flavor: "Marshal's Refuge is a hole in the rock with twelve people in it. Everything outside is bigger than you."
    (2) Set: Your damage is increased by 15% against targets with more current health than you.
    (4) Set: Killing an enemy with more health than you restores 10% of your maximum health.
- Plate - Un'Goro Fossilguard [Implemented]
    Flavor: "Nothing in Un'Goro has learned to fear armor. Most of it predates the concept."
    (2) Set: Your armor is increased by 12%.
    (4) Set: Your maximum health is increased by 8%.

Silithus - Levels: 55-60
- Cloth - Silithus Quartermaster [Implemented]
    Flavor: "Silithus sand gets into the weave, the eyes, and the food. The quartermaster has stopped apologizing."
    (2) Set: Your spells deal 18% additional damage to Beasts.
    (4) Set: Killing a Beast grants 50% increased casting speed for 8 sec.
- Leather - Silithid Chitinworker [Implemented]
    Flavor: "Silithid chitin, boiled and split. It creaks. Everyone here has learned to ignore the sound."
    (2) Set: You take 15% less damage from Beasts and are immune to poison effects.
    (4) Set: Your attacks against Beasts apply a venom dealing Nature damage over 8 sec.
- Mail - Cenarion Hold Nightwatch [Implemented]
    Flavor: "The Qiraji have been behind that wall for a thousand years. Cenarion Hold sleeps armored regardless."
    (2) Set: Your attacks strike all enemies within 3 yards of your target for 20% of the damage.
    (4) Set: For each enemy you have struck in the last 6 sec, gain 4% attack speed, up to 20%.
- Plate - Ahn'Qiraj Gatewarden [Implemented]
    Flavor: "Ahn'Qiraj is a gate with an army behind it. Every set of plate in Silithus points the same direction."
    (2) Set: You take 3% less damage for each enemy attacking you, up to 24%.
    (4) Set: Area effects deal 40% less damage to you.

Winterspring - Levels: 55-60
- Cloth - Everlook Outfitter [Implemented]
    Flavor: "Everlook sells thermal robes at four times the Ironforge price. Everlook is also the only shop for sixty miles."
    (2) Set: Enemies you damage with Frost spells take 12% additional Frost damage for 8 sec, stacking up to 3 times.
    (4) Set: Your spells deal 20% additional damage to slowed or rooted enemies.
- Leather - Frostsaber Poacher [Implemented]
    Flavor: "Frostsaber pelts are magnificent, forbidden by the Wintersaber trainers, and sold openly in Everlook."
    (2) Set: You leave no tracks and your movement speed is increased by 8%.
    (4) Set: Your first strike against each enemy grants 30% critical strike chance for 6 sec.
- Mail - Winterspring Bladebreaker [Implemented]
    Flavor: "The cold makes steel brittle. Winterspring has broken more blades than it has enemies."
    (2) Set: Each 10 sec spent in combat grants 5% damage reduction, up to 20%.
    (4) Set: Your critical strikes freeze the target, reducing its movement speed by 50% for 3 sec.
- Plate - Mazthoril Passguard [Implemented]
    Flavor: "Mazthoril's dragons watch the pass from inside the ice. They are not impressed by plate. Wear it anyway."
    (2) Set: Your armor is increased by 20% while stationary.
    (4) Set: While at or above 90% health, you reflect 15% of melee damage taken back at the attacker.


Outland
--------------------
Hellfire Peninsula - Levels: 58-63
- Cloth - Portal-Scarred Apothecary [Implemented]
    Flavor: "Everything on this side of the Portal is faintly poisoned. The robes are treated. Mostly."
    (2) Set: Your spells deal 10% additional damage to targets already suffering a damage over time effect.
    (4) Set: Your periodic damage has a 20% chance to strike a second time.
- Leather - Helboar Tanner [Implemented]
    Flavor: "Helboar hide is fel-tainted and the tanners know it. They charge less, not more."
    (2) Set: Healing received by enemies you damage is reduced by 50% for 8 sec.
    (4) Set: Your attacks deal additional damage equal to 10% of the target's missing health.
- Mail - Fel Reaver Sentry [Implemented]
    Flavor: "Listen for the footsteps. Mail will not save you from a Fel Reaver, but hearing it might."
    (2) Set: While in combat with two or more enemies, your attack speed is increased by 12%.
    (4) Set: Every 20 sec, your next attack strikes all enemies within 8 yards for 60% of the damage.
- Plate - Honor Hold Garrison [Implemented]
    Flavor: "Honor Hold has held the Portal for years with no reinforcements coming. The plate is patched where the last man was hit."
    (2) Set: Your armor is increased by 10% and you generate 20% additional threat.
    (4) Set: Blocking, parrying, or dodging grants 4% increased armor for 8 sec, stacking up to 4 times.

Zangarmarsh - Levels: 60-64
- Cloth - Glowcap Weaver [Implemented]
    Flavor: "Spore dust settles on everything here and glows faintly. Charming, until you try to hide."
    (2) Set: Your spells leave spores on the target, dealing Nature damage over 6 sec.
    (4) Set: Enemies you strike with a spell deal 10% less damage for 6 sec.
- Leather - Bog Lord Skinner [Implemented]
    Flavor: "Bog lord bark and sporeling caps. Zangarmarsh offers nothing so simple as an animal."
    (2) Set: Every 4 sec, your next attack deals an additional 25% of its damage as Nature damage.
    (4) Set: Nature damage you deal restores 1% of your maximum health.
- Mail - Cenarion Marshguard [Implemented]
    Flavor: "The naga are draining this marsh dry. Cenarion Refuge arms anyone willing to argue about it."
    (2) Set: You regenerate 3% of your maximum health every 5 sec while below 50% health in combat.
    (4) Set: Healing effects on you are 20% more effective while below 50% health.
- Plate - Deepbog Vanguard [Implemented]
    Flavor: "Mushrooms the size of towers, water to the knee, and eighty pounds of steel. Choose your footing."
    (2) Set: Nature damage you take is reduced by 25% and you cannot be poisoned.
    (4) Set: Enemies that strike you are infected with spores, dealing Nature damage over 8 sec.

Terokkar Forest - Levels: 62-65
- Cloth - Shattrath Emissary [Implemented]
    Flavor: "Shattrath dresses Aldor and Scryer alike. It is the only thing those two agree on."
    (2) Set: Casting a spell grants 4% spell power for 8 sec, stacking up to 5 times.
    (4) Set: Every 20 sec, your next spell deals 30% additional damage.
- Leather - Skettis Plumehunter [Implemented]
    Flavor: "The arakkoa of Skettis take feathers seriously. Wear them at your own discretion."
    (2) Set: Your first strike against each enemy deals 25% additional damage.
    (4) Set: Your first strike against each enemy reduces its damage dealt by 20% for 8 sec.
- Mail - Bone Wastes Sentinel [Implemented]
    Flavor: "The Bone Wastes are what Auchindoun's death did to the forest. Patrols go armored and go quickly."
    (2) Set: You gain 10% attack power while three or more enemies are within 30 yards.
    (4) Set: Killing an enemy grants 5% maximum health for 30 sec, stacking up to 4 times.
- Plate - Auchindoun Tombguard [Implemented]
    Flavor: "Auchindoun was a tomb for draenei heroes until something opened it. The plate inside was theirs first."
    (2) Set: Your block, parry, and dodge chances are each increased by 4%.
    (4) Set: Avoiding an attack grants 25% increased damage for 8 sec. (Can only occur once every 6 sec.)

Nagrand - Levels: 64-67
- Cloth - Trueshade Dyer [Implemented]
    Flavor: "Nagrand is the last piece of Draenor that still looks like itself. Even the dye takes better here."
    (2) Set: Casting a spell grants 20% spell power for 8 sec. (Can only occur once every 10 sec.)
    (4) Set: After a spell critical strike, your next spell also strikes a nearby enemy for 40% of the damage.
- Leather - Clefthoof Skinner [Implemented]
    Flavor: "Clefthoof hide is thick enough to stop an arrow and heavy enough to make you wish it had not."
    (2) Set: Every third attack against the same target grants 20% critical strike chance for 6 sec.
    (4) Set: Your critical strikes restore 2% of your maximum health.
- Mail - Garadar Outrider [Implemented]
    Flavor: "Every Mag'har in Garadar can ride, shoot, and mend mail. Draenor left no room for specialists."
    (2) Set: Your attacks against Elementals deal 15% additional damage.
    (4) Set: Killing an Elemental grants 15% attack power and 10% movement speed for 15 sec.
- Plate - Halaani Skirmisher [Implemented]
    Flavor: "Halaa changes hands twice a day. This plate has been on both sides of it."
    (2) Set: Your armor and attack power are increased by 8% while at or above 75% health.
    (4) Set: Falling below 50% health grants 30% increased armor for 10 sec. (Can only occur once every 60 sec.)

Blade's Edge Mountains - Levels: 65-68
- Cloth - Windspire Weaver [Implemented]
    Flavor: "The wind through the spires never stops. Cloth here is stitched down, not draped."
    (2) Set: Your spell critical strikes knock the target back 5 yards. (Can only occur once every 10 sec.)
    (4) Set: Your spell critical strikes reduce the target's spell resistance by 20% for 8 sec.
- Leather - Gruul's Tanner [Implemented]
    Flavor: "Gruul killed dragons and left them on the spires. The tanners of Blade's Edge keep very odd inventory."
    (2) Set: Your attacks against Giants and Dragonkin deal 15% additional damage.
    (4) Set: Critical strikes against Giants or Dragonkin reduce their movement speed by 40% for 5 sec.
- Mail - Gronnwatch Sentry [Implemented]
    Flavor: "The gronn are bigger than the ogres and the ogres are bigger than you. Mail is a formality. Wear it."
    (2) Set: Your critical strikes increase your critical damage by 10% for 8 sec, stacking up to 4 times.
    (4) Set: Landing a critical strike grants 10% attack speed for 5 sec, stacking up to 3 times.
- Plate - Bladespire Warguard [Implemented]
    Flavor: "Bladespire ogres collect armor. Not to wear. To display."
    (2) Set: Your parry chance is increased by 6%, and parrying reduces the attacker's damage by 15% for 5 sec.
    (4) Set: While above 75% health, melee attacks against you cannot critically strike.

Netherstorm - Levels: 67-70
- Cloth - Area 52 Outfitter [Implemented]
    Flavor: "The sky over Netherstorm is a wound. Area 52's tailors stopped looking up and started charging more."
    (2) Set: Tailoring skill increased by 10.
    (4) Set: Cloth you loot from Humanoids is doubled.
- Leather - Nether Drake Peddler [Implemented]
    Flavor: "Nether drake hide, if you believe the seller. In Area 52 that is a considerable if."
    (2) Set: Bolts of cloth you create yield one additional bolt.
    (4) Set: Your Tailoring skill counts as 25 higher.
- Mail - Manaforge Protector [Implemented]
    Flavor: "Manaforge Ultris runs day and night and nobody knows who started it. The Protectorate patrols in mail and hope."
    (2) Set: Your movement speed is increased by 8%, and movement-impairing effects on you are 30% less effective.
    (4) Set: Every 12 sec, your next attack deals 40% additional damage.
- Plate - Tempest Keep Warden [Implemented]
    Flavor: "Tempest Keep was a naaru vessel before Kael'thas took it. Whatever you wear inside, something older has seen better."
    (2) Set: Magical damage you take is reduced by 15%.
    (4) Set: Resisting or absorbing a spell restores 3% of your maximum health.

Shadowmoon Valley - Levels: 67-70
- Cloth - Felglow Weaver [Implemented]
    Flavor: "The rivers here run fel-green and give off light. Shadowmoon's weavers work by it, and their hands shake."
    (2) Set: Your periodic damage is increased by 16%.
    (4) Set: Your spell critical strikes inflict Shadow damage over 6 sec.
- Leather - Dragonmaw Wingguard [Implemented]
    Flavor: "Netherwing hide comes off that ledge and nowhere else. The Dragonmaw guard it jealously."
    (2) Set: Your attacks reduce the target's chance to hit you by 5% for 8 sec, stacking up to 4 times.
    (4) Set: Enemies that miss you take 25% increased damage from you for 6 sec.
- Mail - Black Temple Sentinel [Implemented]
    Flavor: "Everything in Shadowmoon Valley is aimed at the Black Temple. The mail is issued facing the same way."
    (2) Set: Your attacks against enemies affected by a damage over time effect deal 15% additional damage.
    (4) Set: Killing an enemy inflicts Shadow damage over 6 sec on enemies within 8 yards.
- Plate - Illidari Challenger [Implemented]
    Flavor: "Illidan has spent years telling everyone they are not prepared. The plate is an attempt to prove him wrong."
    (2) Set: Your armor is increased by 10%.
    (4) Set: Killing an enemy while below 60% health restores your health fully over 6 sec. (Can only occur once every 3 min.)


Northrend
--------------------
Borean Tundra - Levels: 68-72
- Cloth - Valiance Quartermaster [Implemented]
    Flavor: "Valiance Keep issues wool by weight and lectures you about frostbite. Both are warranted."
    (2) Set: Your spells have 15% reduced pushback and generate 10% less threat.
    (4) Set: While standing still, your spell haste is increased by 15%.
- Leather - Tuskarr Hidecarver [Implemented]
    Flavor: "Mammoth hide takes two people to carry before it is even cut. The tuskarr make it look effortless."
    (2) Set: You are immune to movement-slowing effects.
    (4) Set: Slowed enemies you strike are rooted for 2 sec. (Can only occur once every 15 sec.)
- Mail - Kvaldir Fogwatch [Implemented]
    Flavor: "The Kvaldir come out of the fog and go back into it. The patrols sleep in mail and light fires anyway."
    (2) Set: Your ranged attacks strike one additional nearby enemy for 30% of the damage. (Can only occur once every 6 sec.)
    (4) Set: Killing an enemy restores 10% of your maximum health.
- Plate - Warsong Tundraguard [Implemented]
    Flavor: "Warsong Hold was driven into the tundra like a nail. Everyone inside is armored and nobody is comfortable."
    (2) Set: You take 10% less damage from enemies you have not yet struck.
    (4) Set: The first enemy to strike you each combat deals 30% less damage for 10 sec.

Howling Fjord - Levels: 68-72
- Cloth - Fjord Underweave [Implemented]
    Flavor: "Vrykul do not wear robes and do not respect them. Wear it under something."
    (2) Set: Your spells deal 10% additional damage to targets above 75% health.
    (4) Set: Your first spell against each enemy deals 30% additional damage.
- Leather - Cliffrope Trapper [Implemented]
    Flavor: "The fjord's trappers work the cliffs with rope and optimism. What they bring back is worth the climb."
    (2) Set: You breathe underwater and swim 30% faster.
    (4) Set: Enemies you strike from behind are slowed by 50% for 3 sec. (Can only occur once every 12 sec.)
- Mail - Valgarde Ironcutter [Implemented]
    Flavor: "Vrykul mail is made for men eight feet tall. Valgarde's smiths cut it down and try not to dwell on it."
    (2) Set: Your melee damage is increased by 12%.
    (4) Set: Every 12 sec, your next attack deals 40% additional damage.
- Plate - Utgarde Ironguard [Implemented]
    Flavor: "Utgarde Keep has stood since before humans had a word for it. The vrykul inside have not gone anywhere."
    (2) Set: You take 12% less damage from Giants and cannot be disarmed.
    (4) Set: While below 50% health, your block value and parry chance are increased by 50%.

Dragonblight - Levels: 71-75
- Cloth - Wyrmshroud Tailor [Implemented]
    Flavor: "Dragons come to the Dragonblight to die. The cold keeps them and the wind takes everything lighter."
    (2) Set: Your spells deal 12% additional damage to Dragonkin and Undead.
    (4) Set: While within 10 yards of a corpse, your spell damage is increased by 10%.
- Leather - Wyrmhide Claimant [Implemented]
    Flavor: "There is no shortage of hide in the Dragonblight. There is a great deal of superstition about taking it."
    (2) Set: Your attacks against Dragonkin apply a wound reducing their armor by 10% for 12 sec.
    (4) Set: Your critical strikes against Dragonkin and Undead restore 3% of your maximum health.
- Mail - Wyrmrest Warder [Implemented]
    Flavor: "Wyrmrest Temple holds five flights in one room without bloodshed. Everyone still arrives armed."
    (2) Set: You deal 10% more damage and take 10% more damage while below 50% health.
    (4) Set: Killing an enemy while below 50% health restores 20% of your maximum health.
- Plate - Wrathgate Survivor [Implemented]
    Flavor: "Something happened at the Wrathgate that neither side will discuss. The plate came back. Most of the men did not."
    (2) Set: Damage you take from breath attacks and area effects is reduced by 25%.
    (4) Set: Surviving a hit dealing more than 25% of your maximum health grants 25% damage reduction for 8 sec.

Grizzly Hills - Levels: 73-75
- Cloth - Amberpine Woodsman [Implemented]
    Flavor: "Amberpine Lodge smells of pine pitch and wet dog. The second smell is worth asking about."
    (2) Set: Your spells against Beasts have 20% increased critical strike chance.
    (4) Set: Killing a Beast grants 12% spell haste for 12 sec.
- Leather - Grizzlefur Tanner [Implemented]
    Flavor: "The Grizzly Hills have bears in the name and worse in the woods. The bears are the part you can tan."
    (2) Set: Enemies affected by your damage over time effects take 15% additional damage from your attacks.
    (4) Set: Your attacks against enemies affected by your damage over time effects restore 2% of your maximum health.
- Mail - Conquest Hold Lumberguard [Implemented]
    Flavor: "Conquest Hold cuts timber and the furbolgs object. The objection is why Amberpine issues mail."
    (2) Set: Beasts you strike are staggered, reducing their attack speed by 20% for 6 sec.
    (4) Set: Beasts you damage become enraged, dealing 20% more damage but taking 30% more from you.
- Plate - Grizzlemaw Deepguard [Implemented]
    Flavor: "Grizzlemaw was a furbolg city before it rotted. Something still lives in the roots."
    (2) Set: Your armor is increased by 3% for each 10% of health you are missing, up to 24%.
    (4) Set: While below 40% health, Beasts and Humanoids attacking you deal 25% less damage.

Zul'Drak - Levels: 74-77
- Cloth - Drakkari Godslayer [Implemented]
    Flavor: "The Drakkari are killing their own gods for the power. Nobody in Zul'Drak is dressed for anything good."
    (2) Set: Your spells deal 20% additional damage to enemies affected by a stun, root, or fear.
    (4) Set: Your spell critical strikes stun the target for 2 sec. (Can only occur once every 20 sec.)
- Leather - Drakkari Fleshcarver [Implemented]
    Flavor: "The Drakkari skin what they kill, and they have been killing gods. Take that as a note on the local leatherwork."
    (2) Set: Your attacks against stunned or incapacitated enemies deal 30% additional damage.
    (4) Set: Your critical strikes reduce the target's dodge and parry chance by 20% for 8 sec.
- Mail - Argent Ascendant [Implemented]
    Flavor: "Zul'Drak is a staircase of dead gods. The Argent Crusade climbs it in mail and prays quietly."
    (2) Set: Your attacks reduce the target's attack power by 2% for 10 sec, stacking up to 3 times.
    (4) Set: Killing an enemy grants 20% increased damage for 10 sec.
- Plate - Amphitheater Gladiator [Implemented]
    Flavor: "The Amphitheater of Anguish takes all comers and returns very few. Plate improves the odds from dreadful to poor."
    (2) Set: You are immune to stun effects while above 80% health.
    (4) Set: Breaking free of a stun or root grants 30% damage reduction for 6 sec.

Sholazar Basin - Levels: 76-78
- Cloth - Sholazar Distiller [Implemented]
    Flavor: "Sholazar is a jungle in the middle of Northrend and nobody can explain it. Pack for both."
    (2) Set: Alchemy skill increased by 10.
    (4) Set: Every fifth item you craft with Alchemy yields one additional item.
- Leather - Nesingwary Trophy-Hunter [Implemented]
    Flavor: "Hemet Nesingwary has moved his camp to Northrend. The animals here have not been warned."
    (2) Set: Flasks and elixirs you create yield one additional.
    (4) Set: Your Alchemy skill counts as 25 higher.
- Mail - Basin Truceseeker [Implemented]
    Flavor: "The Oracles and the Frenzyheart have been at war longer than anyone remembers why. Wear nobody's colors."
    (2) Set: Potions you create yield two additional potions.
    (4) Set: Killing an enemy restores 5% of your maximum health and mana.
- Plate - Titanspring Guardian [Implemented]
    Flavor: "Titan machinery keeps this basin warm and the wildlife has grown accordingly. Wear the plate."
    (2) Set: Your armor is increased by 10% while in combat.
    (4) Set: Falling below 35% health shields you for 15% of your maximum health. (Can only occur once every 60 sec.)

Crystalsong Forest - Levels: 77-80
- Cloth - Crystalsong Scrivener [Implemented]
    Flavor: "The trees in Crystalsong ring when the wind moves. Dalaran's mages find it soothing. Nobody else does."
    (2) Set: Inscription skill increased by 10.
    (4) Set: Milling yields one additional pigment.
- Leather - Underbrush Forager [Implemented]
    Flavor: "Crystalsong's animals cut themselves on the underbrush. So will you, and so will the leather."
    (2) Set: Your Inscription skill counts as 25 higher.
    (4) Set: Glyphs you inscribe yield two instead of one.
- Mail - Dalaran's Orphan [Implemented]
    Flavor: "Dalaran floats overhead and drops nothing useful. Crystalsong outfits itself."
    (2) Set: Your spell damage is increased by 8%.
    (4) Set: Your spell haste is increased by 5%.
- Plate - Twinspire Warden [Implemented]
    Flavor: "Windrunner's Overlook and Sunreaver's Command face each other across a glass forest. Both sides stay armored."
    (2) Set: Your maximum health is increased by 6%.
    (4) Set: Entering combat grants a shield absorbing 8% of your maximum health for 10 sec. (Can only occur once every 20 sec.)

Icecrown - Levels: 77-80
- Cloth - Icecrown Provisioner [Implemented]
    Flavor: "Every scrap of cloth in Icecrown was carried in. Nothing here grows, weaves, or forgives."
    (2) Set: Your spells deal 15% additional damage to Undead.
    (4) Set: Killing an Undead grants 10% spell power for 15 sec, stacking up to 3 times.
- Leather - Icebound Flayer [Implemented]
    Flavor: "There is nothing alive in Icecrown to skin. This came off the back of something that only appeared to be."
    (2) Set: Every 10 sec, your next attack deals 50% additional damage.
    (4) Set: Your critical strikes against Undead reduce their damage dealt by 25% for 8 sec.
- Mail - Saronite Deafsmith [Implemented]
    Flavor: "Saronite whispers to the men who mine it. The smiths who work it wear earplugs and will not say why."
    (2) Set: Killing an Undead grants Resolve, increasing your damage by 3%, stacking up to 10 times. Dying clears it.
    (4) Set: Your attacks against Undead restore 2% of your maximum health.
- Plate - Citadel Bulwark [Implemented]
    Flavor: "The Citadel is visible from everywhere in Icecrown. That is deliberate, and so is the weight of this plate."
    (2) Set: You take 20% less damage from Undead and cannot be feared by them.
    (4) Set: While below 50% health, you gain 25% damage reduction and 25% increased damage.

The Storm Peaks - Levels: 77-80
- Cloth - K3 Seamster [Implemented]
    Flavor: "The Sons of Hodir are forty feet tall and their tailoring reflects it. Someone in K3 does alterations."
    (2) Set: Blacksmithing skill increased by 15.
    (4) Set: Smelting titanium yields one additional bar.
- Leather - Hyldnir Hidetrader [Implemented]
    Flavor: "The Hyldnir hunt mammoth and worse across the Snowdrift Plains. They do not sell hide. They trade it, and the price is strange."
    (2) Set: Every fifth item you craft with Blacksmithing yields one additional item.
    (4) Set: Your Blacksmithing skill counts as 25 higher.
- Mail - Forgeborn Ironkin [Implemented]
    Flavor: "The iron dwarves were made, not born. Their mail is better than yours and they never had to learn how."
    (2) Set: Your armor is increased by 12%.
    (4) Set: Your attack power is increased by 10%.
- Plate - Ulduar Gateguard [Implemented]
    Flavor: "Ulduar's doors are the size of a city gate and were built to keep something in. Wear everything you own."
    (2) Set: Your armor value is increased by 15%.
    (4) Set: While at or above 80% health, incoming damage is reduced by 30%.


Dungeons
--------------------
Ragefire Chasm - Levels: 15-21
- Cloth - Searing Blade Adept [Implemented]
    Flavor: "The Searing Blade meets beneath Orgrimmar itself. Their robes were not chosen for the heat."
    (2) Set: Casting a spell grants 6% spell power for 6 sec, stacking up to 3 times.
    (4) Set: Your spells cleave to one enemy within 5 yards of the target for 30% of the damage.
- Leather - Cinderledge Skirmisher [Implemented]
    Flavor: "The chasm is narrow ledges over lava. Light footing beats heavy anything."
    (2) Set: You take 25% less Fire damage.
    (4) Set: Your critical strikes ignite the target, dealing Fire damage over 4 sec.
- Mail - Undercroft Scout [Implemented]
    Flavor: "Thrall does not know what gathers under his city. Someone armored should go and find out."
    (2) Set: Your first strike against each enemy grants 10% attack speed for 6 sec.
    (4) Set: Every 15 sec, your next attack deals 45% additional damage.
- Plate - Ragefire Warden [Implemented]
    Flavor: "Ragefire is hot enough to cook a man inside his own armor. The cultists are counting on it."
    (2) Set: Fire damage you take is reduced by 40%.
    (4) Set: Killing an enemy grants 5% increased armor for 15 sec, stacking up to 3 times.

Deadmines - Levels: 15-25
- Cloth - Cave Shipwright [Implemented]
    Flavor: "VanCleef's men built a warship inside a cave. Nobody has ever explained the sails."
    (2) Set: Your spells deal 12% additional damage to Humanoids.
    (4) Set: Every 6 sec, your spells slow the target by 50% for 4 sec.
- Leather - Defias Stonemason [Implemented]
    Flavor: "The Defias were stonemasons before Stormwind refused to pay them. They kept the leather aprons."
    (2) Set: Your attacks against Humanoids deal 15% additional damage.
    (4) Set: Killing a Humanoid grants 12% critical strike chance for 8 sec.
- Mail - Ironclad Machinist [Implemented]
    Flavor: "The Deadmines run under Westfall for miles. Whatever is being built down there is loud."
    (2) Set: Mechanical enemies take 20% additional damage from your attacks.
    (4) Set: Destroying a Mechanical enemy grants 10% haste for 12 sec.
- Plate - VanCleef's Juggernaut [Implemented]
    Flavor: "Edwin VanCleef asked for wages. What he built instead was a juggernaut, in a mine."
    (2) Set: You take 15% less damage from Mechanical enemies.
    (4) Set: Enemies that strike you are slowed by 30% for 4 sec.

Wailing Caverns - Levels: 15-25
- Cloth - Fang Dreamweaver [Implemented]
    Flavor: "The Druids of the Fang dream while awake. Their robes are damp with something that is not water."
    (2) Set: Your Nature damage is increased by 15%.
    (4) Set: Your spells deal 20% additional damage to enemies affected by your crowd control.
- Leather - Deviate Tanner [Implemented]
    Flavor: "Deviate hide changes color when you are not looking at it. The tanners guarantee nothing."
    (2) Set: Your attacks apply a venom dealing Nature damage over 6 sec.
    (4) Set: Enemies affected by your damage over time effects take 15% additional damage.
- Mail - Naralex Vigilant [Implemented]
    Flavor: "Naralex is still asleep down there and the nightmare is leaking out. Bring something solid."
    (2) Set: Your attacks reduce the target's vision, lowering its chance to hit you by 8% for 10 sec.
    (4) Set: Enemies that miss you are slowed by 50% for 3 sec. (Can only occur once every 20 sec.)
- Plate - Wailing Vanguard [Implemented]
    Flavor: "The Wailing Caverns have no straight corridors and no landmarks. Heavy armor only makes the wrong turn slower."
    (2) Set: You are immune to sleep effects and take 20% less damage from Beasts.
    (4) Set: Breaking free of any control effect heals you for 12% of your maximum health.

Shadowfang Keep - Levels: 16-26
- Cloth - Arugal's Attendant [Implemented]
    Flavor: "Arugal summoned the worgen and then lost his mind. His household still sets the table."
    (2) Set: Your Shadow spells reduce the target's armor by 12% for 10 sec.
    (4) Set: Killing an enemy with a spell grants 15% spell power for 10 sec.
- Leather - Worgen Skinner [Implemented]
    Flavor: "The worgen of Shadowfang were men once. Not everything tanned in that keep came off an animal."
    (2) Set: Your attacks against enemies that are alone deal 25% additional damage.
    (4) Set: Killing an enemy renders you untrackable for 6 sec.
- Mail - Silverlaine Watchman [Implemented]
    Flavor: "Baron Silverlaine's guard still walk their rounds. They have not noticed they are dead."
    (2) Set: Your attacks against Undead and Beasts have 12% increased critical strike chance.
    (4) Set: Your critical strikes cause the target to cower, reducing its damage by 20% for 5 sec.
- Plate - Household Guardian [Implemented]
    Flavor: "Shadowfang Keep is a house with the family still in it. That is the problem."
    (2) Set: You cannot be feared.
    (4) Set: Fleeing enemies take 30% additional damage from you.

Blackfathom Deeps - Levels: 19-29
- Cloth - Fathom Acolyte [Implemented]
    Flavor: "Half of Blackfathom is underwater. Robes are a poor choice and the only one most casters own."
    (2) Set: Your spells have 15% reduced pushback.
    (4) Set: Your Frost damage is increased by 18%.
- Leather - Naga-Skin Corsair [Implemented]
    Flavor: "The naga took this temple when it sank. Everything down there has adapted except the corpses."
    (2) Set: You swim 35% faster and breathe underwater indefinitely.
    (4) Set: Your critical strikes deal 20% additional damage.
- Mail - Aku'mai Cultist [Implemented]
    Flavor: "Aku'mai has been fed by cultists for centuries. Rust is the least of your worries in Blackfathom."
    (2) Set: Your attacks reduce the target's casting speed by 25% for 6 sec.
    (4) Set: Your critical strikes restore 8% of your maximum resource.
- Plate - Drowned Temple Guard [Implemented]
    Flavor: "The temple went down with everyone inside it. Their armor is still there, and still occupied."
    (2) Set: Shadow and Frost damage you take is reduced by 15%.
    (4) Set: Falling below 50% health grants 25% damage reduction for 6 sec. (Can only occur once every 45 sec.)

Stormwind Stockade - Levels: 20-30
- Cloth - Stockade Laundress [Implemented]
    Flavor: "The Stockade riot started in the laundry. Nobody has adequately explained how."
    (2) Set: Your spells deal 15% additional damage while three or more enemies are within 10 yards.
    (4) Set: Your area spells strike one additional target.
- Leather - Stockade Escapee [Implemented]
    Flavor: "Half the Stockade is Defias and the other half wishes it were. Wear something you can run in."
    (2) Set: You take 20% less damage while two or more enemies are attacking you.
    (4) Set: Escaping a stun, root, or snare grants 25% movement speed for 6 sec.
- Mail - Stockade Turnkey [Implemented]
    Flavor: "The guards lost the Stockade in a single afternoon. Their mail is still down there, on the wrong men."
    (2) Set: Your attacks strike a second enemy within 5 yards for 25% of the damage.
    (4) Set: Killing an enemy grants 20% attack power for 12 sec.
- Plate - Four-Corner Bulwark [Implemented]
    Flavor: "The Stockade is one room with four corners and no way around. Plate is the correct answer."
    (2) Set: Enemies within 8 yards deal 8% less damage to you.
    (4) Set: You take 5% less damage for each enemy in melee range beyond the first, up to 25%.

Razorfen Kraul - Levels: 22-32
- Cloth - Thornsnag Adept [Implemented]
    Flavor: "The Kraul is built from the thorns of a dead god. Cloth snags. Cloth always snags."
    (2) Set: Your spells deal 15% additional damage to enemies afflicted by a bleed.
    (4) Set: Your spell critical strikes cause the target to bleed for 20% of the damage over 6 sec.
- Leather - Barbhide Skinner [Implemented]
    Flavor: "Quilboar hide is barbed from the inside. Wearing it is a statement about your tolerance for discomfort."
    (2) Set: You take 25% less damage from area effects.
    (4) Set: Enemies that strike you are slowed by 30% for 4 sec.
- Mail - Razorflank Enforcer [Implemented]
    Flavor: "Charlga Razorflank has held the Kraul longer than the Barrens has had a road."
    (2) Set: Your attacks against enemies attacking someone else deal 20% additional damage.
    (4) Set: Killing an enemy reduces damage you take by 20% for 15 sec.
- Plate - Agamaggan Thornguard [Implemented]
    Flavor: "Agamaggan died here and the thorns grew out of him. Something that large leaves a great many spines."
    (2) Set: Melee attackers suffer damage equal to 3% of your armor.
    (4) Set: While three or more enemies are in melee range, your parry chance is increased by 15%.

Gnomeregan - Levels: 23-33
- Cloth - Gnomeregan Tinker [Implemented]
    Flavor: "Gnomeregan's radiation ruined the gnomes and everything they owned. The cloth is fine, technically."
    (2) Set: Engineering skill increased by 15.
    (4) Set: Every third item you craft with Engineering yields one additional item.
- Leather - Leper Engineer [Implemented]
    Flavor: "The leper gnomes were engineers last week. Try to hold onto that on the way down."
    (2) Set: Items you craft with Engineering yield one additional item.
    (4) Set: Killing a Mechanical enemy grants 20% movement speed for 10 sec.
- Mail - Thermaplugg Survivor [Implemented]
    Flavor: "Thermaplugg flooded his own city with radiation to keep the troggs out. It worked, in a sense."
    (2) Set: Nature damage you take is reduced by 50%.
    (4) Set: Your attacks stun Mechanical enemies for 2 sec. (Can only occur once every 20 sec.)
- Plate - Ironworks Sentinel [Implemented]
    Flavor: "Gnomeregan is a machine the size of a city and most of it is still running. None of it needs you."
    (2) Set: You cannot be disarmed.
    (4) Set: Mechanical enemies that strike you are short-circuited, losing 25% attack speed for 8 sec.

Scarlet Monastery - Graveyard - Levels: 27-37
- Cloth - Thalnos Gravetender [Implemented]
    Flavor: "The Scarlet Crusade buries its own out back. Thalnos has them up again by morning."
    (2) Set: Your spells deal 15% additional damage to enemies raised or summoned by another.
    (4) Set: Summoned and raised enemies you kill grant 8% spell power for 12 sec.
- Leather - Vishas Gravedigger [Implemented]
    Flavor: "Interrogator Vishas keeps his tools in the graveyard shed. He is not a gardener."
    (2) Set: Your attacks against enemies below 25% health deal 20% additional damage.
    (4) Set: Killing an enemy grants 20% attack speed for 6 sec.
- Mail - Postern Warden [Implemented]
    Flavor: "The graveyard is the Monastery's back door. The Crusade watches it closer than the front."
    (2) Set: Your attacks reduce the target's maximum health by 3% for 20 sec, stacking up to 3 times.
    (4) Set: Enemies you kill leave a lingering ward, reducing damage you take by 15% for 15 sec.
- Plate - Undying Crusader [Implemented]
    Flavor: "Everything the Crusade buries here comes back. They have stopped acting surprised."
    (2) Set: You take 15% less damage from Undead.
    (4) Set: Standing your ground grants 20% increased armor.

Scarlet Monastery - Library - Levels: 30-40
- Cloth - Doan Archivist [Implemented]
    Flavor: "Arcanist Doan guards a library the Crusade does not permit its own to read."
    (2) Set: Each enemy spell you resist grants 8% spell power for 15 sec, stacking up to 3 times.
    (4) Set: Your spells deal 20% additional damage to enemies that are casting.
- Leather - Loksey's Houndsman [Implemented]
    Flavor: "Houndmaster Loksey trains his dogs on Scarlet leather. Consider what you are wearing."
    (2) Set: Your attacks silence casting enemies for 1 sec. (Can only occur once every 12 sec.)
    (4) Set: Silenced enemies take 25% additional damage from you.
- Mail - Silent Beastbane [Implemented]
    Flavor: "The Library is the quietest room in the Monastery. That is not a comfort."
    (2) Set: Your attacks against Beasts deal 25% additional damage.
    (4) Set: Killing a Beast grants 20% attack power for 12 sec.
- Plate - Archive Warden [Implemented]
    Flavor: "Doan will bring the shelves down on you before he lets you read a single page."
    (2) Set: Magical damage you take is reduced by 12%.
    (4) Set: Taking magical damage grants a shield absorbing 20% of the damage taken for 10 sec. (Can only occur once every 20 sec.)

Razorfen Downs - Levels: 32-42
- Cloth - Amnennar's Frostbinder [Implemented]
    Flavor: "Amnennar came south to raise the quilboar and found them agreeable. The Downs are cold now."
    (2) Set: Your Frost spells against Undead reduce their movement speed by 50% for 6 sec.
    (4) Set: Your spells deal 20% additional damage to slowed enemies.
- Leather - Deathless Quilboar [Implemented]
    Flavor: "The quilboar of the Downs died and kept walking. Their hide did not improve in the process."
    (2) Set: You are immune to chill effects and take 20% less Frost damage.
    (4) Set: Enemies that die near you shatter, dealing damage to other enemies within 6 yards equal to 12% of the slain enemy's maximum health.
- Mail - Frostfall Tracker [Implemented]
    Flavor: "A lich holds the top of the Downs and the frost runs downhill. Bring more than courage."
    (2) Set: Your attacks chill the target, reducing its casting speed by 15% for 6 sec.
    (4) Set: Killing an enemy grants 15% haste for 10 sec.
- Plate - Barrow Sentinel [Implemented]
    Flavor: "Razorfen Downs was a burial mound. Amnennar regards that as an opportunity."
    (2) Set: You are immune to movement-slowing effects.
    (4) Set: Enemies that strike you are chilled, losing 20% attack speed for 5 sec.

Scarlet Monastery - Armory - Levels: 32-42
- Cloth - Herod's Apprentice [Implemented]
    Flavor: "Herod trains alone in the Armory. Anyone in a robe should let somebody else open that door."
    (2) Set: Your spells deal 20% additional damage to a target with no other enemies within 10 yards.
    (4) Set: Fighting a single enemy grants 12% casting speed.
- Leather - Whirling Evader [Implemented]
    Flavor: "The Armory is one room, one man, and a great deal of spinning. Stay out of the middle."
    (2) Set: You take 30% less damage from area attacks.
    (4) Set: While moving, you gain 15% dodge chance.
- Mail - Armory Challenger [Implemented]
    Flavor: "Herod calls himself the Scarlet Champion. The Armory is where he proves it, repeatedly."
    (2) Set: Your weapon damage is increased by 12% against a single opponent.
    (4) Set: Every fifth consecutive attack against the same enemy grants 20% critical strike chance for 10 sec.
- Plate - Scarlet Armsman [Implemented]
    Flavor: "Everything hanging in the Armory fits a Scarlet Crusader. Some of it is still warm."
    (2) Set: You cannot be disarmed, and your parry chance is increased by 5%.
    (4) Set: Parrying or blocking grants your next attack 30% additional damage.

Scarlet Monastery - Cathedral - Levels: 35-45
- Cloth - Whitemane's Zealot [Implemented]
    Flavor: "Whitemane raises Mograine as fast as you can put him down. Faith is a renewable resource."
    (2) Set: Your Holy damage is increased by 18% and Holy damage you take is reduced by 15%.
    (4) Set: Your spells deal 20% additional damage to enemies above 90% health.
- Leather - Congregation Silencer [Implemented]
    Flavor: "The Cathedral is the last room in the Monastery and the only one with a congregation."
    (2) Set: Your attacks reduce healing received by the target by 50% for 6 sec.
    (4) Set: Killing an enemy grants 25% attack power for 10 sec.
- Mail - Mograine's Faithful [Implemented]
    Flavor: "Mograine leads the faithful. Whitemane makes certain he keeps leading."
    (2) Set: Your attacks reduce healing received by the target by 20% for 10 sec, stacking up to 3 times.
    (4) Set: Your attacks deal 30% additional damage to enemies above 90% health.
- Plate - Cathedral Vindicator [Implemented]
    Flavor: "The Crusade can no longer tell friend from Scourge. Your armor will not clarify matters."
    (2) Set: You take 15% less damage while two or more enemies are engaged.
    (4) Set: Killing an enemy reduces magical damage you take by 30% for 10 sec.

Uldaman - Levels: 35-45
- Cloth - Explorers' League Archivist [Implemented]
    Flavor: "Uldaman holds the discs explaining where dwarves came from. The Explorers' League is beside itself."
    (2) Set: Your spells deal 20% additional damage to Elementals and Mechanical enemies.
    (4) Set: Your spells reduce an Elemental or Mechanical enemy's armor by 20% for 12 sec.
- Leather - Trogg Excavator [Implemented]
    Flavor: "Troggs were the Titans' first attempt at dwarves. Uldaman is where they were left."
    (2) Set: Elementals and Mechanical enemies attacking you deal 25% less damage.
    (4) Set: Your attacks against slowed or rooted enemies deal 25% additional damage.
- Mail - Archaedas' Vaultbreaker [Implemented]
    Flavor: "Archaedas has guarded this vault since before there was anyone to guard it from."
    (2) Set: Your attacks shatter stone, reducing the target's armor by 15% for 12 sec.
    (4) Set: Your attacks against Elementals and Mechanical enemies deal 12% additional damage.
- Plate - Stoneborn Vanguard [Implemented]
    Flavor: "Everything in Uldaman is stone and most of it stands up eventually. Hit it first."
    (2) Set: You cannot be stunned while above 50% health.
    (4) Set: Each Elemental or Mechanical enemy you kill grants 8% armor for 30 sec, stacking up to 3 times.

Maraudon - Purple Crystals - Levels: 39-49
- Cloth - Crystalhum Adept [Implemented]
    Flavor: "The purple crystals hum at a pitch that unsettles casters. Nobody knows why. Nobody stays to learn."
    (2) Set: Your spells deal 30% additional damage to enemies already afflicted by one of your effects.
    (4) Set: Your spells shatter, striking one additional enemy within 6 yards for 25% of the damage.
- Leather - Grandkin Skulker [Implemented]
    Flavor: "The centaur of Maraudon are Theradras's grandchildren. They take the family resemblance badly."
    (2) Set: You move 15% faster while out of combat.
    (4) Set: Attacks made before an enemy has acted deal 35% additional damage.
- Mail - Clanfetter Warden [Implemented]
    Flavor: "Every centaur clan in Desolace traces back into this cave, and they return to argue about it."
    (2) Set: Your attacks against Humanoids reduce their movement speed by 25% for 5 sec.
    (4) Set: Slowed enemies take 20% additional damage from you.
- Plate - Crystalguard Sentinel [Implemented]
    Flavor: "The purple wing is all crystal and echo. Plate announces you three rooms early."
    (2) Set: Arcane damage you take is reduced by 40%.
    (4) Set: Taking damage grants a shield absorbing 100% of the damage taken for 10 sec. (Can only occur once every 20 sec.)

Maraudon - Orange Crystals - Levels: 41-51
- Cloth - Sporeborn Channeler [Implemented]
    Flavor: "Noxxion splits when struck and every piece is still poisonous. Robes offer nothing here."
    (2) Set: Your Nature spells cost 15% less mana and deal 12% additional damage.
    (4) Set: Enemies you kill release spores, slowing enemies within 6 yards by 40% for 5 sec.
- Leather - Razorlash Stalker [Implemented]
    Flavor: "The orange wing grows things. Razorlash was a plant before it decided otherwise."
    (2) Set: Nature and poison damage you take is reduced by 40%.
    (4) Set: Enemies afflicted by a damage over time effect take 20% additional damage from you.
- Mail - Splitroot Culler [Implemented]
    Flavor: "The orange passages run with poison. Mail rusts. You do considerably worse."
    (2) Set: Your attacks against enemies that split or summon deal 20% additional damage.
    (4) Set: Killing a summoned enemy grants 6% attack power for 20 sec, stacking up to 5 times.
- Plate - Thornbreaker Vanguard [Implemented]
    Flavor: "Razorlash uproots itself to reach you. Standing still is not the strategy."
    (2) Set: You are immune to root effects and take 20% less Nature damage.
    (4) Set: Enemies rooted or immobilised take 20% additional damage from you.

Zul'Farrak - Levels: 41-51
- Cloth - Sandsworn Ritualist [Implemented]
    Flavor: "The pyramid steps hold an entire troll army and they all come at once. That is the event."
    (2) Set: Your spells deal 2% additional damage for each enemy within 15 yards, up to 30%.
    (4) Set: Casting while five or more enemies are nearby restores 3% of your maximum mana.
- Leather - Blygang Renegade [Implemented]
    Flavor: "Sergeant Bly and his gang will help for a price. The price is everything you find."
    (2) Set: Beasts and Humanoids attacking you deal 25% less damage.
    (4) Set: While outnumbered three to one or worse, you take 25% less damage.
- Mail - Gahz'rilla Angler [Implemented]
    Flavor: "The Sandfury call Gahz'rilla out of the water with a mallet. Nobody has asked them to stop."
    (2) Set: Each enemy within 10 yards increases your attack speed by 3%, up to 24%.
    (4) Set: Each enemy killed within 10 sec of the last grants 10% attack speed, stacking up to 5 times.
- Plate - Sunscorched Bulwark [Implemented]
    Flavor: "There is no shade in Zul'Farrak and no cover on those steps. Plate is the only cover on offer."
    (2) Set: You take 30% less damage from enemies you have not yet struck.
    (4) Set: While five or more enemies are within 10 yards, healing you receive is increased by 30%.

Maraudon - Pristine Waters - Levels: 43-53
- Cloth - Springwell Adept [Implemented]
    Flavor: "The deep water in Maraudon is the cleanest thing in Desolace. Theradras keeps it that way."
    (2) Set: Your spells are 20% more effective while you are standing in water.
    (4) Set: Your spells restore 1% of your maximum mana when they strike an enemy. (Can only occur once every 3 sec.)
- Leather - Zaetar's Wanderer [Implemented]
    Flavor: "Zaetar's spirit is still down here with his wife. The centaur were their children and neither is proud."
    (2) Set: You swim 50% faster, breathe underwater indefinitely, and take 20% less Nature damage.
    (4) Set: Elementals you damage are destabilised, taking 15% additional Nature and Frost damage for 12 sec.
- Mail - Waterheart Guardian [Implemented]
    Flavor: "Theradras holds the heart of Maraudon and the last clean water in Desolace. She is not sharing."
    (2) Set: Your attacks against Elementals deal 20% additional damage.
    (4) Set: Killing an Elemental grants 20% increased healing received for 15 sec.
- Plate - Deepspring Sentinel [Implemented]
    Flavor: "The waterfall drowns every sound in the lower halls. So does the armor. Something will hear you regardless."
    (2) Set: Healing you receive is increased by 12% while below 60% health.
    (4) Set: Standing in water increases your health regeneration by 150%.

Sunken Temple - Levels: 45-55
- Cloth - Hakkari Exorcist [Implemented]
    Flavor: "The Atal'ai built this temple to call Hakkar back. It sank with them inside and they kept praying."
    (2) Set: Your spells deal 18% additional damage to Dragonkin.
    (4) Set: Your spells deal 20% additional damage to enemies that are casting.
- Leather - Dragonchain Breaker [Implemented]
    Flavor: "Eranikus is chained at the bottom of the Sunken Temple and has been for a very long time."
    (2) Set: Your attacks against enemies casting or channeling deal 35% additional damage.
    (4) Set: Striking a casting enemy grants 25% critical strike chance for 8 sec. (Can only occur once every 12 sec.)
- Mail - Bloodcult Interloper [Implemented]
    Flavor: "Jammal'an has been promising Hakkar's return for centuries. His congregation is patient."
    (2) Set: Shadow damage you take is reduced by 40%.
    (4) Set: Killing an enemy restores 15% of your maximum health.
- Plate - Sunken Vanguard [Implemented]
    Flavor: "The temple is under the swamp and under the water. Every step in plate is a decision."
    (2) Set: Dragonkin and Undead attacking you deal 20% less damage.
    (4) Set: While below 40% health, healing you receive is increased by 30%.

Blackrock Depths - Prison - Levels: 47-57
- Cloth - Ironhold Interrogator [Implemented]
    Flavor: "The Dark Iron keep prisoners for questioning, and the questioning does not end. Gerstahn is thorough."
    (2) Set: Your spells deal 15% additional damage to enemies that are rooted or held.
    (4) Set: Killing an enemy grants 20% spell power for 20 sec.
- Leather - Cellblock Escapist [Implemented]
    Flavor: "Marshal Windsor is in a cell down here with something Stormwind needs to hear. He has been waiting."
    (2) Set: You are immune to root effects.
    (4) Set: Your attacks against enemies above 90% health deal 40% additional damage.
- Mail - Grimstone Gladiator [Implemented]
    Flavor: "The Ring of Law drops you in a pit and lets Grimstone announce your death to a paying crowd."
    (2) Set: Your attacks against an enemy standing on its own deal 15% additional damage.
    (4) Set: Killing an enemy while no allies are within 20 yards restores 12% of your maximum health.
- Plate - Dark Iron Bulwark [Implemented]
    Flavor: "Blackrock Depths is a Dark Iron city, not a dungeon. The prison is only the front hall."
    (2) Set: You take 20% less damage from Humanoids.
    (4) Set: While four or more enemies are within 8 yards, your armor is increased by 25%.

Blackrock Depths - Upper City - Levels: 51-61
- Cloth - Grim Guzzler Patron [Implemented]
    Flavor: "The Grim Guzzler serves Dark Iron ale to anyone who walks in armed. It is that sort of bar."
    (2) Set: Blacksmithing skill increased by 15.
    (4) Set: Every third item you craft with Blacksmithing yields one additional item.
- Leather - Moira's Shadow [Implemented]
    Flavor: "Princess Moira is down here and does not wish to be rescued. That complicates the contract."
    (2) Set: Your Blacksmithing skill counts as 25 higher.
    (4) Set: Mining yields one additional ore.
- Mail - Thaurissan's Bane [Implemented]
    Flavor: "Thaurissan summoned Ragnaros into his own city. The Dark Iron have lived with it ever since."
    (2) Set: Your attacks against Humanoids and Elementals deal 18% additional damage.
    (4) Set: Killing an Elemental grants 15% less Fire damage taken and 10% attack power for 20 sec.
- Plate - Black Anvil Warden [Implemented]
    Flavor: "The Black Anvil has forged for the Dark Iron since Thaurissan's day. It is still warm."
    (2) Set: Your equipment repairs to full whenever you leave combat.
    (4) Set: Fire damage you take is reduced by 20%.

Dire Maul - East - Levels: 53-63
- Cloth - Pusillin's Pursuer [Implemented]
    Flavor: "Pusillin will take your book and run. He will keep running. That is the east wing."
    (2) Set: Your spells deal 20% additional damage to enemies that are fleeing.
    (4) Set: Your spells root the target for 2 sec. (Can only occur once every 15 sec.)
- Leather - Alzzin's Stalker [Implemented]
    Flavor: "Alzzin has been reshaping the east wing into something worse. It is going well for him."
    (2) Set: You move 20% faster while in combat.
    (4) Set: Your attacks against fleeing enemies deal 40% additional damage.
- Mail - Satyrwood Prowler [Implemented]
    Flavor: "The east wing is overgrown and full of satyrs. Both facts are Alzzin's doing."
    (2) Set: Your attacks uproot Elementals, stunning them for 2 sec. (Can only occur once every 20 sec.)
    (4) Set: Killing an Elemental reduces Nature damage you take by 10% for 20 sec, stacking up to 5 times.
- Plate - Thornhoof's Executioner [Implemented]
    Flavor: "Zevrim Thornhoof performs his sacrifices on a schedule. Interrupting it is the job."
    (2) Set: Shadow damage you take is reduced by 20% and you cannot be feared.
    (4) Set: While above 90% health, your damage is increased by 12%.

Dire Maul - North - Levels: 55-65
- Cloth - Gordok Pretender [Implemented]
    Flavor: "Kill King Gordok and the ogres will crown you instead. They are not particular about species."
    (2) Set: Your spells reduce a Giant's damage by 15% for 6 sec.
    (4) Set: Killing a Giant grants 25% casting speed for 10 sec.
- Leather - Tribute Runner [Implemented]
    Flavor: "The tribute run rewards restraint, which is not what most parties bring to an ogre hall."
    (2) Set: You take 25% less damage from enemies you have not attacked.
    (4) Set: Melee attacks against you have a 10% reduced chance to critically strike.
- Mail - Gordok Duelist [Implemented]
    Flavor: "Gordok ogres respect exactly one thing, and it is not diplomacy."
    (2) Set: Killing an enemy grants 10% maximum health for 5 min, stacking up to 3 times.
    (4) Set: Killing an enemy while no ally is within 20 yards grants 30% attack power for 15 sec.
- Plate - Crown Claimant [Implemented]
    Flavor: "The north wing crowns whoever kills the king. The crown is real. The reign is short."
    (2) Set: The first enemy you strike each combat takes 25% additional damage for 15 sec.
    (4) Set: Killing an elite grants a crown of authority, increasing all damage by 15% for 30 sec.

Dire Maul - West - Levels: 55-65
- Cloth - Shen'dralar Loremaster [Implemented]
    Flavor: "The Shen'dralar hid here with their books for ten thousand years. Tortheldrin has been draining them for most of it."
    (2) Set: Enchanting skill increased by 15.
    (4) Set: Every third item you craft with Enchanting yields one additional item.
- Leather - Eldreth Whisper [Implemented]
    Flavor: "The Eldreth are still in the library and still will not be quiet."
    (2) Set: Your Enchanting skill counts as 25 higher.
    (4) Set: Items you craft with Enchanting yield one additional item.
- Mail - Tortheldrin's Leech [Implemented]
    Flavor: "Tortheldrin fed his own people to a demon to keep the lights on. The Shen'dralar have not been told."
    (2) Set: Your attacks restore 2% of your maximum resource.
    (4) Set: Your attacks against casting enemies deal 25% additional damage.
- Plate - Immol'thar's Gaoler [Implemented]
    Flavor: "Immol'thar is held by five crystals and is extremely tired of it."
    (2) Set: Arcane damage you take is reduced by 25%.
    (4) Set: Taking Arcane damage grants 12% increased armor for 15 sec.

Lower Blackrock Spire - Levels: 55-65
- Cloth - Spire Tactician [Implemented]
    Flavor: "Lower Blackrock Spire is orcs, dragonkin, and one very large spider. Robes are a leap of faith."
    (2) Set: Your spells deal 20% additional damage to Dragonkin, Humanoids, and Beasts.
    (4) Set: Killing an enemy grants 25% spell power for 15 sec. (Can only occur once every 30 sec.)
- Leather - Webcave Skitterer [Implemented]
    Flavor: "The spider cave is off the main hall and easy to miss. The webs are the warning."
    (2) Set: You are immune to root effects and take 15% less damage from Beasts.
    (4) Set: Escaping a web or root grants 30% attack speed for 8 sec.
- Mail - Voone's Recruit [Implemented]
    Flavor: "War Master Voone drills Rend's orcs day and night. They are ready. You may not be."
    (2) Set: Your attacks against Humanoids and Dragonkin deal 18% additional damage.
    (4) Set: Killing an enemy in a group of three or more grants 15% attack power for 12 sec.
- Plate - Contested Aegis [Implemented]
    Flavor: "Blackrock Spire is contested by orcs above and dragons below. You are walking into somebody else's war."
    (2) Set: You take 12% less damage from enemies you have already struck.
    (4) Set: Fighting four or more enemies at once grants 20% increased armor.

Upper Blackrock Spire - Levels: 58-65
    Note: Added during implementation. The module generates a set for this
    instance but the original document had no entry for it, so it would have
    kept a random placeholder bonus while every other dungeon was authored.
- Cloth - Emberseer's Unbinding [Implemented]
    Flavor: "Pyroguard Emberseer is chained to a wall while orcs drain him. He is aware of this."
    (2) Set: Your Fire spells deal 22% additional damage.
    (4) Set: Killing an enemy grants 20% spell power for 15 sec.
- Leather - Rookery Eggbreaker [Implemented]
    Flavor: "The rookery is a floor of dragon eggs. They hatch on a timer nobody controls."
    (2) Set: Your attacks against Dragonkin deal 25% additional damage.
    (4) Set: Killing a Dragonkin grants 20% attack speed for 12 sec.
- Mail - Dragonspire Runewatcher [Implemented]
    Flavor: "Dragonspire Hall has seven runes and a dragonkin standing on each one. Nobody moves first."
    (2) Set: Your attacks reduce the target's casting speed by 20% for 8 sec.
    (4) Set: Enemies that are casting take 25% additional damage from you.
- Plate - Rend's Warband [Implemented]
    Flavor: "Rend Blackhand still calls himself Warchief up here and the Dark Horde still answers to it."
    (2) Set: Humanoids and Dragonkin attacking you deal 20% less damage.
    (4) Set: Killing an enemy grants 8% armor for 20 sec, stacking up to 4 times.

Scholomance - Levels: 55-65
- Cloth - Barov Deathscholar [Implemented]
    Flavor: "Scholomance teaches necromancy to anyone who applies. The Barovs donated the building, and then the bodies."
    (2) Set: Your Shadow spells restore 2% of your maximum health when they deal damage.
    (4) Set: Your spells deal 20% additional damage to Undead.
- Leather - Cadaver Courier [Implemented]
    Flavor: "The students practice on whatever is delivered. Delivery is the part nobody discusses."
    (2) Set: Your attacks against summoned enemies deal 20% additional damage.
    (4) Set: Enemies that die near you burst, dealing damage to other enemies within 8 yards equal to 8% of the slain enemy's maximum health.
- Mail - Gandling's Castoff [Implemented]
    Flavor: "Darkmaster Gandling runs the school and expels people through the floor."
    (2) Set: Disease and Shadow damage you take is reduced by 25%.
    (4) Set: Your attacks afflict the target with a wasting disease, dealing Shadow damage over 6 sec.
- Plate - Frostbound Anchor [Implemented]
    Flavor: "Ras Frostwhisper was a man who accepted an offer. He teaches now, after a fashion."
    (2) Set: You cannot be banished or feared.
    (4) Set: Breaking free of a control effect grants 25% increased damage for 8 sec.

Stratholme - Main Gate - Levels: 55-65
- Cloth - Plaguefire Zealot [Implemented]
    Flavor: "Arthas purged Stratholme to stop the plague. The plague stayed anyway."
    (2) Set: Your spells spread to one additional enemy within 5 yards for 30% of the damage.
    (4) Set: Your Fire spells deal 20% additional damage.
- Leather - Crossfire Partisan [Implemented]
    Flavor: "The Crusade holds one half of Stratholme and the Scourge the other. Neither will leave."
    (2) Set: Your attacks against Undead and Humanoids deal 15% additional damage.
    (4) Set: Killing an enemy grants 25% haste for 10 sec. (Can only occur once every 20 sec.)
- Mail - Ziggurat Torchbearer [Implemented]
    Flavor: "The ziggurats keep the Scourge's dead on their feet. Pull them down or fight the city twice."
    (2) Set: Your attacks deal 18% additional damage to enemies afflicted by a damage over time effect.
    (4) Set: Enemies you kill burn, dealing Fire damage to enemies within 5 yards for 6 sec.
- Plate - Cinderguard Watchman [Implemented]
    Flavor: "Stratholme burned once and never quite stopped. Every street is somebody's worst day."
    (2) Set: Fire damage you take is reduced by 25%.
    (4) Set: Holding a single position grants 30% increased armor until you move.

Stratholme - Service Entrance - Levels: 55-65
- Cloth - Backroad Invoker [Implemented]
    Flavor: "Baron Rivendare keeps a horse he does not need and will not share."
    (2) Set: Your spells deal 15% additional damage while in combat.
    (4) Set: Killing an elite grants 30% casting speed for 8 sec.
- Leather - Shortcut Runner [Implemented]
    Flavor: "The service entrance is the quick way to the Baron. Quick is relative and the clock is real."
    (2) Set: Your movement speed is increased by 10%.
    (4) Set: You cannot be dazed or slowed while above 75% health.
- Mail - Ramstein's Unhorser [Implemented]
    Flavor: "Ramstein the Gorger stands between the gate and the Baron. He is precisely as subtle as the name."
    (2) Set: Your attacks slow the target by 40% for 4 sec. (Can only occur once every 10 sec.)
    (4) Set: Killing an enemy grants 30% attack power for 12 sec.
- Plate - Deathcharger's Bane [Implemented]
    Flavor: "Rivendare was among the first Arthas raised. He has had time to decorate."
    (2) Set: You take 20% less damage from Undead.
    (4) Set: Each consecutive second you remain in melee combat increases your damage reduction by 1%, up to 20%.

Hellfire Ramparts - Levels: 57-67
- Cloth - Ramparts Skywatcher [Implemented]
    Flavor: "The Ramparts are the outer wall of Hellfire Citadel and open to the sky. There is nowhere to stand out of sight."
    (2) Set: Enemies more than 15 yards from you take 20% additional damage from your spells.
    (4) Set: Your spells slow the target by 50% for 4 sec.
- Leather - Nazan's Shadow [Implemented]
    Flavor: "Nazan circles above the Ramparts and is not decorative."
    (2) Set: Dragonkin and Demons attacking you deal 25% less damage.
    (4) Set: Attacks made from behind your target deal 40% additional damage.
- Mail - Hellfire Longgunner [Implemented]
    Flavor: "Hellfire Citadel is four instances in one fortress. The Ramparts are the polite introduction."
    (2) Set: Your attacks deal 20% additional damage to enemies more than 15 yards away.
    (4) Set: Every 10 sec, your next attack deals 50% additional damage.
- Plate - Omor's Anchor [Implemented]
    Flavor: "Omor the Unscarred earned that name and intends to keep it."
    (2) Set: You take 25% less damage from area attacks.
    (4) Set: The first enemy to strike you each combat takes 30% additional damage for 15 sec.

Blood Furnace - Levels: 59-68
- Cloth - Furnace Alchemist [Implemented]
    Flavor: "The Blood Furnace turns orcs into fel orcs using Magtheridon's blood. It is running at capacity."
    (2) Set: Your spells deal 18% additional damage to Demons.
    (4) Set: Enemies that die near you rupture, dealing damage to other enemies within 8 yards equal to 8% of the slain enemy's maximum health.
- Leather - The Maker's Discard [Implemented]
    Flavor: "The Maker builds fel orcs to order. The raw material walks in on its own feet."
    (2) Set: Your attacks reduce the target's damage by 20% for 8 sec.
    (4) Set: Your critical strikes deal 25% additional damage.
- Mail - Keli'dan's Bloodletter [Implemented]
    Flavor: "Keli'dan drains a pit lord for a living. The work has changed him."
    (2) Set: Your abilities cost 15% less mana.
    (4) Set: Falling below 50% health grants 15% attack power for 10 sec. (Can only occur once every 30 sec.)
- Plate - Furnace Ironhide [Implemented]
    Flavor: "Everything in the Blood Furnace was a person before it became an ingredient."
    (2) Set: You take 20% less damage from Demons.
    (4) Set: Each Demon you kill grants 5% maximum health for 60 sec, stacking up to 5 times.

Slave Pens - Levels: 60-69
- Cloth - Cenarion Liberator [Implemented]
    Flavor: "The naga work their slaves until the marsh runs dry. The Cenarion Expedition wants it stopped."
    (2) Set: You are immune to snare effects.
    (4) Set: Breaking free of a control effect grants 15% haste for 8 sec.
- Leather - Mennu's Turncoat [Implemented]
    Flavor: "Mennu the Betrayer sold his own people to the naga. The broken remember the name."
    (2) Set: You cannot be rooted.
    (4) Set: Enemies that strike you are snared for 6 sec.
- Mail - Coilfang Netcaster [Implemented]
    Flavor: "The Slave Pens are the shallow end of Coilfang. It worsens considerably deeper in."
    (2) Set: Your attacks deal 20% additional damage while you are standing in water.
    (4) Set: Killing an enemy restores 10% of your maximum health.
- Plate - Zangarmarsh Diver [Implemented]
    Flavor: "Vashj is draining Zangarmarsh through this place. The pens are only the intake."
    (2) Set: You breathe underwater indefinitely and swim 50% faster.
    (4) Set: Allies within 15 yards gain 10% increased armor.

Underbog - Levels: 61-70
- Cloth - Underbog Bloomtender [Implemented]
    Flavor: "The Underbog grows over anything given a week. Do not set anything down."
    (2) Set: Your Nature spells root the target for 2 sec every 15 sec.
    (4) Set: Rooted enemies take 20% additional damage from you.
- Leather - Hungarfen's Sporewalker [Implemented]
    Flavor: "Hungarfen sheds spores that root wherever they land. Including in you."
    (2) Set: You cannot be rooted and move 15% faster.
    (4) Set: Breaking free of a root heals you for 10% of your maximum health.
- Mail - Blackstalker's Wake [Implemented]
    Flavor: "The Black Stalker sits at the bottom of the Underbog and the naga leave it alone. Consider that."
    (2) Set: Nature damage you take is reduced by 40%.
    (4) Set: Taking Nature damage grants 20% attack power for 8 sec.
- Plate - Underbog Bogtrekker [Implemented]
    Flavor: "The Underbog is a swamp built inside a building. Plate sinks in both."
    (2) Set: Enemies within 10 yards deal 8% less damage to you.
    (4) Set: Each enemy within 10 yards grants 4% armor, up to 20%.

Mana-Tombs - Levels: 62-71
- Cloth - Consortium Appraiser [Implemented]
    Flavor: "The ethereals are looting a draenei tomb and selling it back. The Consortium calls this commerce."
    (2) Set: Shadow damage you take is reduced by 20%.
    (4) Set: Taking Shadow damage grants 10% spell power for 10 sec, stacking up to 3 times.
- Leather - Shaffar's Unveiler [Implemented]
    Flavor: "Nexus-Prince Shaffar has claimed the Mana-Tombs. The draenei buried here were not consulted."
    (2) Set: You move 15% faster and cannot be tracked.
    (4) Set: Striking an enemy that has not yet engaged you deals 35% additional damage.
- Mail - Pandemonius's Silencer [Implemented]
    Flavor: "Pandemonius is a void creature wearing a shape. Do not look directly at it for long."
    (2) Set: Casting enemies you strike are silenced for 2 sec. (Can only occur once every 20 sec.)
    (4) Set: Your attacks slow the target's casting by 20% for 8 sec, stacking up to 3 times.
- Plate - Draenei Tomb-Keeper [Implemented]
    Flavor: "The Mana-Tombs held draenei dead for generations. Now they hold inventory."
    (2) Set: You cannot be feared.
    (4) Set: While below 40% health, magical damage you take is reduced by 40%.

Auchenai Crypts - Levels: 63-72
- Cloth - Auchenai Deathtender [Implemented]
    Flavor: "The Auchenai tended draenei dead for centuries, and then something changed their minds."
    (2) Set: Your spells deal 20% additional damage to rooted or slowed enemies.
    (4) Set: Your spells deal 20% additional damage while you stand still.
- Leather - Shirrak's Vigil [Implemented]
    Flavor: "Shirrak the Dead Watcher does not move and does not need to."
    (2) Set: Your attack speed is increased by 10%.
    (4) Set: Striking a casting enemy grants 20% attack speed for 6 sec. (Can only occur once every 10 sec.)
- Mail - Maladaar's Sentinel [Implemented]
    Flavor: "Exarch Maladaar guarded these crypts in life. He guards them far harder now."
    (2) Set: Enemies within 15 yards suffer damage equal to 1% of their maximum health every 3 sec.
    (4) Set: Killing an enemy restores 5% of your maximum health to you and allies within 15 yards.
- Plate - Auchenai Gravedigger [Implemented]
    Flavor: "The Auchenai raise their own dead these days and see no contradiction in it."
    (2) Set: You take 20% less damage from Undead and cannot be feared.
    (4) Set: While below 50% health, you take 25% less damage.

The Escape From Durnholde - Levels: 64-73
- Cloth - Taretha's Mercy [Implemented]
    Flavor: "Taretha Foxton risked everything to free one orc slave. History remembers what it cost her."
    (2) Set: Your spells restore 2% of your maximum health when they deal damage.
    (4) Set: You deal 12% additional damage while an ally is within 10 yards.
- Leather - Durnholde Smuggler [Implemented]
    Flavor: "Thrall escaped Durnholde once already. Your job is to see that he still does."
    (2) Set: Enemies attacking your allies take 20% additional damage from you.
    (4) Set: Killing an enemy grants you and allies within 10 yards 15% haste for 8 sec.
- Mail - Blackmoore's Gladiator [Implemented]
    Flavor: "Blackmoore raised Thrall as a gladiator and a weapon. It worked rather better than intended."
    (2) Set: You deal 15% additional damage to enemies that have not engaged you.
    (4) Set: Surviving a hit dealing more than 25% of your maximum health grants 20% damage reduction for 6 sec.
- Plate - Bronze Timekeeper [Implemented]
    Flavor: "The Infinite Dragonflight want Thrall to die in this keep. The bronze want otherwise."
    (2) Set: Allies within 10 yards gain 12% increased armor.
    (4) Set: While below 40% health, you and allies within 10 yards take 15% less damage.

Sethekk Halls - Levels: 65-73
- Cloth - Sethekk Ravenpriest [Implemented]
    Flavor: "The Sethekk worship a raven god their own people call a curse."
    (2) Set: Your Arcane spells blind the target, reducing its chance to hit by 15% for 6 sec.
    (4) Set: Your Arcane spells deal 20% additional damage.
- Leather - Ikiss's Farseer [Implemented]
    Flavor: "Talon King Ikiss is trying to open a way to Anzu, and he is closer than anyone finds comfortable."
    (2) Set: You take 25% less Arcane damage and cannot be tracked.
    (4) Set: Attacking an enemy that has not engaged you deals 40% additional damage.
- Mail - Syth's Elementalist [Implemented]
    Flavor: "Darkweaver Syth fights with every element he can reach. He can reach several."
    (2) Set: Your attacks silence the target for 2 sec. (Can only occur once every 25 sec.)
    (4) Set: Your attacks root the target for 2 sec. (Can only occur once every 20 sec.)
- Plate - Arakkoa Cursebearer [Implemented]
    Flavor: "The arakkoa were cursed into this shape. The Sethekk have decided to embrace it."
    (2) Set: Area attacks deal 35% less damage to you.
    (4) Set: Surviving a hit dealing more than 25% of your maximum health grants 25% increased damage for 10 sec.

Shadow Labyrinth - Levels: 67-75
- Cloth - Auchindoun Shadowbreaker [Implemented]
    Flavor: "The Shadow Council meets beneath Auchindoun and has summoned something with no shape."
    (2) Set: Your Shadow spells deal 20% additional damage.
    (4) Set: Your spells deal 20% additional damage to summoned enemies.
- Leather - Blackheart's Defiance [Implemented]
    Flavor: "Blackheart turns your own party against you. Bring people you trust, or people you will not miss."
    (2) Set: You cannot be charmed, feared, or mind controlled.
    (4) Set: Breaking free of a charm effect grants 30% critical strike chance for 8 sec.
- Mail - Vorpil's Portalkeeper [Implemented]
    Flavor: "Grandmaster Vorpil holds open a portal to somewhere that should not connect."
    (2) Set: You cannot be silenced.
    (4) Set: Your attacks deafen the target, reducing its casting speed by 25% for 8 sec.
- Plate - Murmur's Herald [Implemented]
    Flavor: "Murmur sits at the bottom of the Labyrinth and is mostly sound. Mostly is doing a great deal of work."
    (2) Set: Demons and Undead attacking you deal 20% less damage.
    (4) Set: Breaking free of a control effect grants 20% damage reduction for 10 sec.

Shattered Halls - Levels: 67-75
- Cloth - Bladefist Zealot [Implemented]
    Flavor: "Kargath Bladefist cut off his own hand to escape a slave pen. He has not mellowed."
    (2) Set: Your spells cost 20% less mana.
    (4) Set: Your spells strike one additional enemy within 8 yards for 25% of the damage.
- Leather - Shattered Hand Duelist [Implemented]
    Flavor: "The Shattered Hand severed their own hands to prove a point. They are still making it."
    (2) Set: Humanoids attacking you deal 25% less damage.
    (4) Set: Your attacks reduce the target's damage by 30% for 8 sec.
- Mail - Shattered Halls Marauder [Implemented]
    Flavor: "The Shattered Halls are a fel orc barracks at full strength. There is no quiet route."
    (2) Set: You take 20% less damage while moving.
    (4) Set: For each enemy you have struck in the last 6 sec, gain 4% attack power, up to 24%.
- Plate - Kargath's Champion [Implemented]
    Flavor: "Kargath holds the deepest hall in Hellfire Citadel. Everything between him and the door is loyal."
    (2) Set: You cannot be disarmed.
    (4) Set: Killing an enemy grants 8% attack speed and 8% armor for 15 sec, stacking up to 3 times.

The Botanica - Levels: 67-75
- Cloth - Botanica Cultivator [Implemented]
    Flavor: "The Botanica grows things that should not exist, in a place that should not be there."
    (2) Set: Summoned enemies you damage decay, suffering Nature damage over 9 sec.
    (4) Set: Killing a summoned enemy restores 6% of your maximum mana.
- Leather - Freywinn's Blightsower [Implemented]
    Flavor: "High Botanist Freywinn plants saplings mid-fight. They are not decorative."
    (2) Set: Your attacks reduce healing received by the target by 50% for 8 sec.
    (4) Set: Your attacks afflict the target with a blight dealing Nature damage over 6 sec.
- Mail - Tempest Greenkeeper [Implemented]
    Flavor: "Kael'thas built a greenhouse into a naaru warship. Nobody has asked him why."
    (2) Set: Each enemy within 15 yards grants 10% attack power, up to 30%.
    (4) Set: Killing a summoned enemy grants 25% attack speed for 12 sec.
- Plate - Warp Splinter's Bark [Implemented]
    Flavor: "Warp Splinter is a tree that Tempest Keep decided to keep. It has opinions about visitors."
    (2) Set: You are immune to root effects.
    (4) Set: Enemies that strike you are entangled, losing 40% movement speed for 4 sec.

The Mechanar - Levels: 67-75
- Cloth - Mechanar Machinist [Implemented]
    Flavor: "The Mechanar builds Kael'thas's machines faster than anyone can break them."
    (2) Set: Your spells overload Mechanical enemies, stunning them for 2 sec every 15 sec.
    (4) Set: Enemies you kill overload, dealing damage to other enemies within 6 yards equal to 10% of the slain enemy's maximum health.
- Leather - Gatewatcher Scavenger [Implemented]
    Flavor: "The Gatewatchers are assembled on site and never quite finish being assembled."
    (2) Set: Your attacks reduce a Mechanical enemy's armor by 25% for 12 sec.
    (4) Set: Destroying a Mechanical enemy grants 15% attack power for 12 sec.
- Mail - Pathaleon's Reckoner [Implemented]
    Flavor: "Pathaleon the Calculator does not so much fight you as compute you."
    (2) Set: Each consecutive attack against the same target deals 6% more damage, up to 30%. Switching targets resets the bonus.
    (4) Set: Your attacks restore 2% of your maximum resource.
- Plate - Mechanar Ironclad [Implemented]
    Flavor: "Everything in the Mechanar is metal, moving, and indifferent."
    (2) Set: You take 20% less damage from Mechanical enemies.
    (4) Set: Each Mechanical enemy destroyed grants 6% armor for 30 sec, stacking up to 4 times.

The Steamvault - Levels: 67-75
- Cloth - Steamvault Distiller [Implemented]
    Flavor: "The Steamvault is where the naga actually drain Zangarmarsh. The steam is the marsh leaving."
    (2) Set: Fire and Frost damage you take is reduced by 50%.
    (4) Set: Taking Fire damage grants 15% spell power for 8 sec.
- Leather - Thespia's Floodcaller [Implemented]
    Flavor: "Hydromancer Thespia brings the water down in sheets. There is no dry corner."
    (2) Set: You take 25% less damage from area attacks.
    (4) Set: Your attacks against slowed enemies deal 30% additional damage.
- Mail - Kalithresh's Brewer [Implemented]
    Flavor: "Warlord Kalithresh drinks from the distillers to make himself worse. It works."
    (2) Set: Your attacks against casting enemies deal 25% additional damage.
    (4) Set: Striking a casting enemy restores 15% of your maximum resource. (Can only occur once every 15 sec.)
- Plate - Vashj's Pumpwright [Implemented]
    Flavor: "Vashj's pumps run through the Steamvault. Break them and the marsh gets a few more years."
    (2) Set: Frost and Nature damage you take is each reduced by 20%.
    (4) Set: Standing in water grants 20% increased armor.

Magisters' Terrace - Levels: 68-75
- Cloth - Quel'Danas Spellbreaker [Implemented]
    Flavor: "Kael'thas came home to Quel'Danas to finish what Tempest Keep started."
    (2) Set: Your spells deal 20% additional damage to enemies that are casting.
    (4) Set: Killing an enemy grants 25% spell power for 15 sec.
- Leather - Delrissa's Gambit [Implemented]
    Flavor: "Priestess Delrissa brings friends and they do not fight fair. Neither should you."
    (2) Set: Each enemy within 10 yards increases your damage by 4%, up to 20%.
    (4) Set: Killing an enemy while three or more enemies are nearby grants 20% critical strike chance for 10 sec.
- Mail - Fireheart's Crystalmark [Implemented]
    Flavor: "Selin Fireheart feeds on the crystals in the walls. Break them, or fight him twice."
    (2) Set: You take 15% less damage while three or more enemies are engaged.
    (4) Set: Every third attack against the same target grants 20% critical strike chance for 8 sec.
- Plate - Sunfury Defector [Implemented]
    Flavor: "Kael'thas was the last hope of his people and sold them regardless. The Terrace is where that ends."
    (2) Set: Magical damage you take is reduced by 4% for each enemy within 10 yards, up to 20%.
    (4) Set: Fully resisting a spell grants 30% increased damage for 8 sec.

The Arcatraz - Levels: 68-75
- Cloth - Manastorm's Boast [Implemented]
    Flavor: "Millhouse Manastorm is locked in the Arcatraz and would like everyone to know how powerful he is."
    (2) Set: Your spells deal 20% additional damage to enemies that have not engaged you.
    (4) Set: Your spells slow the target by 50% for 5 sec. (Can only occur once every 10 sec.)
- Leather - Naaru Sealbreaker [Implemented]
    Flavor: "The naaru built the Arcatraz to hold things nobody should release. The seals are open."
    (2) Set: You take 25% less damage from enemies you have not yet struck.
    (4) Set: Your first attack against each enemy deals 45% additional damage.
- Mail - Skyriss's Reckoning [Implemented]
    Flavor: "Harbinger Skyriss is the reason the Arcatraz has walls. He is out now."
    (2) Set: Being struck by three or more different enemies within 5 sec grants a shield absorbing 20% of your maximum health. (Can only occur once every 60 sec.)
    (4) Set: While five or more enemies are in combat with you, your chance to hit is increased by 10%.
- Plate - Arcatraz Jailor [Implemented]
    Flavor: "Every cell held something worse than the last. Someone has been opening them in order."
    (2) Set: Your attacks stun the target for 2 sec. (Can only occur once every 25 sec.)
    (4) Set: Breaking free of a control effect grants 25% increased armor for 10 sec.

The Black Morass - Levels: 68-75
- Cloth - Medivh's Riftsealer [Implemented]
    Flavor: "Medivh is opening the Dark Portal and you are here to let him. History is uncomfortable work."
    (2) Set: Your spells deal 30% additional damage to summoned enemies.
    (4) Set: Killing a summoned enemy restores 20% of your maximum mana.
- Leather - Infinite Interceptor [Implemented]
    Flavor: "The Infinite Dragonflight want the Portal to fail. That sounds better than it is."
    (2) Set: Enemies within 12 yards are slowed by 25%.
    (4) Set: Killing an enemy grants 15% attack power for 15 sec.
- Mail - Aeonus Wavebreaker [Implemented]
    Flavor: "Eighteen waves stand between Medivh and the Portal. Aeonus is the last of them."
    (2) Set: For each enemy you have struck in the last 6 sec, your damage increases by 3%, up to 30%.
    (4) Set: Killing an enemy grants 10% maximum health for 60 sec, stacking up to 5 times.
- Plate - Darkportal Sentinel [Implemented]
    Flavor: "Protect the man who doomed two worlds. The bronze insist it is necessary."
    (2) Set: Enemies within 8 yards deal 10% less damage to you.
    (4) Set: While standing still, you take 25% less damage from all sources.

Utgarde Keep - Levels: 68-80
- Cloth - Ingvar's Undoing [Implemented]
    Flavor: "The vrykul of Utgarde are waking up, and they are all eight feet of unhappy."
    (2) Set: Your spells deal 20% additional damage to Undead.
    (4) Set: Enemies you kill leave a withering pall, slowing enemies within 8 yards by 30% for 6 sec.
- Leather - Skarvald's Grudge [Implemented]
    Flavor: "Skarvald and Dalronn argue through the entire fight and keep arguing after one of them dies."
    (2) Set: Your attacks against enemies already fighting someone else deal 18% additional damage.
    (4) Set: Killing an enemy grants 25% increased damage for 10 sec.
- Mail - Giantsbane Marksman [Implemented]
    Flavor: "Ingvar the Plunderer does not accept his own death the first time."
    (2) Set: Your critical strike chance is increased by 20% against Giants and Undead.
    (4) Set: Your damage is increased by 15% against targets with more current health than you.
- Plate - Utgarde Doorwarden [Implemented]
    Flavor: "Utgarde Keep is a vrykul hall built for men twice your size. The doorways are the first hint."
    (2) Set: Shadow damage you take is reduced by 30%.
    (4) Set: Killing an enemy while below 50% health restores 15% of your maximum health.

The Nexus - Levels: 69-80
- Cloth - Malygos's Reckoning [Implemented]
    Flavor: "Malygos has decided mortal magic was a mistake. The Nexus is where he corrects it."
    (2) Set: Your Arcane damage is increased by 20% and Dragonkin take 15% more damage from you.
    (4) Set: You cannot be silenced.
- Leather - Telestra's Mirror [Implemented]
    Flavor: "Keristrasza is held in the Nexus against her will. That is the polite version."
    (2) Set: Your attacks against summoned or duplicated enemies deal 20% additional damage.
    (4) Set: Killing a summoned enemy grants 20% attack speed for 10 sec.
- Mail - Keristrasza's Chains [Implemented]
    Flavor: "Grand Magus Telestra splits into three, and each of her is annoyed."
    (2) Set: You are immune to freezing and root effects.
    (4) Set: Breaking free of a root grants 30% attack power for 10 sec.
- Plate - Arcane Confiscator [Implemented]
    Flavor: "The blue flight guarded magic for ten thousand years. Now they are confiscating it."
    (2) Set: You gain 12% increased armor while below 60% health.
    (4) Set: Enemies that cast at you are slowed by 30% for 5 sec.

Azjol-Nerub - Levels: 70-80
- Cloth - Hadronox's Shadow [Implemented]
    Flavor: "Azjol-Nerub was a nerubian empire before the Scourge took it. The architecture survived. Nobody else did."
    (2) Set: Your spells root the target for 2 sec. (Can only occur once every 15 sec.)
    (4) Set: Enemies within 10 yards are slowed by 50%.
- Leather - Azjol Swarmrunner [Implemented]
    Flavor: "Hadronox drags her prey down from above. Look at the ceiling. Once."
    (2) Set: Your attacks deal 3% additional damage for each enemy within 10 yards, up to 24%.
    (4) Set: Killing an enemy reduces damage you take by 5% for 10 sec, stacking up to 5 times.
- Mail - Anub'arak's Collapse [Implemented]
    Flavor: "Anub'arak was a nerubian king. Arthas killed him and then gave him the job back."
    (2) Set: Killing an enemy collapses the ground beneath nearby foes, slowing them by 40% for 4 sec.
    (4) Set: Your attacks root the target for 2 sec. (Can only occur once every 20 sec.)
- Plate - Silkbound Sentinel [Implemented]
    Flavor: "The whole kingdom is a web over a drop. Heavy armor does not help with the drop."
    (2) Set: You are immune to snare effects and take 25% less Nature damage.
    (4) Set: Surviving a hit dealing more than 25% of your maximum health grants 30% damage reduction for 10 sec.

Ahn'kahet: The Old Kingdom - Levels: 71-80
- Cloth - Volazj's Delusion [Implemented]
    Flavor: "Herald Volazj shows you your own party as monsters. Less an illusion than an opinion."
    (2) Set: While below 75% health, your spell damage is increased by 25%.
    (4) Set: Your spell power is increased by 6% for each 25% of health you are missing, up to 24%.
- Leather - Deepwhisper Warden [Implemented]
    Flavor: "The nerubians built Ahn'kahet over something older and stopped digging. It kept talking."
    (2) Set: Your attacks reduce healing received by the target by 30% for 8 sec.
    (4) Set: Striking a casting enemy restores 12% of your maximum health. (Can only occur once every 15 sec.)
- Mail - Taldaram's Larder [Implemented]
    Flavor: "Prince Taldaram is San'layn and regards this kingdom as a larder."
    (2) Set: Enemies within 10 yards suffer damage equal to 1% of their maximum health every 3 sec.
    (4) Set: Enemies below 50% health take 25% additional damage from you.
- Plate - Whisperproof Bulwark [Implemented]
    Flavor: "It is called the Old Kingdom because something was here before the kingdom."
    (2) Set: You cannot be charmed, feared, or put to sleep.
    (4) Set: While three or more enemies are within 8 yards, you cannot be critically struck.

Drak'Tharon Keep - Levels: 72-80
- Cloth - Drak'Tharon Hexweaver [Implemented]
    Flavor: "Drak'Tharon was a Drakkari fortress until the Scourge walked in. Both are still inside."
    (2) Set: Your spells deal 18% additional damage to enemies above 75% health.
    (4) Set: Your spells reduce the target's damage by 25% for 8 sec.
- Leather - Dred's Keeper [Implemented]
    Flavor: "King Dred is a devilsaur the trolls kept as a pet. That arrangement has lapsed."
    (2) Set: Beasts attacking you deal 20% less damage.
    (4) Set: Your critical strike chance against Beasts is increased by 20%.
- Mail - Trollgore's Leash [Implemented]
    Flavor: "Trollgore eats whatever falls in the courtyard and has grown accordingly."
    (2) Set: Your attacks prevent the target from being healed, reducing healing received by 40% for 10 sec.
    (4) Set: While within 10 yards of a corpse, your damage is increased by 20%.
- Plate - Zul'Drak Gatekeeper [Implemented]
    Flavor: "The keep guards the road into Zul'Drak. Whoever holds it holds the door."
    (2) Set: Undead and Beasts attacking you deal 15% less damage.
    (4) Set: Killing an enemy grants 10% increased damage for 20 sec, stacking up to 2 times.

Violet Hold - Levels: 73-80
- Cloth - Dalaran Lockdown Adept [Implemented]
    Flavor: "The Violet Hold is Dalaran's prison, and the doors are opening on a schedule."
    (2) Set: Your spells slow the target by 30% for 4 sec.
    (4) Set: Slowed enemies take 20% additional damage from your spells.
- Leather - Sinclari's Vanguard [Implemented]
    Flavor: "Lieutenant Sinclari holds the entrance and will not come inside. She has seen the roster."
    (2) Set: While no enemy is within 10 yards, you gain 15% movement speed.
    (4) Set: Your first attack against each enemy deals 35% additional damage.
- Mail - Kirin Tor Suppressor [Implemented]
    Flavor: "Every cell in the Violet Hold contains something the Kirin Tor could not kill."
    (2) Set: Your attacks reduce the target's casting speed by 20% for 8 sec.
    (4) Set: Enemies that are casting take 20% additional damage from you.
- Plate - Cellblock Bulwark [Implemented]
    Flavor: "The blue flight is breaking into a prison rather than out of one. That should worry you."
    (2) Set: Enemies within 8 yards are slowed by 60%.
    (4) Set: Enemies you block or parry are stunned for 2 sec. (Can only occur once every 20 sec.)

Gundrak - Levels: 74-80
- Cloth - Drakkari Ritebreaker [Implemented]
    Flavor: "The Drakkari are butchering their own gods for strength to fight the Scourge. It is working."
    (2) Set: Your spells deal 25% additional damage to enemies already afflicted by one of your effects.
    (4) Set: Enemies that die near you rupture, dealing damage to other enemies within 8 yards equal to 10% of the slain enemy's maximum health.
- Leather - Eck's Undertow [Implemented]
    Flavor: "Eck the Ferocious lives in the water between rooms and appears on no roster."
    (2) Set: You are immune to root and snare effects.
    (4) Set: Enemies that strike you are stunned for 3 sec. (Can only occur once every 25 sec.)
- Mail - Gal'darah's Borrowed Coat [Implemented]
    Flavor: "Gal'darah wears a god's power like a borrowed coat. It does not fit and he does not care."
    (2) Set: Killing an enemy takes a portion of its strength, granting 4% attack power for 60 sec, stacking up to 6 times.
    (4) Set: Your attacks restore 2% of your maximum health when they deal damage.
- Plate - Gundrak Godeater [Implemented]
    Flavor: "Gundrak is a temple where the priests eat the gods. Everything here is a bad trade."
    (2) Set: Holy damage you take is reduced by 25%.
    (4) Set: Enemies within 8 yards deal 12% less damage to you.

Halls of Stone - Levels: 75-80
- Cloth - Tribunal's Blessing [Implemented]
    Flavor: "The Tribunal of Ages will answer any question Brann asks. Something objects to the answers."
    (2) Set: Allies within 15 yards gain 8% increased armor.
    (4) Set: You deal 15% additional damage while an ally is within 15 yards.
- Leather - Bronzebeard's Escort [Implemented]
    Flavor: "Brann Bronzebeard talks the entire way through the Halls of Stone. He is also usually right."
    (2) Set: You take 20% less damage while an ally is within 15 yards.
    (4) Set: Your first attack against each enemy deals 35% additional damage.
- Mail - Sjonnir's Crucible [Implemented]
    Flavor: "Sjonnir builds iron dwarves from raw material, and has a great deal of raw material."
    (2) Set: Shadow damage you take is reduced by 25% and you cannot be feared.
    (4) Set: You take 20% less damage from enemies you have already struck.
- Plate - Titan Record-Keeper [Implemented]
    Flavor: "The Halls of Stone hold the record of Azeroth's making. The dwarves are in it."
    (2) Set: Mechanical and Elemental enemies attacking you deal 25% less damage.
    (4) Set: While an ally is within 10 yards, your armor is increased by 20%.

Halls of Lightning - Levels: 77-80
- Cloth - Loken's Defiance [Implemented]
    Flavor: "Loken is a Titan keeper who chose a side. The Halls of Lightning are where he defends it."
    (2) Set: Nature damage you take is reduced by 25%.
    (4) Set: Taking Nature damage grants 12% casting speed for 8 sec, stacking up to 3 times.
- Leather - Ionar's Discharge [Implemented]
    Flavor: "Ionar comes apart into lightning and puts himself back together. There is no safe distance, only less bad ones."
    (2) Set: Area attacks deal 50% less damage to you.
    (4) Set: Your attacks arc to one enemy within 8 yards for 25% of the damage.
- Mail - Volkhan's Quench [Implemented]
    Flavor: "Volkhan forges iron dwarves mid-fight and does not pause to deal with you personally."
    (2) Set: Enemies within 10 yards suffer damage equal to 2% of their maximum health every 3 sec.
    (4) Set: Striking a casting enemy grants 25% attack power for 10 sec. (Can only occur once every 12 sec.)
- Plate - Bjarngrim's Vanguard [Implemented]
    Flavor: "General Bjarngrim commands a golem army that has never needed to eat or sleep."
    (2) Set: You cannot be stunned while above 40% health.
    (4) Set: Each enemy within 10 yards grants 5% armor, up to 25%.

The Culling of Stratholme - Levels: 77-80
- Cloth - Stratholme Culler [Implemented]
    Flavor: "You are here to make certain Arthas burns the city. That is the assignment, and it does not get easier."
    (2) Set: Your spells deal 20% additional damage to Humanoids and Undead.
    (4) Set: Enemies above 90% health take 40% additional damage from you.
- Leather - Bronze Vigil [Implemented]
    Flavor: "Every citizen cut down here was going to turn. The bronze insist that matters."
    (2) Set: Your attacks against enemies above 75% health deal 30% additional damage.
    (4) Set: Killing an enemy restores 10% of your maximum health.
- Mail - Plaguebreaker [Implemented]
    Flavor: "Arthas culls Stratholme street by street and the Infinite want him stopped. So did everyone else."
    (2) Set: Your attacks deal 20% additional damage to enemies afflicted by a damage over time effect.
    (4) Set: Enemies you kill spread their plague, afflicting enemies within 8 yards for 8 sec.
- Plate - Northbound Sentinel [Implemented]
    Flavor: "Mal'Ganis waits at the end of this and Arthas will follow him north. Nothing you do prevents that."
    (2) Set: You take 20% less damage from Undead.
    (4) Set: Holding one location grants 25% increased armor until you leave it.

The Oculus - Levels: 77-80
- Cloth - Coldarra Skyrider [Implemented]
    Flavor: "The Oculus is fought from the back of a drake. Nobody has ever been happy about this."
    (2) Set: Your spells have 30% reduced pushback.
    (4) Set: Your spells cost 20% less mana.
- Leather - Drakerider's Reflex [Implemented]
    Flavor: "Malygos keeps his flight in rings above Coldarra. Getting between them requires wings."
    (2) Set: Your attack speed is increased by 10% and you move 10% faster.
    (4) Set: Breaking free of a control effect grants 40% attack speed for 8 sec.
- Mail - Eregos's Watch [Implemented]
    Flavor: "Ley-Guardian Eregos waits at the top, and the only way up is to fly."
    (2) Set: Dragonkin attacking you deal 30% less damage.
    (4) Set: Your attacks against Dragonkin deal 25% additional damage.
- Plate - Skyfall Warden [Implemented]
    Flavor: "Plate does not help on a drake. Very little does."
    (2) Set: You take 25% less damage from area attacks.
    (4) Set: Surviving a hit dealing more than 25% of your maximum health grants 30% increased armor for 12 sec.

Utgarde Pinnacle - Levels: 77-80
- Cloth - Svala's Altar [Implemented]
    Flavor: "Svala Sorrowgrave gave herself to the Scourge on the altar upstairs. She considers it a promotion."
    (2) Set: Your spells deal 20% additional damage to summoned enemies.
    (4) Set: Killing a summoned enemy grants 25% spell power for 15 sec.
- Leather - Skadi's Ascent [Implemented]
    Flavor: "Skadi rides a proto-drake along the ramparts. You are meant to shoot it down."
    (2) Set: You cannot be stunned while above 50% health.
    (4) Set: Breaking free of a stun grants 40% critical strike chance for 6 sec.
- Mail - Ymiron's Roll Call [Implemented]
    Flavor: "King Ymiron remembers every vrykul who ever died, and will list them."
    (2) Set: Casting enemies you strike are silenced for 4 sec. (Can only occur once every 25 sec.)
    (4) Set: Killing a summoned enemy reduces damage you take by 10% for 15 sec, stacking up to 4 times.
- Plate - Pinnacle Thronewarden [Implemented]
    Flavor: "The Pinnacle is the top of Utgarde and the vrykul king is still on his throne."
    (2) Set: You take 25% less damage from Undead.
    (4) Set: Killing a summoned enemy grants 8% maximum health for 30 sec, stacking up to 3 times.

Coren Direbrew - Levels: 78-82
- Cloth - Grim Guzzler Reveler [Implemented]
    Flavor: "Coren has taken issue with the Brewfest competition. The issue is being settled in the Grim Guzzler."
    (2) Set: Your spell power is increased by 10%.
    (4) Set: Killing an enemy restores 10% of your maximum mana.
- Leather - Brewfest Brawler [Implemented]
    Flavor: "Brewfest ends in a bar fight with a Dark Iron every single year. It is practically tradition."
    (2) Set: You are immune to snare effects.
    (4) Set: While two or more enemies are within 5 yards, you gain 20% dodge chance.
- Mail - Mole Machine Wrangler [Implemented]
    Flavor: "Coren brings mole machines to a bar brawl. The Dark Iron have never fought fair."
    (2) Set: Your attacks deal 15% additional damage to Mechanical enemies.
    (4) Set: Your attacks stun the target for 2 sec. (Can only occur once every 20 sec.)
- Plate - Blackrock Bouncer [Implemented]
    Flavor: "The dispute is about beer. The armor is because it is Blackrock Depths."
    (2) Set: Mechanical enemies attacking you deal 30% less damage.
    (4) Set: Being struck grants 15% increased damage for 10 sec, stacking up to 3 times.

The Crown Chemical Co. - Levels: 78-82
- Cloth - Crown Chemical Apothecary [Implemented]
    Flavor: "The Crown Chemical Company sells perfume, and something considerably less romantic."
    (2) Set: Nature damage you take is reduced by 60%.
    (4) Set: Allies within 15 yards gain 8% increased armor.
- Leather - Perfumed Tracker [Implemented]
    Flavor: "Apothecary Hummel's product is a poison with a pleasant label. Read the label anyway."
    (2) Set: Your first attack against each enemy marks it, causing it to take 20% additional damage for 30 sec.
    (4) Set: Your attacks against enemies afflicted by one of your effects deal 20% additional damage.
- Mail - Heartbreaker's Guard [Implemented]
    Flavor: "Love is in the air, and so is whatever the Crown Chemical Company has been mixing."
    (2) Set: You are immune to charm and infatuation effects.
    (4) Set: Enemies that cast at you take 30% additional damage for 10 sec.
- Plate - Gasmask Sentinel [Implemented]
    Flavor: "The plot is a mass poisoning. The venue is a holiday. Someone thought this through."
    (2) Set: Nature damage you take is reduced by 50%.
    (4) Set: Taking Nature damage grants 20% increased armor and 10% attack power for 10 sec.

The Frost Lord Ahune - Levels: 78-82
- Cloth - Midsummer Firebrand [Implemented]
    Flavor: "Ahune is summoned in the middle of a fire festival, which is rather the point."
    (2) Set: Your Fire spells deal 25% additional damage.
    (4) Set: Your Fire spells reduce the target's armor by 20% for 10 sec.
- Leather - Ahune's Thaw [Implemented]
    Flavor: "The Frost Lord surfaces, is beaten down, and sinks again. Every summer, on schedule."
    (2) Set: You cannot be frozen and take 30% less Frost damage.
    (4) Set: Taking Frost damage grants 20% attack speed for 6 sec.
- Mail - Cenarion Frostwarden [Implemented]
    Flavor: "Ahune comes up out of the water in Coilfang once a year. The Cenarion Expedition sends word."
    (2) Set: Your attacks shatter an Elemental's form, reducing its armor by 20% for 10 sec.
    (4) Set: Killing an Elemental reduces Frost damage you take by 50% for 10 sec.
- Plate - Frost-Lord's Ward [Implemented]
    Flavor: "A frost lord at a fire festival. The Midsummer organizers consider this excellent programming."
    (2) Set: You are immune to snare effects and take 25% less Frost damage.
    (4) Set: Taking Frost damage grants 15% increased damage for 8 sec.

The Headless Horseman - Levels: 78-82
    Note: Not implementable as written. The module keys a source off the LFG
    dungeon id, and the Horseman's encounter shares map 189 with the four
    Scarlet Monastery wings, so the generator's one-source-per-map filter
    excludes it -- there is no set for these four names to attach to. Giving it
    one would mean either a second source on a map that already has four, or
    special-casing the filter. Left unauthored pending that call; the four names
    and bonuses below are preserved as written.
- Cloth - Hallow's End Dismantler
    Flavor: "The Horseman laughs through the entire fight. It is worse than the fire."
    (2) Set: Your spells deal 25% additional damage to enemies that have separated into parts.
    (4) Set: Destroying a separated part deals damage equal to 10% of the enemy's maximum health.
- Leather - Hallow's Emberdancer
    Flavor: "Take his head and he will ask for it back. Politely, and at volume."
    (2) Set: Fire on the ground and burning hazards deal no damage to you.
    (4) Set: Moving through fire grants 25% movement speed and 15% critical strike chance for 6 sec.
- Mail - Monastery Flamequencher
    Flavor: "Hallow's End brings him back to the Monastery every year. Nobody has made it stick."
    (2) Set: Your attacks extinguish flames on the target, removing one Fire effect.
    (4) Set: Extinguishing a flame grants 20% attack power for 10 sec.
- Plate - Horseman's Rival
    Flavor: "He throws his own head at you. There is no elegant counter to this."
    (2) Set: You cannot be knocked from a mount, and mounted enemies deal 20% less damage to you.
    (4) Set: Enemies that taunt or laugh at you take 25% additional damage for 10 sec.

Halls of Reflection - Levels: 80-80
- Cloth - Jaina's Vigil [Implemented]
    Flavor: "Frostmourne is in that room, and Jaina still believes there is something left of him."
    (2) Set: While moving, your spell damage is increased by 25%.
    (4) Set: Your spells have 30% reduced pushback.
- Leather - Falric's Shadow [Implemented]
    Flavor: "Falric and Marwyn were Arthas's captains. They are still following orders."
    (2) Set: You move 25% faster while below 50% health.
    (4) Set: While moving, you take 30% less damage.
- Mail - Marwyn's Pursuit [Implemented]
    Flavor: "The Halls of Reflection end with the Lich King walking after you. You do not fight him. You run."
    (2) Set: You are immune to snare and root effects.
    (4) Set: Your attacks slow the target by 30% for 5 sec.
- Plate - Icewake Rearguard [Implemented]
    Flavor: "Nothing you wear matters in the last hall. Keep moving."
    (2) Set: Melee attacks against you have a 10% reduced chance to critically strike.
    (4) Set: While below 50% health, you and allies within 10 yards move 20% faster.

Pit of Saron - Levels: 80-80
- Cloth - Saronite Delver [Implemented]
    Flavor: "The Pit mines saronite with slave labor. Saronite is an Old God's blood, and it talks."
    (2) Set: Shadow damage you take is reduced by 25%.
    (4) Set: Your spells deal 20% additional damage to enemies afflicted by one of your effects.
- Leather - Pit Vein-Runner [Implemented]
    Flavor: "Scourgelord Tyrannus does not need the ore. He needs the labor broken."
    (2) Set: Mining skill increased by 15, and mining yields one additional ore.
    (4) Set: Mining a vein grants 20% movement speed for 10 sec.
- Mail - Slave Chain Breaker [Implemented]
    Flavor: "Every ton of saronite out of this pit becomes Scourge plate. Yours would fit right in."
    (2) Set: Breaking free of a control effect restores 12% of your maximum health.
    (4) Set: Killing an enemy grants 20% attack power for 20 sec.
- Plate - Rimefang's Wake [Implemented]
    Flavor: "Rimefang circles overhead while Tyrannus talks. Neither of them is bluffing."
    (2) Set: You cannot be charmed or feared.
    (4) Set: Enemies that strike you suffer damage equal to 4% of your armor.

The Forge of Souls - Levels: 80-80
- Cloth - Icecrown Soulforger [Implemented]
    Flavor: "The Forge makes val'kyr and worse out of whatever Icecrown collects."
    (2) Set: Your spells deal 25% additional damage to Undead.
    (4) Set: Killing an enemy restores 4% of your maximum mana.
- Leather - Bronjahm's Contract [Implemented]
    Flavor: "Bronjahm calls himself the Godfather of Souls and has the manner to match."
    (2) Set: Your attacks sever a fragment of the target's spirit, reducing its damage by 6% for 12 sec, stacking up to 4 times.
    (4) Set: Your attacks against enemies afflicted by one of your effects deal 25% additional damage.
- Mail - Devourer's Mask [Implemented]
    Flavor: "The Devourer of Souls wears three faces and none of them were its own."
    (2) Set: Each enemy within 10 yards grants 8% increased damage, up to 24%.
    (4) Set: Striking a casting enemy grants 25% attack power for 10 sec. (Can only occur once every 12 sec.)
- Plate - Forge-Tempered Soul [Implemented]
    Flavor: "Everything the Scourge takes passes through this forge first. Including the armor."
    (2) Set: You cannot be charmed, and Shadow damage you take is reduced by 20%.
    (4) Set: Taking Shadow damage grants 10% increased armor for 20 sec, stacking up to 3 times.

Trial of the Champion - Levels: 80-80
- Cloth - Paletress's Nightmare [Implemented]
    Flavor: "The Argent Tournament opens with a joust, which nobody in a robe has ever enjoyed."
    (2) Set: Your spells deal 25% additional damage to summoned enemies.
    (4) Set: Killing a summoned enemy restores 20% of your maximum mana.
- Leather - Lanceproof Duelist [Implemented]
    Flavor: "Confessor Paletress finds your worst memory and lets it fight for her."
    (2) Set: You take 30% less damage from area attacks.
    (4) Set: Dodging an attack grants 35% attack power for 10 sec. (Can only occur once every 20 sec.)
- Mail - Argent Joust-Rider [Implemented]
    Flavor: "The Argent Crusade tests everyone the same way before Icecrown. Mount up."
    (2) Set: Your attacks deal 30% additional damage to enemies that have not engaged you.
    (4) Set: Killing an enemy grants 25% critical strike chance for 12 sec.
- Plate - Black Knight's Match [Implemented]
    Flavor: "The Black Knight enters the tournament, loses, and comes back anyway. Twice."
    (2) Set: You cannot be disarmed, and cannot be stunned while above 50% health.
    (4) Set: Killing an enemy grants 20% damage reduction for 20 sec.


Raids
--------------------
Four thresholds per set rather than two: 2, 4, 6 and 8. The extra two are the
reason the sets were widened to eight slots and nothing has used the extra room
yet. ItemSet.dbc has eight spell slots (fields 35-42) and eight threshold slots
(43-50), and mod_source_item_set_program keys on (set_id, threshold), so 6 and 8
need no schema change -- only the generator, which currently hard-codes two.

Coverage rule. An armor family is worn by a fixed set of classes, and every one
of their specs has to care about every set. Cloth is Mage, Priest and Warlock;
leather is Rogue and Druid; mail is Hunter and Shaman; plate is Warrior, Paladin
and Death Knight. That means a cloth set cannot key everything to one school, a
leather set cannot assume melee, a mail set cannot assume a pet, and a plate set
cannot ignore healing done.

No threshold is reserved for a flat stat package. A bonus may branch according
to whether its trigger damaged an enemy, healed an ally, or prevented damage,
but every branch must express the same raid mechanic and carry comparable
weight. The four thresholds instead serve these purposes:

    (2)  Identity. Introduces the set's loop through an action every wearer can
        perform, such as spending resources, critically striking, moving, or
        taking a meaningful hit.
    (4)  Encounter. Recreates a recognizable mechanic from the raid, with a
        condition every spec can deliberately meet.
    (6)  Transformation. Changes how the earlier loop plays or adds a second
        decision; never just three flat percentages joined by commas.
    (8)  Capstone. Large, unmistakably tied to the raid, and useful whether its
        wearer is dealing damage, healing, or surviving pressure.

Magnitudes step with the band: level 60 raids use 8 / 12 / 15 / 25 percent as
their tuning anchors, level 70 raids use 10 / 15 / 18 / 30, and level 80 raids
use 12 / 18 / 20 / 35. They are budgets rather than mandatory wording; a proc,
shield, echo, resource refund, or positional effect may spend the same budget
without restating it as a passive stat increase.

Molten Core - Levels: 60-60
- Cloth - Sulfuron Emberweave [Implemented]
    Flavor: "Nothing in the Core is woven. This was made somewhere sane and carried down."
    (2) Set: Your spell criticals ignite the target, dealing Fire damage over 6 sec equal to half the critical strike. A critical heal instead shields its target for the same amount.
    (4) Set: When one of your damage over time effects lands the killing blow, it erupts, dealing Fire damage to all enemies within 8 yards. When one of your healing over time effects would overheal, the excess instead shields its target.
    (6) Set: Each tick of your ignites and each hit absorbed by your ash shields stores an Ember, up to five. Your next spell consumes the Embers to repeat 3% of its effect per Ember against nearby enemies or allies.
    (8) Set: Every 45 sec, your next critical spell opens a Sulfuron vent beneath its target for 10 sec. Ignites erupt inside it and ash shields flow through it, dealing damage to enemies and shielding allies each second for up to 25% of the triggering spell.
- Leather - Corehound Skinner [Implemented]
    Flavor: "Two heads, one hide, and a tanner at Thorium Point who has learned not to ask."
    (2) Set: While stealthed or shapeshifted, you regenerate health steadily; breaking stealth or shifting to attack does not interrupt this regeneration for 4 sec.
    (4) Set: Killing an enemy that is burning or bleeding causes it to erupt, dealing Fire damage to all enemies within 8 yards and hastening your attack and movement speed for 8 sec.
    (6) Set: While your regeneration is active, every third damaging or healing action bites twice. The second bite repeats 15% of the action and extends the regeneration by 2 sec, up to 8 sec.
    (8) Set: Every 60 sec, an eruption or critical heal unleashes both heads for 15 sec. One repeats 25% of your damaging actions against a nearby enemy; the other repeats 25% of your healing and absorption on a nearby ally.
- Mail - Firelord's Vigil [Implemented]
    Flavor: "Dwarves dug down here looking for a forge. They found one, and it was awake."
    (2) Set: Your pet, or a totem you control, radiates heat every 3 sec, dealing Fire damage to all nearby enemies.
    (4) Set: Every 45 sec, you become wreathed in flame for 6 sec: you cannot be slowed or frozen, enemies that strike you in melee are burned, and your pet or totems deal 25% additional damage for the duration.
    (6) Set: Each heat pulse also shields the most injured nearby ally for 3% of your maximum health. Damaging an enemy or shielding an ally stores one degree of Heat, and at five degrees your next action is repeated at 15% strength by your pet or totem.
    (8) Set: Every 60 sec, your pet or most recently summoned totem becomes the Firelord's vessel for 12 sec. It pulses each second, damaging enemies and shielding allies for 5% of your maximum health, and mirrors 25% of your actions from its position.
- Plate - Ragnaros's Contempt [Implemented]
    Flavor: "TOO SOON! The armor does not help with the volume."
    (2) Set: Being critically struck ignites you: you erupt, dealing Fire damage to all enemies within 5 yards.
    (4) Set: The first hit that would drop you below 15% health is instead fully absorbed, and you erupt from within as the Firelord once did, dealing Fire damage to all enemies within 10 yards equal to 25% of your maximum health. (Can only occur once every 5 min.)
    (6) Set: Blocking, parrying, or critically damaging or healing causes a lesser eruption. (Can only occur once every 8 sec.) Each eruption leaves a magma pool for 8 sec; enemies inside take Fire damage and allies inside gain a shield equal to 3% of your maximum health every 2 sec.
    (8) Set: Every 60 sec, your next damaging or healing action hurls Sulfuras at its target. The hammer travels through nearby enemies and allies, damaging or shielding each for 25% of your maximum health before returning to you.

Onyxia's Lair - Levels: 60-60
- Cloth - Brood Ashweaver
    Flavor: "The lair is warm the way an oven is warm. The weave is treated. You are not."
    (2) Set: Your critical damage scorches the target for 6 sec, causing your next spell against it to deal 8% additional Fire damage. Your critical healing instead coats its target in ash, absorbing damage equal to 8% of the heal.
    (4) Set: When a single hit deals more than 20% of your maximum health, your next spell within 6 sec is instant, costs no mana, and is 20% stronger. (Can only occur once every 20 sec.)
    (6) Set: After moving at least 8 yards, your next spell within 6 sec may be cast while moving and grants 15% movement speed for its cast. (Can only occur once every 12 sec.)
    (8) Set: Every 20 sec, your next spell becomes a breath: a harmful spell repeats at 50% strength against up to three enemies in front of you, while a beneficial spell repeats at 50% strength on up to three allies in front of you.
- Leather - Whelp Culler
    Flavor: "The whelps come in waves and nobody counts them afterward."
    (2) Set: Each enemy beyond the first within 10 yards increases your resource regeneration by 4%, up to 16%. Changing targets preserves this bonus for 4 sec.
    (4) Set: Killing an enemy while another is nearby grants 8% attack speed, spell haste, and movement speed for 8 sec, stacking up to 3 times.
    (6) Set: Dodging an attack or critically damaging or healing sheds a black scale for 8 sec. The scale reduces the next direct hit against you by 15% and, when broken, restores 5% of your maximum resource. (Can only occur once every 8 sec.)
    (8) Set: Every 20 sec, your next damaging or healing action marks its target as Brood's Prey for 8 sec. Your actions against a marked enemy splash 50% of their damage to another nearby enemy; your actions on a marked ally echo 50% of their healing or absorption to another nearby ally.
- Mail - Onyxian Scalecutter
    Flavor: "Black dragon scale turns a blade once. The trick is being the second blade."
    (2) Set: Every fifth attack, spell, or heal cracks a scale. Your next action is 20% stronger and restores 4% of your maximum resource.
    (4) Set: A critical damaging action tears free a whelp that savages the target for 8 sec; a critical heal instead sends it to guard the ally with a shield equal to 12% of the heal. (Can only occur once every 10 sec.)
    (6) Set: Your pet or most recently summoned totem becomes a Broodguard, pulsing every 3 sec to damage nearby enemies and shield nearby allies for 3% of your maximum health.
    (8) Set: Every 20 sec, your next attack, spell, or heal is guaranteed to critically strike and is repeated at 50% strength by your Broodguard against the same target.
- Plate - Bellowing Bulwark
    Flavor: "She takes to the air, she inhales, and every plan in the room becomes the same plan."
    (2) Set: You cannot be feared. Whenever you resist or outlast a fear effect, you bellow, granting allies within 10 yards 8% increased damage and healing for 8 sec.
    (4) Set: Damage exceeding 25% of your maximum health from a single hit is reduced by 40%, and the prevented damage empowers your next damaging or healing action.
    (6) Set: The last enemy you damaged or ally you healed becomes Guarded for 10 sec. You intercept 15% of damage dealt to a Guarded ally; damage dealt by a Guarded enemy to anyone else grants you a shield for the same amount.
    (8) Set: Once every 2 min upon entering combat, you loose a bellow that shakes the room: enemies within 20 yards are disoriented for 3 sec and deal 25% less damage for 15 sec, while allies within 20 yards become immune to fear for the same duration.

Blackwing Lair - Levels: 60-60
- Cloth - Nefarian's Experiment
    Flavor: "Nefarian bred the chromatic flight out of spare parts and kept notes. Some of them are on this robe."
    (2) Set: Casting a spell records its school for 12 sec. Casting from a different school makes the new spell 8% stronger and restores 2% of your maximum mana.
    (4) Set: Every 20 sec, your next spell mutates, dealing or healing 60% more and leaving Chromatic Residue that makes your next spell from a different school instant.
    (6) Set: Using three different spell schools within 12 sec grants Chromatic Insight: your next three spells each echo at 30% strength as a different school, or as an absorption shield when beneficial.
    (8) Set: Recording four different spell schools unleashes Nefarian's experiment, breathing each school in turn at targets in front of you; enemies take damage and allies receive healing equal to 25% of your maximum health over 8 sec.
- Leather - Chromaggus Hidestripper
    Flavor: "Chromaggus carries five breaths and a disease nobody has survived naming twice."
    (2) Set: You are immune to disease effects. Cleansing, resisting, or outlasting a harmful effect adapts your hide, reducing damage from its school by 8% for 12 sec.
    (4) Set: Each different school of damage you suffer within 12 sec grants 6% damage reduction, up to five schools. Avoiding an attack counts as Physical.
    (6) Set: When your adapted hide prevents damage, your next damaging or healing action within 8 sec gains 15% of the prevented amount and refreshes that adaptation.
    (8) Set: Every 45 sec, the next harmful effect applied to you is shed and reflected. For 10 sec afterward, each different damage school you deal, heal through, or resist adds 5% to your damage, healing, and avoidance, up to 25%.
- Mail - Razorgore's Leash
    Flavor: "Razorgore does as the orcs tell him until somebody breaks the orb. Then he does as he likes."
    (2) Set: You cannot be charmed. Every fifth attack, spell, or heal issues a command through the leash, causing your pet or most recently summoned totem to repeat 30% of the action's effect.
    (4) Set: Breaking free of a stun, root, or fear snaps the leash for 10 sec, removing the resource cost of your next three actions and making your pet or totems immune to control effects.
    (6) Set: While you are controlled or afflicted by harmful magic, your pet or totems become Unbound: they pulse damage at enemies and shields on allies every 3 sec, and each pulse restores 3% of your maximum resource.
    (8) Set: Every 45 sec in combat, the orb breaks for 12 sec. Your pet or totems grow to Razorgore's scale, taunt nearby enemies, and mirror 50% of your damage and healing while you cannot be interrupted.
- Plate - Broodlord's Bulwark
    Flavor: "Broodlord Lashlayer stands at the bottom of the stairs and has never let a first attempt past."
    (2) Set: Blocking, parrying, or enduring three direct hits within 6 sec readies a Lash. Your next damaging action sweeps a second enemy, while your next heal also shields its target for 8% of your armor.
    (4) Set: Enemies that strike you in melee are lashed with flame for damage equal to 8% of your armor. Their next attack against anyone else deals 12% less damage.
    (6) Set: Each enemy beyond the first within 10 yards adds a charge to your bulwark, up to five. Damaging or healing consumes the charges to splash 3% of the action per charge to nearby enemies or allies.
    (8) Set: Holding position for 5 sec plants a Blackwing standard until you move. It taunts lesser enemies and pulses every 2 sec, damaging enemies and shielding allies within 10 yards for 5% of your maximum health.

Zul'Gurub - Levels: 60-60
- Cloth - Hakkari Bloodweaver
    Flavor: "The Hakkari bled the Soulflayer into this cloth. It has never quite dried."
    (2) Set: Every fifth tick of your periodic damage or healing draws Blood. Your next direct spell consumes it to restore 4% of your maximum mana and repeat the triggering tick.
    (4) Set: When one of your periodic effects expires, its final tick spreads at 50% strength to up to two nearby enemies or allies.
    (6) Set: Drawing Blood three times within 15 sec causes your next spell to weave a blood ward around its target, repeating 15% of its damage as healing or 15% of its healing as absorption.
    (8) Set: Your spells fill a Blood Chalice with 10% of their damage, healing, and absorption. Every 20 sec the chalice spills, dividing its contents between damage to nearby enemies and healing to nearby allies.
- Leather - Mandokir's Quarry
    Flavor: "Bloodlord Mandokir names the next person to die and is usually right."
    (2) Set: Your first damaging or healing action marks its target as the Quarry for 15 sec. Actions on the Quarry restore 1% of your maximum resource, increasing by 1% with each consecutive action.
    (4) Set: Each consecutive action on the Quarry gains 6% effect, up to 30%. Changing targets transfers the mark but resets the bonus.
    (6) Set: When an enemy Quarry attacks someone else, or an allied Quarry falls below 50% health, you gain 30% movement speed and your next action on it is guaranteed to critically strike.
    (8) Set: Killing an enemy Quarry or restoring an allied Quarry from below 20% to above 80% health grants Mandokir's Triumph for 10 sec: full resource regeneration and 25% haste, dodge, and critical effect.
- Mail - Jin'do's Shackle
    Flavor: "Jin'do binds Hakkar and every hexxer in the temple to one thread. Pull it and they all move."
    (2) Set: Your direct damage or healing shackles its target to your pet or nearest totem for 8 sec. The shackle repeats 10% of your actions as damage to a bound enemy or healing to a bound ally.
    (4) Set: Every 20 sec, your next action hexes an enemy to deal 30% less damage or wards an ally to take 30% less damage for 6 sec.
    (6) Set: When a shackled target takes a critical hit or heal, the thread snaps across up to three nearby targets for 15% of that effect and restores 3% of your maximum resource per target reached.
    (8) Set: Entering combat raises Jin'do's web for 20 sec. Allies, pets, and totems within 20 yards are linked; 25% of each member's damage and healing is echoed by the next member to act.
- Plate - Soulflayer's Due
    Flavor: "Hakkar takes blood as payment. The armor is a way of arguing about the amount."
    (2) Set: Damaging, healing, blocking, or parrying adds 1% of the amount to your Blood Debt, up to 8% of your maximum health. At its cap the debt is paid as healing to you and the most injured nearby ally.
    (4) Set: While below 50% health, Blood Debt fills twice as fast and healing you cause or receive first adds an absorption shield equal to 20% of the heal.
    (6) Set: Paying your Blood Debt coats your armor for 15 sec. Each direct hit removes one layer to empower your next damaging or healing action by the amount prevented.
    (8) Set: Falling below 40% health calls the Soulflayer's due, draining enemies within 10 yards for 10% of their maximum health and dividing the total as healing and shields among nearby allies. (Can only occur once every 90 sec.)

Ruins of Ahn'Qiraj - Levels: 60-60
- Cloth - Qiraji Chitinweave
    Flavor: "The silithid do not weave. Whatever this is came off something's back."
    (2) Set: Direct spells grow a layer of chitin on their target for 8 sec. On an enemy, the layer cracks for 8% additional damage from your next spell; on an ally, it absorbs damage equal to 8% of the heal.
    (4) Set: Killing an enemy or healing an ally below 20% health leaves a cocoon for 10 sec. Touching it restores 15% of your maximum mana and coats you in a shield for 15% of your maximum health.
    (6) Set: Breaking three layers of chitin within 12 sec releases a swarm that repeats 15% of your spells against enemies and allies near their targets for 8 sec.
    (8) Set: Every 25 sec, your next spell hatches every layer of chitin within 10 yards, damaging enemies and healing allies for 50% of the spell's effect per layer consumed.
- Leather - Ossirian's Crystal
    Flavor: "Ossirian the Unscarred earned the name honestly, right up until the crystals."
    (2) Set: Critical damage, healing, or dodges create an Ossirian crystal that orbits you for 12 sec, up to three. Each crystal grants 2% critical strike and dodge chance.
    (4) Set: Every 15 sec, your next action shatters an orbiting crystal: damaging an enemy strips 20% of its armor, healing an ally shields it, and avoiding an attack blinds the attacker for 4 sec.
    (6) Set: Shattering a crystal amplifies your next critical effect by 15% and causes it to create two crystals instead of one.
    (8) Set: Reaching three crystals makes you Unscarred for 10 sec. Your critical actions erupt through all three, repeating 25% of their effect on three nearby enemies or allies before the crystals reform.
- Mail - Kurinnaxx Sandcutter
    Flavor: "The sand moves before Kurinnaxx does. That is the only warning anyone gets."
    (2) Set: You take 25% less damage from area effects.
    (4) Set: Your actions against movement-impaired targets gain 30% effect: enemies take additional damage, while allies are healed and freed from one snare or root.
    (6) Set: Moving 10 yards stirs a sand cloud around your pet or nearest totem for 8 sec. Enemies inside have 15% reduced chance to hit; allies inside take 15% less area damage.
    (8) Set: Every 20 sec, your next damaging or healing action sinks you and its target into the sand for 4 sec. Both take 50% less area damage, and your actions emerge at 25% increased effect.
- Plate - Swarmguard Carapace
    Flavor: "Layered like the things it was taken from, and about as pleasant to wear."
    (2) Set: Your armor is increased by 5% for each enemy within 10 yards, up to 25%.
    (4) Set: At four nearby enemies, your carapace opens and releases scarabs. Each scarab intercepts one hit against you or a nearby ally, then bites the attacker for 5% of your armor.
    (6) Set: Blocking, parrying, or being healed consumes one carapace layer to hatch a scarab that repeats 15% of your next damaging or healing action on a nearby target.
    (8) Set: For each enemy within 10 yards, one scarab joins your swarm, up to five. Every 3 sec each scarab either bites an enemy or shields the most injured ally for 5% of your maximum health.

Ahn'Qiraj Temple - Levels: 60-60
- Cloth - Whisper of the Old God
    Flavor: "C'Thun speaks to everyone in the temple. Most of them answer."
    (2) Set: Every third spell invites a Whisper for 8 sec. Accepting it makes your next spell 25% stronger but costs 8% of your maximum health; letting it expire restores 8% of your maximum mana.
    (4) Set: Critical spells open an eye on their target for 8 sec. An enemy eye reduces damage dealt by 20%; an allied eye watches for the next hit and shields it.
    (6) Set: Accepting two Whispers within 20 sec opens an eye above you that repeats 15% of your spells at nearby enemies or allies and returns the health paid as healing over 10 sec.
    (8) Set: Every 30 sec, the Old God answers. Your next spell is cast twice, the second at 50% effect and free; if a target bears an eye, the echo spreads to every other open eye.
- Leather - Vekniss Hivestalker
    Flavor: "The Vekniss dug these tunnels, and the tunnels were not dug for you."
    (2) Set: You gain 8% dodge chance while three or more enemies are within 10 yards.
    (4) Set: Dodging an attack or critically damaging or healing lets you burrow a short distance toward your target, leaving a tunnel that grants allies 20% movement speed for 8 sec.
    (6) Set: Each 10 yards traveled through your tunnels stores a Vekniss Ambush, up to three. Your next action consumes one to strike or heal from beneath the target for 15% additional effect.
    (8) Set: Every 30 sec, you burrow for 3 sec and become immune to damage. Emerging collapses every tunnel, damaging enemies and shielding allies along them for 25% of your maximum health.
- Mail - Twin Emperors' Regard
    Flavor: "Vek'lor and Vek'nilash share everything, including the damage."
    (2) Set: Your first action in combat appoints the nearest ally, pet, or totem as your Twin. Every fifth action is echoed from the Twin's position at 40% strength.
    (4) Set: While within 15 yards of your Twin, both of you take 12% less damage. Crossing beyond that range pulls the more injured of you 5 yards toward the other. (Can only occur once every 15 sec.)
    (6) Set: Critical actions swap Vek'lor's Regard and Vek'nilash's Regard between you and your Twin: one grants 15% haste, the other converts 15% of damage taken into healing.
    (8) Set: Every 60 sec, the Twin Emperors manifest for 12 sec. Harmful actions are repeated by one Twin and beneficial actions by the other, each at 50% strength from opposite sides of the target.
- Plate - Skeram's Certainty
    Flavor: "The Prophet Skeram announces your death several times before attempting it."
    (2) Set: You cannot be silenced, and take 8% less damage from spells.
    (4) Set: Fatal damage instead leaves you at 25% health and immune to damage for 4 sec. (Can only occur once every 8 min.)
    (6) Set: Taking a spell hit, blocking, or critically healing creates an illusion for 8 sec, up to three. Each illusion absorbs one direct hit and repeats your next damaging or healing action at 15% strength.
    (8) Set: Every 60 sec, Skeram announces one of three certainties for 12 sec: your illusions either duplicate 25% of your damage, duplicate 25% of your healing, or redirect 25% of damage taken. The certainty follows your first action.

Karazhan - Levels: 70-70
- Cloth - Medivh's Marginalia
    Flavor: "The Guardian annotated everything. Half the tower's library is arguing with itself."
    (2) Set: Casting two different spells on the same target adds a Marginal Note for 12 sec. Your next new spell on that target consumes the note for 20% additional effect and restores 3% of your maximum mana.
    (4) Set: Every 20 sec, consuming a Marginal Note opens the annotated page, repeating 60% of that spell against all valid targets within 10 yards.
    (6) Set: Adding notes with three different spells writes a Contradiction. Your next spell resolves it by casting a free 30% echo of each spell that wrote it.
    (8) Set: A critical spell edits the tower's script: it reduces the cooldown of the last different spell you cast by 2 sec and adds it to the margin. At four edits, the entire margin is recast at 25% strength.
- Leather - Opera House Understudy
    Flavor: "The tower stages a different play every week and has never once asked for volunteers."
    (2) Set: Your first action in combat casts you as Hero, Healer, or Villain according to whether you damaged, healed, or avoided an attack. Repeating your role three times grants 10% haste for 8 sec.
    (4) Set: Killing an enemy, healing an ally below 25% health, or dodging a heavy hit advances the scene and grants a stack of Applause: 8% movement speed and critical effect for 12 sec, up to three stacks.
    (6) Set: At three stacks of Applause, an Understudy appears for 10 sec and repeats 30% of your actions. Changing roles directs the Understudy to taunt your target, shield your ally, or strike your enemy.
    (8) Set: Entering combat raises the curtain for 20 sec. Every fourth action changes the play, cycling through 30% increased effect, 30% damage reduction, and no resource costs; the final scene grants all three for 6 sec.
- Mail - Ivory Gambit
    Flavor: "Medivh's chess set plays itself, and does not much care which side you took."
    (2) Set: Your first action against each target places a Pawn. Pawns take or receive 20% more from your next action, then advance to the far side of the target.
    (4) Set: Killing an enemy Pawn or critically healing an allied Pawn promotes it for 10 sec, granting you 25% critical strike chance and causing your pet or totems to guard its square.
    (6) Set: Every sixth action moves as a chess piece: a Knight action leaps to a second target, a Bishop action chains along a line, and a Rook action shields targets between you and the first. The move cycles in that order.
    (8) Set: Every 30 sec, your next action calls Check. Enemy Pawns are pinned for 4 sec, allied Pawns take 30% less damage, and you may instantly move behind any Pawn with 30% increased effect for 8 sec.
- Plate - Prince's Debt
    Flavor: "Malchezaar rules a tower he does not own, and drops infernals on it to make the point."
    (2) Set: You take 20% less damage from Demons and cannot be feared by them. Damage prevented this way is added to the Prince's Debt, up to 20% of your maximum health.
    (4) Set: At three nearby enemies, the debt begins charging interest: your actions add 15% of their damage, healing, or blocking to it, and one enemy is branded as the Collector.
    (6) Set: When the debt reaches its cap, an infernal fragment crashes onto the Collector, damaging nearby enemies and shielding nearby allies for the stored amount before the debt begins again.
    (8) Set: Every 90 sec, a full infernal falls at your position for 20 sec. It taunts nearby enemies, pays 30% of damage taken on your behalf, and repeats your damaging and healing actions at 30% strength until destroyed.

Gruul's Lair - Levels: 70-70
- Cloth - Gronn-Bane Weave
    Flavor: "Gruul the Dragonkiller has seven sons and a very short temper."
    (2) Set: Spells against enemies with more maximum health than you deal 10% additional damage. Spells on allies with less health than their attacker heal for 10% more.
    (4) Set: Killing a Giant or elite, or healing an ally after a Giant or elite strikes them, drops a Gronn Tooth. Collecting it restores 20% of your maximum mana and makes your next spell uninterruptible.
    (6) Set: Standing still for 3 sec petrifies the weave, storing 6% spell effect each second up to 18%. Moving shatters it, adding the stored effect to your next spell and splashing half to nearby targets.
    (8) Set: Every 30 sec, your next spell grows with its target: it gains 10% effect for each size category above you, up to 30%, then reverberates through larger enemies and allies within 15 yards.
- Leather - Blade's Edge Skinner
    Flavor: "Blade's Edge is named for what it does to anything that falls."
    (2) Set: You take no falling damage. Falling at least 8 yards or changing elevation by 5 yards grants High Ground, adding 10% effect to your next damaging or healing action.
    (4) Set: Dodging an attack or landing from High Ground grants 30% attack speed, spell haste, and movement speed for 8 sec.
    (6) Set: Consuming High Ground leaves a blade at your landing point for 12 sec. Crossing between two blades causes your next action to strike or heal along the path for 18% of its effect.
    (8) Set: Every 25 sec, your next action leaps you to its target and lands with 60% additional effect. Enemies along the leap are cut; allies along it are shielded for the same amount.
- Mail - Maulgar's Council
    Flavor: "Maulgar brings four advisors and no plan for what happens when they die first."
    (2) Set: Your first four actions in combat appoint a rotating advisor: Seer restores 3% resource, Summoner repeats 20% through your pet or totem, Mage shields the target, and Priest heals the most injured nearby ally.
    (4) Set: Killing an enemy or critically healing an ally promotes the active advisor for 12 sec, doubling its effect. Up to three advisors may be promoted at once.
    (6) Set: When all four advisors have acted, they form a council for 10 sec. Each of your actions triggers a different advisor, and their effects can critically strike.
    (8) Set: Every 60 sec, Maulgar joins the council for 15 sec. Your pet, totems, and advisors grow, taunt one nearby enemy each, and mirror 50% of your damage, healing, and absorption.
- Plate - Cave Lord's Grip
    Flavor: "Gruul grows heavier as the fight goes on. So, eventually, does everything else."
    (2) Set: Each 10 sec in combat grants 3% increased armor, damage and healing, up to 18%.
    (4) Set: You cannot be stunned while above 60% health. A stun resisted this way immediately grants one Growth stack and causes your next action to stagger its target.
    (6) Set: At three Growth stacks, your direct actions create a Ground Slam beneath the target, damaging enemies or shielding allies within 6 yards for 18% of the action.
    (8) Set: At six Growth stacks, Shatter releases them: enemies within 15 yards are knocked back and damaged for 30% of your maximum health, allies are shielded for the same amount, and Growth begins again.

Magtheridon's Lair - Levels: 70-70
- Cloth - Hellfire Channeler
    Flavor: "Five channelers hold the Pit Lord to the floor. This is what is left when one of them stops."
    (2) Set: Finishing a cast without interruption adds a Channeler for 12 sec, up to five. Each Channeler returns 2% of the spell's mana cost and stabilizes the next cast against pushback.
    (4) Set: Every 25 sec, your next spell consumes one Channeler to cost no mana and gain 75% effect. If no Channeler is present, it instead creates two.
    (6) Set: At five Channelers, your spells draw beams to their targets for 8 sec. Enemy beams deal 18% of the spell again over time; allied beams absorb 18% of damage taken.
    (8) Set: Maintaining five Channelers for 6 sec banishes your target for 3 sec if hostile or makes it immune to damage for 3 sec if friendly, then grants you 30% spell haste for 12 sec.
- Leather - Pit Lord's Measure
    Flavor: "Magtheridon ruled Outland once. Illidan chained him to a floor and started drawing blood."
    (2) Set: Damaging, healing, or dodging draws a measure of blood into the hide, up to 10% of your maximum health. At its cap, your next action is free and spills the stored amount as additional damage or healing.
    (4) Set: Killing a Demon or critically healing an ally injured by one fills the measure and grants 20% attack speed, spell haste, and movement speed for 15 sec.
    (6) Set: Spilling the measure leaves a chain at the target for 12 sec. Chained enemies deal 18% less damage; chained allies receive 18% more healing and cannot be moved against their will.
    (8) Set: Every 45 sec, all nearby targets below 50% health are chained to you for 10 sec. Your actions gain 3% effect for each missing 10% of health among them, up to 30%, and divide that effect across the chains.
- Mail - Blood-Drained Mail
    Flavor: "Everything in this pit is being bled for something. Do not linger."
    (2) Set: You take 20% less damage from Demons. Ten percent of your damage, healing, and damage prevented is stored as Pit Blood, up to 20% of your maximum health.
    (4) Set: While below 50% health, each action drinks 10% of the Pit Blood to heal you and empower the action by the amount consumed.
    (6) Set: Your pet or most recently summoned totem drinks from the store every 3 sec, pulsing damage at enemies and healing on allies for 18% of the amount stored without consuming it.
    (8) Set: Every 20 sec, the pit is drained. All stored blood erupts from you, split evenly between damage to enemies and healing to allies within 20 yards; each target reached restores 3% of your maximum resource.
- Plate - Cube-Warden's Plate
    Flavor: "Somebody has to hold the cube. It is never the person who volunteers."
    (2) Set: You cannot be silenced or interrupted, and take 10% less Shadow damage.
    (4) Set: Taking a single hit above 20% of your maximum health activates one face of the cube, shielding you for 20% of your maximum health. (Can only occur once every 45 sec.)
    (6) Set: Damaging, healing, blocking, or parrying activates another face for 12 sec, up to five. At five faces, your next action imprisons an enemy for 3 sec or makes an ally immune to control effects for 8 sec.
    (8) Set: Every 60 sec, the sixth face opens and you hold the line for 8 sec. Allies within 20 yards take 30% less damage, you take 20% of it instead, and each redirected hit powers a retaliatory strike or group heal.

Coilfang: Serpentshrine Cavern - Levels: 70-70
- Cloth - Tidehunter's Weave
    Flavor: "Lady Vashj drained a marsh to fill this cavern and considers it an improvement."
    (2) Set: Direct spells leave a Tide Mark for 8 sec. Moving 5 yards pulls the mark into a current, causing your next spell on that target to gain 10% effect and restore 3% of your maximum mana.
    (4) Set: Pulling a Tide Mark from an enemy slows it by 25%; pulling one from an ally grants 25% movement speed. Your spells gain 25% effect on targets moving against your current.
    (6) Set: Pulling three marks within 15 sec reverses the tide for 8 sec. Enemy marks flow toward you as damage, allied marks flow outward as healing, and each one repeats 18% of the spell that created it.
    (8) Set: Every 20 sec, your next spell raises a tidal wave that travels through the target and chains to two additional enemies or allies for 50% effect, collecting and triggering every Tide Mark in its path.
- Leather - Naga Sealskin
    Flavor: "Naga hide holds water. So does everything else in Coilfang."
    (2) Set: You breathe underwater, swim 40% faster, and are immune to movement-slowing effects.
    (4) Set: Killing an enemy, critically healing an ally, or dodging an attack creates a Current for 10 sec, granting 25% movement speed and 15% dodge chance.
    (6) Set: Traveling 15 yards with a Current leaves a wake behind you. Enemies crossing it are slowed and take 18% of your last damaging action; allies crossing it are freed from snares and receive 18% of your last heal.
    (8) Set: After moving continuously for 4 sec, you become an Undertow until you stop: you cannot be interrupted, your actions gain 30% effect, and every third action repeats from the far end of your wake.
- Mail - Serpentshrine Striker
    Flavor: "The Steamvault pumps this cavern dry one shift at a time. It is not working."
    (2) Set: Damaging actions pull 30% movement speed from enemies for 5 sec; healing actions grant the stolen speed to allies. Your pet or totems share the transferred speed.
    (4) Set: Actions gain 30% effect against slowed enemies or movement-impaired allies, and the latter are freed from one snare or root.
    (6) Set: Your actions alternate High Tide and Low Tide. High Tide repeats 18% as damage from your pet or nearest totem; Low Tide repeats 18% as healing or absorption from the same position.
    (8) Set: Every 20 sec, High Tide and Low Tide collide in a surge at your position, damaging enemies and healing allies within 12 yards for 30% of your maximum health and carrying them 5 yards with the wave.
- Plate - Fathom-Guard Bulwark
    Flavor: "The Fathom-Guard drowned once already and took the promotion."
    (2) Set: You take 20% less Nature damage and are immune to poison effects.
    (4) Set: Enemies that strike you are waterlogged for 5 sec, losing 30% movement speed and taking Nature damage equal to 6% of your armor when they next move.
    (6) Set: Blocking, parrying, cleansing a poison, or receiving a critical heal fills one chamber of the bulwark, up to three. Your next action empties them for 6% effect per chamber and splashes nearby enemies or allies.
    (8) Set: At or above 75% health, High Tide makes every third action surge through nearby enemies and allies at 30% strength. Below 75%, Low Tide makes every third hit against you heal you and the most injured nearby ally for 30% of the damage.

Tempest Keep - Levels: 70-70
- Cloth - Kael'thas's Remainder
    Flavor: "Kael'thas took the Eye for his people, and then stopped mentioning them."
    (2) Set: Spell criticals tear loose a Mana Fragment that restores 5% of your maximum mana and orbits you for 12 sec, up to four.
    (4) Set: Each orbiting Mana Fragment grants 8% spell haste. Casting the same spell twice consumes one fragment; casting a different spell refreshes them all.
    (6) Set: At four fragments, a phoenix egg forms for 10 sec. Your spells feed it 18% of their damage, healing, and absorption; if it survives, it hatches and returns the stored amount around its target.
    (8) Set: Hatching an egg makes your next spell free, instant, and 60% stronger. It consumes the four fragments, then the phoenix repeats the spell at 30% strength before burning out.
- Leather - Void Reaver's Shadow
    Flavor: "The Void Reaver is a machine built out of a dead god's leftovers."
    (2) Set: You take 30% less damage from area effects.
    (4) Set: Each area attack that lands within 8 yards without hitting you adds an Arcane Charge. At three charges, your next action gains 80% effect and consumes them.
    (6) Set: Consuming Arcane Charges leaves your shadow behind for 6 sec. It repeats 18% of your actions from its position and absorbs the next area hit that would strike you.
    (8) Set: Every 30 sec, you phase into your shadow for 4 sec, becoming immune to area damage. On return, all area damage avoided erupts as damage to enemies and shields on allies around you, up to 30% of your maximum health per target.
- Mail - Al'ar's Feather
    Flavor: "Al'ar dies twice. Plan the second one before the first."
    (2) Set: Critical damage, healing, or absorption creates a Feather of Al'ar, up to five. Each feather causes your pet or nearest totem to repeat 2% of your next action.
    (4) Set: Falling below 30% health consumes the feathers, healing you for 6% of your maximum health per feather and igniting nearby enemies for the same total. (Can only occur once every 5 min.)
    (6) Set: At five feathers, your pet or nearest totem becomes a phoenix egg for 6 sec. Actions feed it 18% of their effect; hatching repeats the stored amount around the egg.
    (8) Set: On death, the egg is created immediately and may rebirth you once every 30 min at 40% health. For 20 sec, the phoenix fights beside you and repeats 30% of your damage and healing.
- Plate - Solarian's Sanction
    Flavor: "High Astromancer Solarian calls the stars down and does not check who is standing where."
    (2) Set: You take 20% less Arcane damage and cannot be critically struck by spells.
    (4) Set: Taking Arcane damage, blocking, or critically healing calls down a star that orbits you for 8 sec, up to three. Each star absorbs one spell hit and then falls on the caster.
    (6) Set: Damaging or healing launches one orbiting star at the target for 18% of the action. On an enemy it explodes; on an ally it becomes a shield and reflects the next spell hit.
    (8) Set: Every 45 sec, three stars fall around you. Each chooses the most dangerous enemy and most injured ally within 20 yards, damaging one and healing the other for 15% of your maximum health.

The Battle for Mount Hyjal - Levels: 70-70
- Cloth - Archimonde's Witness
    Flavor: "The Caverns replay Hyjal exactly. The felfire is no cooler for being a memory."
    (2) Set: You take 30% less Fire damage. Each spell cast during a new enemy wave adds 1 sec to a Sands of Time reserve, up to 10 sec.
    (4) Set: Killing an enemy or healing an ally through a hit above 20% of their maximum health spends 1 sec from the reserve to reduce your active cooldowns by 3 sec.
    (6) Set: Spending 5 sec of reserve rewinds your last spell at 18% strength and leaves a felfire patch beneath its target that damages enemies or heals allies for 6 sec.
    (8) Set: Every 40 sec, your next spell empties the reserve into a felfire ward for 15 sec. Each stored second increases the ward's radius and its damage or healing pulse by 3%.
- Leather - Hyjal Wave-Runner
    Flavor: "Eight waves before the boss, every night, forever. Nobody at the Caverns finds this strange."
    (2) Set: Your first action against each new enemy, or first heal on each newly injured ally, grants a Wave counter for 12 sec. Each counter restores 2% of your maximum resource.
    (4) Set: Killing a marked enemy or healing a marked ally above 80% health converts its counter into 10% haste for 12 sec, stacking up to five times.
    (6) Set: At three haste stacks, every third action sweeps across the wave for 18% effect on all marked enemies or allies between you and the target.
    (8) Set: At five stacks, you outrun the wave for 10 sec: immune to movement effects, no resource costs, and each action repeats at 30% strength against the next marked target.
- Mail - Jaina's Reserve
    Flavor: "Jaina holds the first base and knows precisely how long she has."
    (2) Set: Critical actions while an ally is within 20 yards add 2% to Jaina's Reserve, up to 20% of your maximum resource. Your pet and totems contribute their critical actions.
    (4) Set: Killing an enemy or critically healing an ally spends 4% of the reserve to grant allies within 15 yards 12% attack speed and spell haste for 10 sec.
    (6) Set: When the reserve is at least half full, your pet or nearest totem raises a standard. Allies near it repeat 18% of their first action every 6 sec without resource cost.
    (8) Set: Every 60 sec, the base must hold for 15 sec. The reserve stops draining, allies within 20 yards gain 15% of your offensive and healing power, and each ally present grants you 5% damage reduction, up to 25%.
- Plate - Nordrassil Warden
    Flavor: "The World Tree was traded for the win. Everyone involved agreed it was worth it, afterward."
    (2) Set: Your maximum health is increased by 12%.
    (4) Set: Falling below 50% health plants a Nordrassil seed for 15 sec. You and allies within 12 yards of it take 15% less damage. (Can only occur once every 45 sec.)
    (6) Set: Damage prevented, healing received, and damage dealt near the seed make it grow, up to 18% of your maximum health. At its cap it blooms, shielding nearby allies for the stored amount.
    (8) Set: Every 3 min, the seed becomes the World Tree for 6 sec, healing you and allies within 20 yards to full. Half the healing becomes a debt dealt to you over the same duration, but each ally who survives removes 10% of that debt.

Black Temple - Levels: 70-70
- Cloth - Illidari Apostate
    Flavor: "A draenei shrine, then an orc fortress, then this. The temple keeps the furniture."
    (2) Set: Spells against enemies or on allies below 35% health tear loose a Soul Fragment, up to three. Each fragment restores 3% of your maximum mana when your target rises above 50% or dies.
    (4) Set: While a target is below 35% health, your spells consume no Soul Fragments and gain 25% effect. Leaving that threshold causes one fragment to repeat the last spell at 40% strength.
    (6) Set: At three fragments, your next spell erects an Illidari shrine for 12 sec. It repeats 18% of harmful spells as Shadow damage and beneficial spells as a draenei ward.
    (8) Set: Every 30 sec, your next spell brands its target with the Apostate's Mark for 15 sec. All effects on it are 30% stronger; when the mark ends, the shrine repeats 25% of everything it witnessed.
- Leather - Demon Hunter's Discipline
    Flavor: "You are not prepared. Everyone says so, and everyone is correct the first six times."
    (2) Set: Critical damage, healing, or dodges grant 6 Fury, up to 60. At 20 Fury, your next action cannot miss or be resisted and sees through stealth and invisibility.
    (4) Set: Every 18 sec, your next action consumes up to 20 Fury for 4% additional effect per 1 Fury consumed. Excess over 80% is split among nearby enemies or allies.
    (6) Set: At 60 Fury, you grow spectral glaives for 12 sec. Critical actions sweep a second target for 18% effect, and dodging causes the glaives to parry the next direct hit.
    (8) Set: Reaching 60 Fury twice within 3 min triggers Metamorphosis for 12 sec: 30% increased effect and damage reduction, no resource costs, and immunity to fear and charm.
- Mail - Akama's Bargain
    Flavor: "Akama has been planning this betrayal for longer than most of the raid has been alive."
    (2) Set: Your first action against a Demon or near an ally fighting one summons a Broken shade for 10 sec. It repeats 20% of your actions from the opposite side of the target.
    (4) Set: Killing a Demon or critically healing an ally injured by one extends every shade by 10 sec and adds another, up to three shades.
    (6) Set: Each shade chooses a bargain: one mirrors 18% of damage, one mirrors 18% of healing, and one redirects 18% of damage taken to your pet or nearest totem.
    (8) Set: Every 60 sec, Akama joins for 20 sec. He commands all three shades at once, and each repeats 30% of the action matching its bargain without consuming resources.
- Plate - Warden's Vigil
    Flavor: "Maiev followed him for ten thousand years and would not describe it as a job."
    (2) Set: You cannot be feared or charmed, and take 10% less damage from Demons.
    (4) Set: Being struck by three different enemies within 6 sec closes a Warden's Cage around you, absorbing 25% of your maximum health and trapping lesser attackers at its edge. (Can only occur once every 60 sec.)
    (6) Set: Damage absorbed, blocked, or healed inside a cage is stored in its bars. Your next action breaks one bar to add 18% of the stored amount as damage or healing, up to three bars.
    (8) Set: Every 2 min, your next action cages its target for 6 sec if hostile or cages out harm if friendly. While the cage holds, your actions echo from each remaining bar at 30% total strength.

Zul'Aman - Levels: 70-70
- Cloth - Amani Hexbinder
    Flavor: "The Amani kept four animal gods and lost all of them in one afternoon. The timer was tight."
    (2) Set: Applying a periodic effect invokes an animal god for its duration: Eagle restores mana, Bear shields, Lynx grants haste, and Dragonhawk splashes the first tick. The invoked god rotates.
    (4) Set: When a periodic effect reaches its final tick, its animal god repeats that tick at 100% strength and remains with you for 8 sec.
    (6) Set: Keeping three different gods active makes their aspects hunt together: periodic ticks have an 18% chance to trigger the other two gods without advancing the rotation.
    (8) Set: Every 30 sec, all four gods answer. Your periodic effects on every target tick immediately at 50% strength, and each tick invokes a different god.
- Leather - Bear Rider's Hide
    Flavor: "Nalorakk rides the bear and is the bear. The Amani see no contradiction."
    (2) Set: Damaging, healing, or dodging adds a layer of Bear Hide for 10 sec, up to five. Each layer absorbs damage equal to 2% of your maximum health before falling away.
    (4) Set: Killing an enemy, critically healing an ally, or losing all five layers grants a Bear Charge: 25% haste and 15% movement speed for 15 sec.
    (6) Set: Charging through an enemy knocks it aside and deals 18% of your last damaging action; charging through an ally shields it for 18% of your last heal and grants it one Bear Hide layer.
    (8) Set: Every 90 sec, five layers transform you into the bear for 15 sec: 40% increased maximum health, immunity to stun, and each action charges through its target for 30% additional effect.
- Mail - Halazzi's Split
    Flavor: "Halazzi splits himself in half, and both halves are annoyed."
    (2) Set: Your attacks and spells strike or heal a second nearby target for 25% of the effect.
    (4) Set: When the split action critically strikes, its two targets are linked for 8 sec. Actions on either repeat 15% on the other, and your pet or totems may maintain one additional link.
    (6) Set: Every sixth action splits your spirit between the linked targets for 10 sec. One half repeats 18% of damage; the other repeats 18% of healing and absorption.
    (8) Set: Every 60 sec, your full spirit splits from you for 15 sec and repeats 40% of every action. Actions that already split are repeated from both targets instead of one.
- Plate - Zul'jin's Tally
    Flavor: "Zul'jin cut off his own arm to escape once, and has been keeping score ever since."
    (2) Set: Each 10% of health missing adds one mark to Zul'jin's tally. Your next action consumes one mark for 4% additional effect or 4% damage reduction if it blocks or absorbs.
    (4) Set: Dropping below 35% health stops the tally from being consumed for 12 sec, but you take 10% more damage while it is frozen. (Can only occur once every 60 sec.)
    (6) Set: Every second mark changes your aspect: Bear prevents a stun, Eagle arcs your next action, Lynx repeats it rapidly, and Dragonhawk leaves a damaging or healing patch, each at 18% strength.
    (8) Set: Recording five different enemies in the tally invokes all four aspects for 15 sec. Every action triggers the next aspect at 30% strength, and the tally cannot fall until the hunt ends.

The Sunwell - Levels: 70-70
- Cloth - Sunwell Reclaimer
    Flavor: "Destroyed, rebuilt out of a naaru, and being fought over again. Some things do not settle."
    (2) Set: Spells leave a Sunmote on their target for 10 sec. Your next different spell consumes it for 10% additional effect and restores 2% of your maximum mana to you and the nearest ally.
    (4) Set: Every 20 sec, consuming a Sunmote makes the spell instant and 60% stronger, then scatters two new Sunmotes to nearby valid targets.
    (6) Set: Consuming three Sunmotes within 12 sec opens a beam to the Sunwell for 8 sec. Your spells cost no mana and return 18% of their effect to the most injured or mana-starved nearby ally.
    (8) Set: Every 60 sec, the Sunwell rises beneath you for 15 sec. Spells cast inside leave two Sunmotes, allies inside recover 2% mana per second, and consumed motes pulse 30% of their effect through the well.
- Leather - Kil'jaeden's Reprieve
    Flavor: "Kil'jaeden comes halfway out of the well and is sent back by a dragon with better timing."
    (2) Set: You take 30% less damage from Demons.
    (4) Set: Fatal damage instead leaves you at 30% health and records a Reprieve from 4 sec earlier. (Can only occur once every 10 min.)
    (6) Set: Dodging a hit, critically damaging or healing, or receiving the Reprieve stores one moment, up to three. Consuming a moment repeats your previous action at 18% strength and restores its resource cost.
    (8) Set: Every 2 min, three stored moments rewind you 4 sec: health, position, resource, and cooldowns return to their recorded state, while an echo remains behind to repeat 30% of what you did during those 4 sec.
- Mail - Brutallus's Measure
    Flavor: "Brutallus hits for more than most raids have. That is the entire encounter."
    (2) Set: Your maximum health is increased by 15%.
    (4) Set: Damage exceeding 30% of your maximum health in a single hit is halved. The prevented half is stored as Brutal Reserve instead of lost.
    (6) Set: Overhealing, excess absorption, and damage prevented by you, your pet, or your totems add to Brutal Reserve, up to 60% of your maximum health. Every 10% stored makes your next action repeat at 18% strength.
    (8) Set: Every 2% of maximum health in Brutal Reserve increases your damage, healing, and absorption by 1%. Taking a hit above 30% releases the reserve as healing and shields among nearby allies before the hit lands.
- Plate - M'uru's Ember
    Flavor: "M'uru was a naaru for a very long time, and a void god for about six minutes."
    (2) Set: You cannot be charmed, and take 20% less Shadow damage.
    (4) Set: Killing an enemy or preventing a fatal hit on an ally turns the ember toward Light, healing nearby allies for 8% of your maximum health. Taking Shadow damage turns it toward Void, damaging nearby enemies for the same amount.
    (6) Set: Light actions leave an 18% absorption shield; Void actions leave an 18% damage echo. Blocking or parrying rotates the ember without consuming the current gift.
    (8) Set: Every 90 sec, the ember completes its turn for 12 sec. If Light is foremost, healing and shields gain 40% effect and damage becomes absorption; if Void is foremost, damage gains 40% effect and healing becomes Shadow damage. Your last six actions choose the face.

Naxxramas - Levels: 80-80
- Cloth - Kel'Thuzad's Ledger
    Flavor: "Kel'Thuzad keeps a list. Being on it is the only qualification anyone here has."
    (2) Set: Your first spell on each enemy or injured ally writes its name in the Ledger for 30 sec. Further spells on a listed target restore 2% of your maximum mana and gain 12% effect.
    (4) Set: Critical spells annotate their entry with Frost, reducing an enemy's attack and casting speed by 25% or shielding an ally from its next direct hit for 8 sec.
    (6) Set: Writing four entries opens a page for 12 sec. Spells on one listed target echo at 20% strength to the other three, then erase that target's entry.
    (8) Set: Each unique elite or boss your group defeats is entered permanently for the rest of the instance, up to 25. Every fifth permanent entry raises a shade that repeats 20% of your spells against listed targets.
- Leather - Spider Wing Creeper
    Flavor: "Maexxna wraps the slow ones first. Nobody has ever agreed on who that was."
    (2) Set: You are immune to root effects and take 25% less damage from periodic effects.
    (4) Set: Applying a periodic effect spins a web beneath its target for 10 sec. Enemy webs slow and deal the final tick again; allied webs absorb damage equal to the final tick.
    (6) Set: Crossing a web strand or dodging inside one grants Spider's Haste. Your next action within 6 sec leaps along the strand and repeats 20% of its effect at the other end.
    (8) Set: Every 45 sec, you web all targets within 12 yards for 4 sec. Each enemy caught adds 8% to your damage and avoidance; each ally caught adds 8% to your healing and periodic effect, up to 40% total.
- Mail - Four Horsemen's Mark
    Flavor: "Four riders, four corners, and a mark that stacks whether or not you understand it."
    (2) Set: Consecutive actions on one target apply the Horsemen's Mark, up to four. Each mark adds 6% effect, but acting on a different target moves the oldest mark there.
    (4) Set: At four marks, your next action invokes a Horseman: Thane cleaves, Blaumeux leaves a void zone, Zeliek chains healing, and Rivendare restores resource. The Horseman rotates.
    (6) Set: Your pet or nearest totem may hold a second set of marks. When either set reaches four, 20% of its triggering action crosses to the other marked target.
    (8) Set: Every 60 sec, four marked targets become the Four Corners for 20 sec. Actions at one corner repeat at 25% strength at every other corner, and allies standing there take 20% less damage.
- Plate - Patchwerk's Leftovers
    Flavor: "Patchwerk was assembled from the best parts available. This was assembled from the rest."
    (2) Set: Your maximum health is increased by 15% and you take 20% less damage from Undead.
    (4) Set: Every 4 sec in combat, a Leftover stitches itself on, healing you for 3% of your maximum health and remaining as one spare part, up to four.
    (6) Set: Damaging, healing, blocking, or parrying consumes one spare part to add 20% of the amount to your next different kind of action. At four parts, none are consumed for 8 sec.
    (8) Set: A hit above 15% of your maximum health is halved and tears off every spare part. Each part becomes a Hateful Strike against the attacker and a 5% maximum-health heal to the most injured nearby ally.

The Obsidian Sanctum - Levels: 80-80
- Cloth - Twilight Ashweave
    Flavor: "Sartharion keeps three drakes alive out of pride. It has never once gone well for him."
    (2) Set: You take 35% less Fire damage. Fire damage taken weaves a Twilight Thread for 10 sec; your next spell carries the thread to its target for 12% additional damage, healing, or absorption.
    (4) Set: Threads invoke the nearest living drake: Tenebron spreads the spell, Shadron doubles its periodic portion, and Vesperon returns 20% as mana. The invoked drake rotates.
    (6) Set: Keeping all three drake invocations active opens a Twilight Fissure for 10 sec. Spells cast through it emerge at the target for 20% additional effect and cannot be interrupted.
    (8) Set: Every 60 sec, the three drakes remain up for 15 sec. Each spell triggers all three invocations, and every additional enemy beyond one within 20 yards adds a 10% echo, up to 30%.
- Leather - Tenebron's Brood
    Flavor: "Leaving the drakes up is optional. So is surviving it."
    (2) Set: Critical damage, healing, or dodges lay a Twilight Egg near the target for 12 sec, up to three. Each egg stores 12% of the triggering effect.
    (4) Set: Killing an enemy, healing an ally above 80%, or dodging a heavy hit hatches every nearby egg. Each whelp repeats its stored effect and grants 25% haste for 12 sec.
    (6) Set: Whelps remain for 20 sec and repeat 20% of the action that matches what hatched them: damage, healing, or avoidance. A new egg refreshes the oldest whelp.
    (8) Set: Every 60 sec, Tenebron opens the portal for 20 sec. Eggs hatch instantly, whelps repeat 30% of every action, and each active whelp reduces area damage you take by 10%.
- Mail - Twilight Portal-Walker
    Flavor: "The portals go somewhere worse and return you to exactly where you were standing."
    (2) Set: You take 25% less Shadow damage and cannot be charmed.
    (4) Set: Your effects open a small Twilight Portal behind their target for 8 sec. Your next action on that target emerges from the portal at 25% strength.
    (6) Set: Your pet or nearest totem anchors a second portal. Every third action crosses between the pair, repeating 20% of its damage, healing, or absorption around both exits.
    (8) Set: Every 45 sec, you step through for 5 sec and become untargetable by enemies. Actions taken inside emerge from both portals at 35% strength when you return to your original position.
- Plate - Sartharion's Contempt
    Flavor: "The black drake sits on a lake of fire and waits for you to make the interesting choice."
    (2) Set: You are immune to knockback effects and take 25% less Fire damage.
    (4) Set: While three or more enemies are within 15 yards, your armor becomes Obsidian. Each direct hit chips off a shard that damages the attacker or shields the next ally you heal.
    (6) Set: Standing in harmful ground effects hardens one shard per second, up to four. Your actions launch hardened shards for 5% of your maximum health as damage or healing each.
    (8) Set: Harmful ground effects deal 60% less damage to you. At four hardened shards, a meteor falls at your position, consuming them to damage enemies and shield allies for 35% of your maximum health.

The Eye of Eternity - Levels: 80-80
- Cloth - Malygos's Objection
    Flavor: "The Spell-Weaver decided mortals were done with magic. The raid disagreed at length."
    (2) Set: Each spell reduces the cost of the next different spell by 12%, stacking up to five times. Repeating a spell consumes the stacks without their cost reduction.
    (4) Set: Critical spells stabilize the chain, restoring 6% of your maximum mana and preventing its stacks from being consumed for 8 sec.
    (6) Set: Reaching five stacks attracts a Power Spark for 10 sec. Spells cast near it repeat at 20% strength and pass one cost-reduction stack to a nearby ally.
    (8) Set: At five stacks, your next different spell detonates the Spark: it is free and 50% stronger, then every spell in the chain is echoed at 20% strength against the same target.
- Leather - Nexus Drake-Rider
    Flavor: "The last phase is fought from the back of a drake, which nobody's leather was cut for."
    (2) Set: Your movement speed is increased by 12% and cannot be reduced below normal.
    (4) Set: Actions used while moving add a Drake Combo Point to the target, up to five. Damaging, healing, and dodging each add a different color of point.
    (6) Set: At five points, your next action becomes a finisher: red points repeat 20% as damage, green points repeat 20% as healing, and bronze points grant 6% dodge and damage reduction each.
    (8) Set: Every 45 sec, spending five mixed points takes you into flight for 8 sec. You ignore movement and ground effects, and each action triggers all three finishers at 35% total strength.
- Mail - Power Spark Conduit
    Flavor: "The sparks drift in from the edge of the platform and are the only reason anyone wins."
    (2) Set: Every fifth action attracts a Power Spark that restores 3% of your maximum resource each second as it approaches.
    (4) Set: Catching the Spark makes your next action within 8 sec 100% stronger. If your pet or totem catches it first, both of your next actions gain 50% instead.
    (6) Set: A caught Spark orbits your pet or nearest totem for 10 sec, repeating 20% of your actions and granting its targets 10% haste for 6 sec.
    (8) Set: Every 20 sec, the orbiting Spark lands between you and the nearest ally for 10 sec. Actions crossing it gain 25% effect and haste, and chain once to the other side.
- Plate - Blue Flight Deserter
    Flavor: "Not every blue dragon agreed with Malygos. Their armor ended up here regardless."
    (2) Set: You take 30% less Arcane damage and cannot be critically struck by spells.
    (4) Set: Taking Arcane damage or blocking a spell stores 20% of it in a Blue Scale for 12 sec, up to three scales.
    (6) Set: Damaging or healing launches one Blue Scale, adding its stored amount to the action and leaving 20% of that total as a shield on the target.
    (8) Set: Twenty-five percent of all magic damage you take becomes a Blue Scale instead. When three are stored, they fly to the three most injured nearby allies as shields and heal you for the total absorbed.

Vault of Archavon - Levels: 80-80
- Cloth - Wintergrasp Spoil
    Flavor: "The Vault opens for whoever holds Wintergrasp that hour. The armor does not care who that was."
    (2) Set: Your first spell on a target plants a Wintergrasp flag for 15 sec. A second spell captures it, restoring 4% of your maximum mana and adding 12% effect to that spell.
    (4) Set: Killing a flagged enemy or critically healing a flagged ally captures its workshop for 20 sec, up to three. Each workshop sends a siege bolt at your next target every 6 sec.
    (6) Set: With three workshops, your spells also capture ground beneath the target for 8 sec. Enemy ground is bombarded; allied ground grants 20% damage reduction and mana regeneration.
    (8) Set: Every 60 sec, three captured workshops build a fortress around you for 15 sec. Allies inside gain 30% effect, enemies cannot move the occupants, and every spell fires all three siege bolts.
- Leather - Emalon's Charge
    Flavor: "Emalon keeps four minions charged and has no other ideas."
    (2) Set: Damaging, healing, or dodging charges one of four Tempest Minions orbiting you. A charged minion repeats 12% of your next action, then discharges.
    (4) Set: With three or more targets nearby, each charged minion chooses a different target and repeats 40% of the action divided among them.
    (6) Set: Charging all four minions Overcharges the oldest for 10 sec. It repeats 20% of every action and shocks enemies that strike you before exploding.
    (8) Set: Every 25 sec, all four minions discharge as chain lightning, damaging enemies and healing allies for 30% of your maximum health split among them, then return fully charged.
- Mail - Koralon's Ember
    Flavor: "Koralon burns the floor and waits. It has all the time the siege allows."
    (2) Set: You take 30% less Fire damage.
    (4) Set: Taking Fire damage or critically acting inside a fire patch creates an Ember, up to three. Each Ember causes your next action to leave a burning patch for 12% of its effect.
    (6) Set: At three Embers, your pet or nearest totem becomes a Meteor Fist for 10 sec, pounding its area every 2 sec to damage enemies and shield allies for 20% of your last action.
    (8) Set: You burn steadily without harming allies. Enemies within 8 yards take Fire damage and allies are healed each second for 3% of your maximum health; every third pulse drops a burning patch and restores all three Embers.
- Plate - Archavon's Weight
    Flavor: "Archavon the Stone Watcher has stood in that vault since before Wintergrasp had a name."
    (2) Set: Your armor is increased by 25% and your movement speed reduced by 5%.
    (4) Set: Striking, taunting, or blocking an enemy marks it with Archavon's Hand; marked enemies deal 25% less damage to you until they move more than 10 yards away.
    (6) Set: Every 5 yards moved stores one Stone Step, up to five. Stopping for 2 sec slams the stored steps into the ground, adding 4% of your armor per step to your next damaging or healing action.
    (8) Set: At five Stone Steps, you become the Stone Watcher for 15 sec: you cannot be moved, your actions send 15% of your armor as shockwaves through nearby enemies or allies, and marked enemies are pulled back when they flee.

Ulduar - Levels: 80-80
- Cloth - Yogg-Saron's Margin
    Flavor: "The Old God in the basement has been talking to the keepers for a very long time."
    (2) Set: Every third spell opens a Whisper in the margin. Accepting it costs 3% of your maximum health and makes the next different spell 40% stronger; refusing it restores 3% of your maximum mana.
    (4) Set: With no ally within 20 yards, Whispers remain open for twice as long and their accepted spell leaves a Sanity Ward that reduces damage taken by 15% for 8 sec.
    (6) Set: Accepting three Whispers summons a Guardian of Yogg-Saron for 12 sec. It repeats 20% of your spells, then returns half the health paid as healing or absorption.
    (8) Set: Every 60 sec, the whisper offers a bargain for up to 20 sec: each second grants 2% spell effect and costs 3% maximum health. Ending it early detonates the accumulated effect through every active Sanity Ward.
- Leather - Mimiron's Tolerance
    Flavor: "Mimiron built four phases of himself, and a self-destruct for each one."
    (2) Set: You take 35% less damage from area effects.
    (4) Set: Your first action after avoiding area damage deploys a component for 10 sec: Leviathan strikes enemies, VX-001 shields allies, and Aerial Unit increases movement speed. Components rotate.
    (6) Set: Keeping all three components active assembles V-07-TR-0N for 12 sec. Each component repeats 20% of the action matching its purpose, and critical actions repair their duration.
    (8) Set: Every 90 sec, the emergency button starts a 15 sec self-destruct. Each 5 sec overloads one component for 35% effect; surviving all three detonates them harmlessly and grants every overload for 10 sec.
- Mail - Thorim's Charge
    Flavor: "Thorim waits in the arena for someone to reach him. The stairs are the encounter."
    (2) Set: Critical actions grant a Thunder Charge, up to ten. Your pet and totems can generate one charge every 3 sec.
    (4) Set: Every 12 sec, your next action spends up to three charges to call lightning on that many nearby enemies or allies for 20% of the action per charge.
    (6) Set: At six charges, lightning jumps continuously between you and your pet or nearest totem. Actions crossing the arc gain 20% effect and make its next jump immediate.
    (8) Set: At ten charges, the arena becomes a storm for 12 sec. Each action spends one charge to damage enemies and heal allies within 20 yards for 4% of your maximum health; criticals keep the storm charged.
- Plate - Iron Council Standard
    Flavor: "Steelbreaker, Runemaster Molgeim, Stormcaller Brundir. Kill them in whichever order you can survive."
    (2) Set: Your armor is increased by 20% while three or more enemies are within 12 yards.
    (4) Set: Melee hits against you invoke Steelbreaker, returning Nature damage equal to 10% of your armor. Damaging invokes Brundir; healing or blocking invokes Molgeim.
    (6) Set: Each Council member leaves a rune for 10 sec: Brundir's repeats 20% as lightning, Molgeim's repeats 20% as healing or shielding, and Steelbreaker's reduces the next hit by 20%.
    (8) Set: Keeping all three runes active raises the Iron Council Standard for 15 sec. Every action triggers all three runes, and the rune matching your most-used role in the last 10 sec acts twice.

Trial of the Crusader - Levels: 80-80
- Cloth - Crusader's Trial-Weave
    Flavor: "The Argent Crusade built a coliseum outside Icecrown and fights everything in it except Icecrown."
    (2) Set: Every 15 sec in combat earns an Argent Seal. Your next spell spends it for 12% additional effect and applause that restores 4% of your maximum mana.
    (4) Set: Killing an enemy or rescuing an ally below 20% health awards the current round, granting two Seals and making the next one last twice as long.
    (6) Set: Spending four Seals invokes the defeated round for 12 sec: Beasts cleave, Champions interrupt enemies, Val'kyr echo spells, and Anub'arak shields. The round rotates.
    (8) Set: Every 60 sec in combat completes a round and permanently improves its invocation by 8% for the rest of the fight, up to four rounds. Completing all four invokes them together.
- Leather - Faction Champion's Grudge
    Flavor: "One round of the trial is other adventurers. Everyone remembers that round."
    (2) Set: Your first action on each target starts a Grudge for 15 sec. Acting on anyone else stores 12% of that action in the Grudge instead of ending it.
    (4) Set: Critical actions settle the Grudge: enemies receive 40% less healing and take the stored amount, while allies receive 40% more healing and gain it as absorption.
    (6) Set: Dodging or being struck by a new damage school adds that school to the Grudge. Settling it grants 20% resistance to every recorded school and makes your next action unavoidable.
    (8) Set: Every 45 sec, your longest Grudge names a Faction Champion for 15 sec. You adapt to its last three actions, gaining 30% resistance to their schools and reflecting their control effects.
- Mail - Twin Val'kyr's Balance
    Flavor: "Light and dark, and a wall of it moving down the middle of the room."
    (2) Set: Your actions alternate Light Essence and Dark Essence. Light repeats 20% as healing or absorption; Dark repeats 20% as damage, regardless of the original action.
    (4) Set: Striking a target with the opposite Essence creates Balance for 8 sec, adding 20% effect to the next action and stacking up to three times.
    (6) Set: Your pet or nearest totem holds the opposite Essence. Every action crosses the two essences, repeating 20% around both positions and swapping which one you carry.
    (8) Set: At six swaps, the Twin Val'kyr collide: your next action is 100% stronger, affects every valid target within 15 yards, and applies both Light and Dark without advancing the cycle.
- Plate - Anub'arak's Burrow
    Flavor: "The floor gives way in the final round. Nobody involved planned for the basement."
    (2) Set: You take 25% less damage from Undead and cannot be rooted.
    (4) Set: Each enemy within 10 yards grows one layer of Burrowed Chitin, up to five. A direct hit removes one layer instead of striking you for its full amount.
    (6) Set: Removed layers become spikes beneath your next target. Each spike adds 4% of the triggering damage, healing, or absorption and impales a nearby enemy if the target is allied.
    (8) Set: Every 90 sec, the ground opens beneath targets within 15 yards. Enemies are rooted for 4 sec, allies gain Burrowed Chitin, and each target caught raises one 8% spike that follows your actions for 20 sec.

Icecrown Citadel - Levels: 80-80
- Cloth - Lich King's Regard
    Flavor: "The Frozen Throne is at the top of this citadel. Everything below it is a delaying tactic."
    (2) Set: Spells tear a Soul Shard from their target for 10 sec. Your next different spell consumes it for 12% additional effect and carries the soul to the Frozen Throne.
    (4) Set: Critical spells freeze the target for 8 sec, slowing an enemy's attacks and movement by 30% or shielding an ally from 30% of the next hit. Frozen targets yield two Soul Shards.
    (6) Set: Delivering six Soul Shards releases a Vile Spirit for 12 sec. It follows your target, repeating 20% of harmful spells as Frost damage or beneficial spells as absorption.
    (8) Set: Every 45 sec, the Throne spends every carried soul on your next spell, echoing it at 10% strength per soul against every enemy or ally you touched in the last 10 sec, up to 60%.
- Leather - Frostwing Halls Prowler
    Flavor: "Sindragosa was Malygos's equal once. Now she guards a stairwell."
    (2) Set: Critical damage, healing, or dodges crack one layer of Frostwing Ice, up to three. Each crack grants 8% movement speed and makes the next crack easier to trigger.
    (4) Set: Killing an enemy, saving an ally below 20% health, or avoiding a heavy hit shatters a layer, granting 20% haste for 12 sec and leaving an ice patch behind.
    (6) Set: Crossing your own ice patch launches a Frostwing echo to your target for 20% of your last action and grants 6% dodge and area-damage reduction for 8 sec.
    (8) Set: Shattering all three layers makes you Unbound for 15 sec: immune to movement effects, no resource costs, and every action launches a 35% Frostwing echo from the nearest ice patch.
- Mail - Blood Queen's Thirst
    Flavor: "Lana'thel bit the San'layn court one at a time. The court did not object."
    (2) Set: Eight percent of your damage and 12% of your healing fills the Blood Queen's Thirst, up to 20% of your maximum health. At its cap, it bites your target for the stored amount as damage or healing.
    (4) Set: Below 50% health, Thirst fills twice as fast and every bite returns half its amount to you. Above 50%, bites overflow to the most injured nearby ally.
    (6) Set: A bite infects your pet or nearest totem for 20 sec. It repeats 20% of your actions as leeching damage or transfused healing and can fill Thirst on your behalf.
    (8) Set: Every 60 sec, a bite passes the Thirst to an ally for 30 sec. Your actions feed both vessels, overflow between them, and erupt at 35% increased strength when either reaches its cap.
- Plate - Ashen Verdict Bulwark
    Flavor: "Two orders that hated each other for a decade forged one ring and marched in together."
    (2) Set: You take 30% less damage from Undead and cannot be feared or charmed.
    (4) Set: Fatal damage instead leaves you at 30% health and forges an Ashen Sigil that shields you for 25% of your maximum health. (Can only occur once every 10 min.)
    (6) Set: Above 50% health, damaging or healing forges an Ashen Sigil on the target; below 50%, blocking or taking damage forges a Verdict Sigil on you. At three sigils, your next action consumes them for 20% effect each.
    (8) Set: Ashen Sigils grant allies within 25 yards 10% damage and healing; Verdict Sigils grant 10% damage reduction. Below 50% health the sigils return to you and double, while consuming three shares their benefit with the raid for 10 sec.

The Ruby Sanctum - Levels: 80-80
- Cloth - Halion's Twilight
    Flavor: "Halion fights in two realms at once and expects you to keep up in both."
    (2) Set: Your spells alternate Corporeal and Twilight realms. Corporeal spells leave 12% of their effect on the target; the next Twilight spell releases it as Shadow damage or absorption.
    (4) Set: Periodic effects exist in both realms. Direct spells against their targets trigger an immediate 30% tick without advancing the duration.
    (6) Set: Critical spells tear open a realm portal for 8 sec. Spells cast through it leave a 20% echo in the opposite realm, and crossing it restores 6% of your maximum mana.
    (8) Set: You exist in both realms. Every spell is repeated at 25% strength by its opposite: Corporeal echoes as Shadow damage or a Twilight absorb, while Twilight echoes as Fire damage or direct healing.
- Leather - Twilight Cutter's Gap
    Flavor: "The beam sweeps the room on a timer. There is a gap. Find it early."
    (2) Set: You take 40% less damage from area effects.
    (4) Set: Avoiding all damage for 4 sec reveals the Cutter's Gap for 3 sec. Acting through the gap doubles the action and moves you 5 yards to the safe side.
    (6) Set: Dodging or crossing the Gap leaves a Twilight Marker for 10 sec. Your next action from the opposite side sweeps between you and the marker at 20% effect on every target in its path.
    (8) Set: Every 30 sec, a Twilight Cutter sweeps from you toward every active marker. Enemies in its path take your last damaging action at 35% strength; allies gain 35% of your last heal and 20% damage reduction for 12 sec.
- Mail - Baltharus's Split
    Flavor: "Baltharus the Warborn makes a copy of himself, and neither one is the real problem."
    (2) Set: Your attacks and spells strike or heal a second nearby target for 30% of the effect.
    (4) Set: Killing an enemy or critically healing an ally splits a lesser copy from you for 15 sec, up to three. Each copy repeats the 30% secondary effect from a different position.
    (6) Set: Your pet or nearest totem anchors the copies. Every third action orders one copy to hold your threat, one to repeat 20% as damage, and one to repeat 20% as healing or absorption.
    (8) Set: Every 90 sec, Baltharus's full clone splits from you for 20 sec. It repeats 50% of your actions, holds its own threat, and causes every lesser copy to repeat from both of its targets.
- Plate - Ruby Sanctum Warder
    Flavor: "The red flight kept the last dragon eggs here, which is exactly why the Twilight came."
    (2) Set: Your maximum health is increased by 15% and you take 25% less Fire damage.
    (4) Set: Falling below 40% health hatches a Ruby Egg, healing you and allies within 12 yards for 25% of your maximum health. (Can only occur once every 3 min.)
    (6) Set: Preventing damage, healing an ally below 40%, or surviving a heavy hit warms an Egg, up to three times. A fully warmed Egg hatches a whelp that repeats 20% of your actions and intercepts one fatal hit.
    (8) Set: The red flight's gift leaves allies within 20 yards at 20% health instead of dying once every 5 min. Each life saved hatches every Egg, and the resulting whelps repeat 35% of your actions for 20 sec.

Progression Beyond Legendary
--------------------
Design only. Nothing in this section is implemented, and nothing in it has been
written into AUTHORED_SETS, mod-reliquary, or the core. It exists so the numbers
and the blockers are settled before any of it is built.

Raid sets currently drop at one item level per raid and stop there. This section
adds three things: difficulty tiers on the drop, an Artifact quality reached by
upgrading a legendary at the Reliquarian, and a Primal quality above it. The
upgrade never destroys a legendary. It consumes tokens farmed from the raid the
piece came from, so old raids stay worth running at level 80.

Quality ladder
    2  Uncommon    green         world sets, drop
    3  Rare        blue          dungeon sets, drop
    5  Legendary   orange        raid sets, drop, four difficulty tiers
    6  Artifact    pale gold     upgrade, three level bands
    8  Primal      deep scarlet  upgrade, band 80 only

Quality 4 (Epic) and 7 (Heirloom) are deliberately skipped. Epic has no content
tier left to sit on. Heirloom is unusable: ItemTemplate.h overrides item level
entirely with pLevel * 2.33f for that quality, so every stat decision below
would be silently discarded.

Legendary difficulty tiers
--------------------
The four tiers are the real raid difficulties, so the server reads them off the
map rather than guessing. The spacing is Wrath's own: at level 80 the ladder
runs from 245 to 284, which is Val'anyr at the bottom and Shadowmourne at the
top -- the only two legendaries the expansion shipped.

    difficulty        L60    L70    L80
    10 normal         187    217    245
    25 normal         197    228    258
    10 heroic         207    240    271
    25 heroic         217    251    284

The tier multipliers are 0.863 / 0.908 / 0.954 / 1.000 against the band top, and
the band tops (217 / 251 / 284) are what the raid sets already generate today,
so the 25-heroic column is the current behaviour and the other three are new
steps below it.

Most raids do not have four difficulties. Molten Core, Blackwing Lair and
Ahn'Qiraj Temple are 40-man; Zul'Gurub and Ruins of Ahn'Qiraj are 20-man;
Karazhan and every Burning Crusade raid but Zul'Aman are single-difficulty. A
raid that Blizzard never subdivided awards its band top, because clearing Molten
Core at 40-man *is* the hardest thing available at level 60. Only the Wrath
raids -- Naxxramas, Obsidian Sanctum, Eye of Eternity, Ulduar, Trial of the
Crusader, Icecrown Citadel, Ruby Sanctum -- offer all four rungs.

The ladder is continuous where it should be: L70 10-normal (217) is exactly L60
25-heroic (217), so the hardest tier of one bracket equals the easiest tier of
the next. It overlaps once, at L70 25-heroic (251) beating L80 10-normal (245),
which is correct -- Sunwell gear did outclass Naxxramas 10 at the time.

Artifact bands
--------------------
An Artifact is a level band, not a raid tier. A legendary can be raised to the
band matching its acquisition level and then to each band above it, ten levels
at a time, so a Molten Core piece climbs 60 -> 70 -> 80 in three steps and an
Icecrown Citadel piece reaches 80 in one.

    difficulty      band 60  band 70  band 80
    10 normal         259      302      345
    25 normal         273      318      363
    10 heroic         286      334      382
    25 heroic         300      350      400

Band tops are 300 / 350 / 400, fifty item levels apart, with the same difficulty
multipliers applied across each row. 400 at 25-heroic band 80 is the ceiling.

Every legendary in the game therefore ends in the same place. A Molten Core
piece and an Icecrown Citadel piece both finish at 400 in their difficulty
column; the Molten Core piece just pays three times to get there. That is the
point -- it makes all 23 raids a live path to the ceiling instead of leaving
nineteen of them dead the moment Icecrown opens.

The band-60 Artifact is item level 300 at required level 60. That is far above
anything the level-60 game contains and is the single largest balance decision
here. It is deliberate -- these are raid legendaries that have been paid for
twice -- but it is the first number to turn down if the curve feels wrong.

Primal
--------------------
Band 80 only, no difficulty tiers, item level 425. Every path converges on one
value, which is what makes it an endpoint rather than another rung.

425 is only six percent over the Artifact ceiling, so the item level is not
where Primal gets its weight. Its stat *shape* is. Every other tier in this
catalog spends its whole budget on two lines, primary and stamina, which is why
those two match real gear and the pieces carry no crit, haste, or spell power at
all. Primal is the only tier that keeps those two lines at full value and adds
two more on top, at 0.55 share each, chosen by armor family. item_template
already carries ten stat slots and the generator only ever fills two, so the
lever exists today. That lands a Primal piece around 1.6x the total stat budget
of anything else in the game, which is the intent.

Stats
--------------------
Existing formulas, unchanged: primary is item level x 0.37 x slot share,
stamina x 0.38, armor is the item level 232 donor scaled by item level / 232.
A full-share slot (head, chest, legs) at the top difficulty column:

    tier                     ilvl   primary  stamina  plate chest armor
    Legendary 25H, L80        284     105      108        2900
    Artifact  25H, band 60    300     111      114        3064
    Artifact  25H, band 70    350     130      133        3574
    Artifact  25H, band 80    400     148      152        4084
    Primal,        band 80    425     157      162        4340

Primal additionally carries two secondary lines at 0.55 share, roughly +87 each
at a full-share slot.

MAX_ILEVEL in mod-source-item-sets/tools/generate_catalog.py is currently 300
and would need raising to 425. item_template.ItemLevel is smallint unsigned, so
the column itself is not a constraint.

Upgrade cost
--------------------
The legendary is never consumed. Each step costs the piece itself plus tokens
that drop only in the raid the piece came from, at roughly 50 tokens per step.
A Molten Core piece pays 150 Sulfuron Ingots to reach band 80; an Icecrown
Citadel piece pays 50 Primordial Saronite. The older the raid, the more tokens
and the easier each one -- which is the mechanism that keeps Molten Core, Zul'
Gurub and Black Temple being run at level 80.

Four raids already have a bind-on-pickup token that drops nowhere else and can
be used as-is:

    Molten Core            Sulfuron Ingot
    Ulduar                 Fragment of Val'anyr
    Trial of the Crusader  Trophy of the Crusade
    Icecrown Citadel       Primordial Saronite

The remaining nineteen need one nominated. Where the raid already has a unique
drop with the right flavour -- Onyxia's head, the Ahn'Qiraj scarabs and idols,
the Zul'Gurub bijous, the Burning Crusade tier tokens -- use it rather than mint
a new one, so the token is something players already recognise. Everything else
gets a new item.

Primal's cost is unsettled. It should not be more of the same token, or the last
step is just a longer version of the previous one.

What this needs from other modules
--------------------
mod-reliquary is where all of this lives. Artifact and Primal destinations are
generated reliquary templates in the 2000000+ range, so mod-source-item-sets
never needs to know either quality exists. Three things there block it today:

  - MIN_QUALITY / MAX_QUALITY are 1 and 4, and the catalog query filters
    Quality BETWEEN 1 AND 4. Legendary is already excluded, which means the 736
    raid pieces are currently invisible to the Reliquarian. This is a live bug
    regardless of whether any of the rest gets built.
  - TIER_CEILING has columns for qualities 1-4 only. Widening the filter without
    adding columns is a KeyError, not a graceful skip.
  - The tier list ends at TIER_RAID_25H / 277. Artifact and Primal need tiers
    above it, and the band table (floor 30, step 5) needs a second ladder that
    steps by 10 from 60.

Artifact and Primal should be band-80-and-up only in the catalog sense: one
destination per source per band, not per five-level band. mod-reliquary already
reserves 133,119 item_template entries; a per-5-band artifact ladder would
multiply that again for destinations nobody can wear.

mod-random-item-enchants tops out at a single catch-all bracket covering item
level 300 to 999, granting +28 stats and +34 ratings. An item level 425 Primal
piece would roll exactly the same affixes as an item level 300 one. Compensating
means subdividing 300-425 into real steps, which needs new SpellItemEnchantment
rows -- stock 3.3.5 has nothing above roughly +28 stat / +40 spell power -- plus
the client patch to carry them. That module already authors its own enchant ids
(61100-61103), so the pattern is established.

Core changes for quality 8
--------------------
Quality 6 (Artifact) needs nothing. It exists in SharedDefines.h, and
ItemTemplate.h groups it with epic and legendary in GetItemLevelIncludingQuality,
so there is no hidden item level penalty. The client already colours it pale
gold.

Quality 8 (Primal) does not exist anywhere and needs five edits:

  - SharedDefines.h:315-327 -- add ITEM_QUALITY_PRIMAL = 8 and raise
    MAX_ITEM_QUALITY from 8 to 9.
  - ObjectMgr.cpp:3534 -- until that constant moves, every Primal item is
    silently reset to white at load. It logs an error and carries on rather than
    failing the load, so this fails quietly and looks like a data problem.
  - ObjectMgr.cpp:3290 and 3302 -- qualityToBuyValueConfig and
    qualityToSellValueConfig are sized MAX_ITEM_QUALITY and need a ninth entry
    each, which means two new worldserver.conf values.
  - cs_bag.cpp:24 -- itemQualityToString is sized the same and needs a ninth
    string.
  - AchievementMgr.cpp:253 already guards on MAX_ITEM_QUALITY and needs nothing
    once the constant moves.

Client-side, deep scarlet is the hard part. The 3.3.5 client knows qualities 0
through 7; GetItemQualityColor is a binary API over that range and quality 8 is
out of bounds. A FrameXML override shipped in patch-Z.MPQ extends
ITEM_QUALITY_COLORS and covers everything Lua draws -- tooltips, chat links, bag
slot borders -- but anything the client draws natively from its own table will
fall back to whatever an out-of-range index gives. That behaviour has not been
tested here and should be, on a throwaway item, before any of this is built.

Open questions
--------------------
  - Difficulty tiers multiply the raid catalog. 23 raids x 4 armor families is
    92 sets today; adding four difficulty variants makes it 368, and the item id
    bands in generate_catalog.py were not sized for that.
  - Whether a Primal piece keeps its set bonus. mod-reliquary preserves itemset
    and the source-item-sets bonuses are percentages now, so it would scale --
    but a 4-piece Primal set is a very large number and may want its own tuning.
  - What Primal costs, given it should not just be more raid tokens.
  - Whether the band-60 Artifact at item level 300 stands, or whether the
    Artifact ladder should start nearer the legendary it came from.


Affix Ladder Expansion
--------------------
Design only. mod-random-item-enchants owns the bracket table in
src/RandomItemEnchantsLogic.cpp, and mod-reliquary rescales affixes through the
same table, so anything fixed here is inherited by both.

Three problems, all of them at exactly the item levels the tiers above occupy.

The top bracket is a catch-all covering item level 300 to 999. An item level 425
Primal piece rolls precisely the affixes an item level 300 piece rolls. Every
one of the new bands lands inside a single undifferentiated bucket.

The rating affixes plateau long before that. Haste, Hit, Dodge and Parry sit at
+20 across four consecutive brackets, from 201-220 through 261-299, while the
stat lines keep climbing +20, +22, +24, +26. Critical Strike freezes at +20 for
three. Mana per 5 sec has been +14 since the 161-180 bracket, unchanged through
seven brackets. An affix that stops growing while the piece it sits on doubles
in item level stops being a reason to care which affix rolled.

The proposal is to keep the 20-wide shape, carry it to 425, and let the ratings
track the stat line at roughly 1.2x instead of freezing.

    bracket      stat  rating  crit    AP   SP  mp5
    201-220        20      24    24    40   26   16
    221-240        22      26    26    44   28   18
    241-260        24      29    29    48   34   20
    261-299        26      31    31    52   37   22
    300-319        30      36    36    60   42   24
    320-339        33      40    40    66   46   26
    340-359        36      43    43    72   50   28
    360-379        39      47    47    78   55   30
    380-399        42      50    50    84   59   32
    400-425        45      54    54    90   63   34

The first four rows are existing brackets with the plateau removed; the last six
replace the 300-999 catch-all.

Cost. Stock 3.3.5 has nothing above roughly +28 stat, +34 rating and +40 spell
power, so almost every value in that table needs a new SpellItemEnchantment row
-- about 84 for the six new brackets and another 16 to unfreeze the ratings in
the existing ones. The module already authors its own ids in the 61100 block for
exactly this reason, so the pattern exists; the rows are client-read for the
suffix text, so they ride the existing patch.

Code. The Brackets array and BracketCount in RandomItemEnchantsLogic.cpp, and
the fallback on line 174, which reads `itemLevel >= 300 ? Brackets.size() - 1 :
0` and needs its constant moved to the new top floor.


Too Deeply We Delved
--------------------
Design only. A new module, not yet written.

Every unique boss in the game, the first time you kill it, grants one permanent
stack of "Too Deeply We Delved". Each stack is +1% to all stats, and the buff is
only active while you are on a raid map. Dungeons are where it is farmed and
raids are where it pays, which is the whole loop: the reward for clearing old
content is being able to walk into new content.

The boss list already exists and should not be invented. instance_encounters is
the DungeonEncounter.dbc-backed table of every scripted boss in the game and is
the right source, but the key matters:

    612  rows in instance_encounters
    434  unique (creditType, creditEntry) pairs
    168  credits shared by more than one row

Those 168 are the same boss listed once per raid difficulty. Keying the ledger
on the encounter `entry` would let a single boss pay out up to four times for
being killed on 10-normal, 25-normal, 10-heroic and 25-heroic. Key the ledger on
the **credit**, not the entry, and the count is 434.

Which means the ceiling is +434% to all stats. That is a little over five times
a character's base stats, and it is worth stating plainly because it is far more
than the problem being solved needs -- clearing Icecrown Citadel trash in Ulduar
gear wants something closer to a doubling, which is about 100 bosses. A
configurable cap on the stack count is the first lever and should exist from the
start rather than being retrofitted after someone has 400 stacks.

Proposal: Initial Cap @ 250%

Shape:

    Ledger      One character table, one row per (guid, creditType, creditEntry),
                unique key on all three so a re-kill is a no-op insert. Per
                character by default, with an account-wide config, because
                account-wide turns every alt into a fully-buffed raider on day
                one.
    Aura        A single spell using the percentage-stat aura Blessing of Kings
                uses, with base points set from the player's count. Not 434
                cloned spells -- the magnitude is per player, so the tooltip has
                to read "increased by 1% for each unique boss you have defeated"
                rather than stating a number.
    Applied     On entering a map where map->IsRaid() is true, removed on
                leaving. Recalculated on login, on map change, and at the moment
                a new boss is credited, so it ticks up mid-raid rather than at
                the next zone-in.
    Credited    On encounter completion rather than on creature death. Bosses
                that summon copies of themselves, or that are scripted to die
                twice, will double-count off a raw kill hook.
    creditType  34 of the 612 rows are creditType 1, completed by a spell rather
                than a creature kill. They need either handling or a documented
                exclusion; silently dropping them makes a handful of bosses
                uncountable and the total unreachable.

Open questions:

  - Dungeon bosses only, or raid bosses too. 434 is everything. Counting only
    dungeon bosses is a much smaller and more gradual number, and makes the
    dungeon-farms-raid loop literal rather than thematic.
  - Whether the stack should decay or be diminishing past some count, instead of
    a hard cap.
  - Whether it should show as one aura of N stacks or one aura with a computed
    magnitude. Stacks are more readable in the buff bar; a computed magnitude
    avoids a 434-stack aura, which no 3.3.5 client UI was built to render.
  - Whether killing a boss while already over the cap should still be recorded,
    so raising the cap later credits work already done. It should.
