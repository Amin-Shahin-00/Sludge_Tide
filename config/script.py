"""SLUDGE TIDE - the short film, shot by shot.

Every shot is listed in order with its minimum length, its transition in, the
dialogue spoken during it and named cue points (seconds from the shot start)
that the picture and the sound effects both read.

Dialogue lines are placed one after another: `at` = seconds from the shot start
for the first line (or an absolute position for any line), `gap` = pause after
the previous line ends. Once the voices exist, config/timeline.py stretches any
shot whose dialogue would overrun it, so the edit always fits the performance.

Speakers: NAR narrator, JUNK, IGGY (before the fall), RUST (Baron Rust),
MAGNUS, GRANNY, SELA, PIP, MGR (factory manager), CROWD, BOLT (clicks, subtitled).
"""


def L(who, text, at=None, gap=0.35, sub=True, fx=None, say=None):
    return dict(who=who, text=text, at=at, gap=gap, sub=sub, fx=fx, say=say)


def S(sid, scene, dur, lines=(), cues=None, tin=None, tail=0.6):
    """tin: transition INTO this shot: None (cut), ("dissolve", d), ("black", d), ("white", d)."""
    return dict(id=sid, scene=scene, dur=dur, lines=list(lines), cues=cues or {}, tin=tin, tail=tail)


SHOTS = [
    # ------------------------------------------------------------------ COLD OPEN
    S("o1_drip", "open", 8.0, cues=dict(drip=1.2, hit=2.3, title=2.4, out=7.2)),

    # ------------------------------------------------------------------ 1. THE NIGHT SHIFT
    S("n1_isle", "night", 6.5, [
        L("NAR", "Gloamworks Isle. Three in the morning.", at=0.9),
        L("NAR", "The chimneys are quiet."),
    ], tin=("black", 1.2)),
    S("n2_hall", "night", 10.0, [
        L("NAR", "Nineteen years on the night shift...", at=0.5),
        L("NAR", "and nobody here knows his name.", gap=0.2),
        L("MGR", "Hey, you! You missed a spot.", gap=0.5),
        L("IGGY", "Yes, sir. Sorry, sir.", gap=0.3),
    ], cues=dict(door=7.4), tail=2.6),
    S("n3_vat", "night", 7.0, [
        L("IGGY", "Barrels... for the Graveyard Shelf?", at=2.4, fx="whisper"),
        L("IGGY", "That's where the children dive.", gap=0.5, fx="whisper"),
    ], tin=("dissolve", 0.5)),
    S("n4_phone", "night", 5.0, [
        L("MAGNUS", "Now, now. Let's not do anything silly.", at=2.0),
    ], cues=dict(click=1.3)),
    S("n5_magnus", "night", 5.5, [
        L("MAGNUS", "Mister... uh...", at=1.6),
        L("MAGNUS", "Mister Janitor.", gap=0.7),
    ], cues=dict(puff=0.8)),
    S("n6_frame", "night", 7.0, [
        L("MAGNUS", "You've had a long night. You're confused.", at=0.4),
        L("MAGNUS", "So confused, in fact, that you're the one who caused this terrible spill.", gap=0.3),
        L("IGGY", "I didn't...", gap=0.2),
    ], tail=0.2),
    S("n7_willhave", "night", 4.0, [
        L("MAGNUS", "You will have.", at=0.4),
        L("MAGNUS", "By morning.", gap=0.6),
    ], tail=0.5),
    S("n8_struggle", "night", 3.8, cues=dict(grab=0.25, snap=1.5, slip=2.6)),
    S("n9_fall", "night", 10.5, [
        L("MGR", "Hey, you.", at=3.2, sub=False, fx="echo"),
        L("MGR", "Hey, you!", at=4.0, sub=False, fx="echo"),
        L("MGR", "Hey, YOU.", at=4.7, sub=False, fx="echo"),
    ], cues=dict(letgo=6.4, splash=9.1)),
    S("n10_orange", "night", 7.0, cues=dict(still=0.0, orange=1.6, rust=2.8, crumble=4.0, run=4.6)),
    S("n11_paper", "night", 8.0, [
        L("GRANNY", "Huh.", at=4.6),
        L("GRANNY", "The noodle man.", gap=0.9),
    ], cues=dict(spin=0.0, land=1.4), tin=("white", 0.4), tail=1.0),

    # ------------------------------------------------------------------ 2. THE BLOOM
    S("b1_card", "bloom", 6.0, [
        L("NAR", "Six months later.", at=1.6),
    ], tin=("black", 1.2)),
    S("b2_arm", "bloom", 8.5, [
        L("JUNK", "A WHOLE ROBOT ARM!", at=0.7),
        L("JUNK", "Hello, buddy! Who threw you away? Rude!", gap=0.4),
        L("JUNK", "You're coming home with me.", gap=0.3),
    ], tin=("dissolve", 0.5)),
    S("b3_bolt", "bloom", 5.5, [
        L("BOLT", "*click-click-CLICK* (This is KIDNAPPING!)", at=0.4),
        L("JUNK", "Sorry, Bolt. You're shiny. That's the rule.", gap=0.3),
    ]),
    S("b4_cloud", "bloom", 6.5, [
        L("JUNK", "Huh?", at=4.4),
    ], cues=dict(fish=0.3, crack=2.2)),
    S("b5_pip", "bloom", 5.5, [
        L("PIP", "Aaah! Help!", at=3.3),
    ], cues=dict(fizz=1.0, tip=2.6, splash=3.2)),
    S("b6_dive", "bloom", 3.2, [
        L("JUNK", "Hang on!", at=0.5),
    ], cues=dict(kick=0.3)),
    S("b7_fall", "bloom", 10.5, [
        L("JUNK", "Not today.", at=3.2, fx="inner"),
        L("JUNK", "Nothing's getting thrown away today.", gap=0.7, fx="inner"),
    ], cues=dict(grab=1.2, teal=8.6)),
    S("b8_bubble", "bloom", 6.5, cues=dict(rise=0.4, pop=3.0)),
    S("b9_glow", "bloom", 5.0, [
        L("PIP", "...Your hair is glowing.", at=0.9),
        L("JUNK", "Huh?!", gap=0.4),
    ], tail=1.0),

    # ------------------------------------------------------------------ 3. SCRAP HEART
    S("s1_ceiling", "scrap", 5.0, [
        L("JUNK", "Uh... Granny?", at=2.2),
    ], tin=("black", 0.8)),
    S("s2_bonk", "scrap", 6.5, [
        L("JUNK", "I'm magnetic, Granny! I'm a MAGNET!", at=1.9),
        L("GRANNY", "You're a disaster.", gap=0.4),
    ], cues=dict(bonk=0.7, stick=1.0)),
    S("s3_bikes", "scrap", 4.6, [
        L("JUNK", "Whoa, whoa! Good bikes! Sit!", at=1.8),
    ], cues=dict(pile=3.4)),
    S("s4_bolt", "scrap", 6.0, [
        L("BOLT", "*click... CLICK!* (MINE.)", at=0.5),
    ], cues=dict(grow=1.8, grab=3.6)),
    S("s5_train", "scrap", 8.5, [
        L("JUNK", "Hubcap... HAYMAKER!", at=0.3),
        L("JUNK", "Rocket Clunkers!", at=4.9),
    ], cues=dict(clang1=1.5, clang2=1.75, clang3=2.0, punch=2.6, launch=5.6, crash=7.4)),
    S("s6_tincan", "scrap", 5.0, [
        L("CROWD", "TIN CAN KID!", at=0.5),
        L("JUNK", "Tin Can Kid... I love it!", gap=0.3),
    ]),

    # ------------------------------------------------------------------ 4. BARON RUST
    S("r1_fog", "rust", 6.0, cues=dict(creak=1.0), tin=("black", 1.2)),
    S("r2_collapse", "rust", 4.0, cues=dict(crash=1.6)),
    S("r3_walk", "rust", 7.5, cues=dict(step0=0.6, period=1.15)),
    S("r4_bow", "rust", 9.0, [
        L("RUST", "Good evening, Barnacle Bay.", at=1.0),
        L("RUST", "Please... don't get up.", gap=0.5),
        L("RUST", "You didn't get up for me before.", gap=0.4),
        L("RUST", "You may call me... Baron Rust.", gap=0.7),
    ]),
    S("r5_swarm", "rust", 4.0),
    S("r6_junk", "rust", 4.2, [
        L("JUNK", "Hey! Gas Mask! Those boats are people's homes!", at=0.6),
    ]),
    S("r7_notice", "rust", 5.0, [
        L("RUST", "Oh...", at=1.0),
        L("RUST", "how interesting. You fell into it too.", gap=0.4),
    ]),
    S("r8_fist", "rust", 5.5, [
        L("JUNK", "Hubcap HAYMAKER!", at=0.2),
    ], cues=dict(swing=1.6, touch=2.3, dust=2.7)),
    S("r9_lesson", "rust", 4.6, cues=dict(shield=0.3, rot=0.8, boots=2.0, plant=3.6)),
    S("r10_kneel", "rust", 10.0, [
        L("RUST", "Same poison. Same water.", at=0.8),
        L("RUST", "And it gave you... arts and crafts.", gap=0.5),
        L("RUST", "Everything you build, I can unbuild.", gap=0.6),
        L("RUST", "Everything rots eventually. I'm just being... efficient.", gap=0.5),
    ]),
    S("r11_threat", "rust", 7.0, [
        L("RUST", "Three days.", at=0.6),
        L("RUST", "In three days... I will rot the Stilts.", gap=0.6),
    ], tail=2.4),
    S("r12_boat", "rust", 7.0, tin=("dissolve", 0.8)),

    # ------------------------------------------------------------------ 5. THE TRUTH
    S("t1_bandage", "truth", 9.0, [
        L("GRANNY", "That was Iggy Slate. Quiet fella. Ate my noodles every night on his way home.", at=0.8),
        L("GRANNY", "He never caused that spill. Not in a hundred years.", gap=0.4),
        L("JUNK", "Then who did?", gap=0.5),
    ], tin=("black", 1.0)),
    S("t2_sela", "truth", 8.0, [
        L("SELA", "You're the Tin Can Kid. You're shorter than on the news.", at=1.5),
        L("JUNK", "You're meaner than you look!", gap=0.2),
        L("SELA", "I look extremely mean.", gap=0.4),
    ], cues=dict(drone=0.6), tin=("dissolve", 0.6)),
    S("t3_safe", "truth", 8.0, [
        L("SELA", "Dumping logs. A photo of my father, at the vat.", at=1.6),
        L("SELA", "He did it on purpose. He blamed that man.", gap=0.4),
        L("SELA", "And now he wants to... harvest you.", gap=0.5),
    ], cues=dict(open=0.5, blueprint=None)),
    S("t4_lights", "truth", 5.0, [
        L("MAGNUS", "Sweetheart. You've made a new friend.", at=0.9),
        L("MAGNUS", "How wonderful.", gap=0.3),
    ], cues=dict(lights=0.2)),
    S("t5_escape", "truth", 6.0, [
        L("JUNK", "Hold ON!", at=2.2),
    ], cues=dict(grow=0.2, smash=0.9, build=2.8, land=4.2)),

    # ------------------------------------------------------------------ 6. THREE DAYS
    S("p1_theory", "speech", 8.0, [
        L("SELA", "The sludge locks in whatever you feel the second it swallows you.", at=0.6),
        L("SELA", "He fell in hating everything. You fell in saving everything.", gap=0.3),
        L("SELA", "Same power. Flipped.", gap=0.4),
        L("JUNK", "So I can't beat him.", gap=0.6),
    ], tin=("black", 1.0)),
    S("p2_granny", "speech", 14.0, [
        L("GRANNY", "You know why they call it Tumble Island? Because it falls down all the time.", at=1.4),
        L("GRANNY", "We've rebuilt this place a hundred times.", gap=0.4),
        L("GRANNY", "Rot doesn't win because it's strong, Juno.", gap=0.8),
        L("GRANNY", "Rot wins when people stop fixing things.", gap=0.7),
    ], tin=("dissolve", 1.0), tail=1.2),
    S("p3_faster", "speech", 6.5, [
        L("JUNK", "So I don't have to build something he can't rot...", at=0.4),
        L("JUNK", "I just have to build FASTER than he can rot it!", gap=0.3),
    ], cues=dict(bonk=None), tail=1.6),
    S("p4_stay", "speech", 7.5, [
        L("NAR", "On the third day, nobody left.", at=0.9),
        L("NAR", "They brought everything they had.", gap=0.4),
    ], tin=("dissolve", 0.8)),

    # ------------------------------------------------------------------ 7. ROT VS REBUILD
    S("f1_army", "battle", 6.5, cues=dict(rise=0.5), tin=("black", 1.0)),
    S("f2_why", "battle", 9.0, [
        L("RUST", "You stayed.", at=0.6),
        L("RUST", "Why?", gap=0.5),
        L("JUNK", "Because it's our home.", gap=0.5),
        L("JUNK", "And because you're not trash either... Iggy.", gap=0.4),
    ], tail=2.0),
    S("f3_round1", "battle", 6.0, cues=dict(slam=0.5, crab=3.2)),
    S("f4_blur", "battle", 6.5),
    S("f5_rain", "battle", 5.5, [
        L("RUST", "Oxide... Rain.", at=0.6),
    ]),
    S("f6_titan", "battle", 9.0, [
        L("JUNK", "JUNKYARD... TITAN!", at=5.2),
    ], cues=dict(pull=0.8, slam=5.0, heart=6.4)),
    S("f7_throne", "battle", 7.0, [
        L("RUST", "Ha. Ha, ha, ha.", at=0.4, sub=False),
        L("RUST", "Magnificent. Truly.", gap=0.4),
        L("RUST", "But it's still just junk, child.", gap=0.4),
    ]),
    S("f8_clash", "battle", 5.5, cues=dict(hit1=1.4, hit2=2.6, crack=3.9)),
    S("f9_rig", "battle", 8.0, [
        L("MAGNUS", "Thank you both! You've tired each other out beautifully!", at=3.4, fx="loudspeaker"),
    ], cues=dict(quake=0.2)),
    S("f10_hoses", "battle", 5.0, cues=dict(latch=0.6)),
    S("f11_logs", "battle", 10.0, [
        L("JUNK", "SELA! NOW!", at=0.6),
        L("SELA", "This is Sela Gloam, on every radio in the Archipelago.", gap=0.6, fx="radio"),
        L("SELA", "Magnus Gloam dumped the sludge. He caused the spill.", gap=0.3, fx="radio"),
        L("SELA", "And he blamed an innocent man.", gap=0.3, fx="radio"),
    ], cues=dict(switch=2.0)),
    S("f12_hears", "battle", 6.0, cues=dict(touch=4.6)),
    S("f13_collapse", "battle", 7.0, [
        L("MAGNUS", "No, no, NO!", at=2.4, fx="loudspeaker"),
    ], cues=dict(race=0.0, groan=1.6, fall=3.4, splash=5.0)),
    S("f14_rage", "battle", 6.0, [
        L("RUST", "It doesn't matter! They still laughed! They still forgot me!", at=0.4),
        L("RUST", "EVERYTHING ROTS!", gap=0.3),
    ]),
    S("f15_bowl", "battle", 15.0, [
        L("JUNK", "Granny saved you a bowl.", at=9.4, fx="soft"),
        L("JUNK", "Every night. For six months.", gap=0.9, fx="soft"),
    ], tin=("dissolve", 0.8), tail=0.4),
    S("f16_granny", "battle", 4.5),
    S("f17_fade", "battle", 10.0, [
        L("IGGY", "...Thank you.", at=4.4, fx="whisper"),
    ], cues=dict(flicker=0.6, janitor=2.6, fall=7.0, catch=8.0)),

    # ------------------------------------------------------------------ 8. WHAT ROTS, WHAT STAYS
    S("e1_rebuild", "end", 7.0, [
        L("NAR", "So Tumble Island did what it always does.", at=0.6),
        L("NAR", "It rebuilt.", gap=0.4),
    ], tin=("white", 1.2)),
    S("e2_paper", "end", 5.5, cues=dict(land=1.0), tin=("dissolve", 0.5)),
    S("e3_cell", "end", 9.0, [
        L("RUST", "Thank you for the meal.", at=1.6, fx="soft"),
        L("RUST", "This isn't over, Tin Can Kid.", gap=0.5, fx="soft"),
        L("RUST", "Not until I decide what I am.", gap=0.5, fx="soft"),
    ], tin=("dissolve", 0.6)),
    S("e4_cliff", "end", 10.0, [
        L("SELA", "Think it'll fly?", at=2.4),
        L("JUNK", "Nope.", gap=0.5),
        L("JUNK", "Not yet.", gap=0.6),
        L("JUNK", "It's just waiting.", gap=0.4),
    ], tin=("dissolve", 1.0), tail=2.0),
    S("e5_rattle", "end", 7.0, cues=dict(slurp=3.6), tin=("dissolve", 1.0)),
    S("e6_title", "end", 9.0, tin=("black", 1.0)),
    S("e7_post", "end", 10.0, cues=dict(crack=(3.0, 4.6, 6.0, 7.0)), tin=("black", 1.5)),
]
