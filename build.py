#!/usr/bin/env python3
"""Builds the static rexwalrond.com site into ./docs (served by GitHub Pages).

Run:  python3 build.py            (preview build: noindex on every page)
      python3 build.py --live     (production build: indexable, adds CNAME)
"""
import json
import os
import shutil
import sys

LIVE = "--live" in sys.argv
BASE = "https://rexwalrond.com"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "docs")

NAV = [("Home", ""), ("About", "about/"), ("Blog", "blog/"), ("Portfolio", "portfolio/"),
       ("Resources", "resources/"), ("Contact", "contact/")]

# Rex's other profiles. The old WordPress site linked to these; keeping the links preserves the
# support they give the profiles that hold page-1 spots for his name.
PROFILES = [
    ("LinkedIn", "Work history and education", "https://www.linkedin.com/in/theodore-rex-walrond/"),
    ("theodorewalrond.com", "My site under my full name, Theodore Walrond", "https://theodorewalrond.com/"),
    ("Field notes", "Trip reports, gear and music", "https://rexwalrond.github.io/RexWalrond/"),
    ("Neuroscience &amp; community", "Research and Parkinson's support work", "https://rexwalrond.weebly.com/"),
    ("Issuu", "My biography, resume and trip journals", "https://issuu.com/rexwalrond"),
    ("Issuu: Theodore Walrond", "Research summary, dive notes and the Rainier climb", "https://issuu.com/theodorewalrond"),
    ("Instagram", "@rexwalrond", "https://www.instagram.com/rexwalrond/"),
    ("F6S", "Rex Walrond's F6S profile", "https://www.f6s.com/rex-walrond"),
    ("Creator Spring", "Rex Walrond's Spring page", "https://rexwalrond.creator-spring.com/"),
    ("Jimdo", "Theodore Walrond's Jimdo site", "https://theodore-walrond.jimdosite.com/"),
    ("about.me", "Rex Walrond on about.me", "https://about.me/rexwalrond"),
    ("Muck Rack", "Rex Walrond on Muck Rack", "https://muckrack.com/rex-walrond"),
    ("Crunchbase", "Rex Walrond on Crunchbase", "https://www.crunchbase.com/person/rex-walrond"),
    ("YouTube", "Rex Walrond's channel", "https://www.youtube.com/@RexWalrond"),
]


# Issuu publications, linked one by one so each document gets a direct link.
PUBLICATIONS = [
    ('Rex Walrond Biography', 'Questions and answers: background, research and the outdoors', 'https://issuu.com/rexwalrond/docs/rex_walrond_biography'),
    ('Rex Walrond Resume', 'Research, service, education and certifications', 'https://issuu.com/rexwalrond/docs/the_journey_of_an_aspiring_scientist_navigating_t'),
    ('Tracking COVID-19 Drug Candidates at Romark Laboratories', 'Project summary, summer 2021', 'https://issuu.com/rexwalrond/docs/the_journey_of_an_aspiring_scientist_from_classro'),
    ('Photo Journal: Yosemite and the High Country', 'Photos from the John Muir Trail and beyond', 'https://issuu.com/rexwalrond/docs/the_scientist_s_journey_from_dreams_in_the_classr'),
    ('Ski Log: Seven Mountains From Alta to Telluride', 'Notes from Utah, Colorado and Idaho', 'https://issuu.com/rexwalrond/docs/top_ski_destinations_for_expert_skiers_from_tellu'),
]


def profile_links(items):
    return "".join(f'<a href="{u}" rel="me"><b>{t}</b><span>{d}</span></a>' for t, d, u in items)


PERSON = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Rex Walrond",
    "alternateName": ["Theodore Rex Walrond", "Theodore Walrond"],
    "url": BASE + "/",
    "image": {"@type": "ImageObject", "url": BASE + "/wp-content/uploads/2026/07/Headshot.jpg", "caption": "Rex Walrond", "width": 1200, "height": 1500},
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Florida", "alternateName": "UF", "sameAs": "https://www.ufl.edu/"},
    "homeLocation": {"@type": "Place", "name": "St. Petersburg, Florida",
                     "address": {"@type": "PostalAddress", "addressLocality": "St. Petersburg", "addressRegion": "FL", "addressCountry": "US"}},
    "knowsAbout": ["Behavioral neuroscience", "Cognitive neuroscience", "Healthcare", "Finance", "Scuba diving", "Mountaineering"],
    "sameAs": [u for _, _, u in PROFILES],
}


def page(path, title, description, body, current=None, extra_head="", image="/wp-content/uploads/2026/07/Headshot.jpg"):
    depth = path.count("/")
    root = "../" * depth if depth else "./"
    nav = "".join(
        f'<a href="{root}{href}"{" aria-current=page" if label == current else ""}>{label}</a>'
        for label, href in NAV
    )
    robots = "" if LIVE else '<meta name="robots" content="noindex,nofollow">\n'
    canonical = BASE + "/" + path
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{robots}<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2313202b'/%3E%3Cpath d='M10 48 L26 24 L34 34 L42 20 L54 48 Z' fill='%23d9893b'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css">
{extra_head}</head>
<body>
<header class="site-head"><div class="wrap"><a class="brand" href="{root}">Rex Walrond</a><nav class="nav">{nav}</nav></div></header>
<main>
{body.replace("{root}", root)}
</main>
<footer class="site-foot"><div class="wrap"><span>&copy; 2026 Rex Walrond</span><span><a href="https://www.linkedin.com/in/theodore-rex-walrond/">LinkedIn</a> &middot; <a href="{root}university-of-florida/">At UF</a> &middot; <a href="https://rexwalrond.github.io/RexWalrond/">Field notes</a> &middot; <a href="https://rexwalrond.weebly.com/">Research &amp; community</a> &middot; <a href="https://theodorewalrond.com/">theodorewalrond.com</a></span></div></footer>
</body>
</html>
"""
    dest = os.path.join(OUT, path, "index.html") if path.endswith("/") or path == "" else os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj) + "</script>\n"


TOPO = """<svg class="topo" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="#c9bfae" stroke-width="1">
<path d="M-50 520 C 150 470, 260 560, 420 500 S 700 380, 860 430 S 1100 520, 1260 470"/><path d="M-50 480 C 160 420, 270 510, 430 450 S 700 330, 870 380 S 1100 470, 1260 420"/>
<path d="M-50 440 C 170 370, 290 460, 445 400 S 705 280, 880 330 S 1110 420, 1260 370"/><path d="M-50 400 C 180 320, 310 410, 460 350 S 710 230, 890 280 S 1120 370, 1260 320"/>
<path d="M-50 360 C 190 270, 330 360, 475 300 S 715 180, 900 230 S 1130 320, 1260 270"/><path d="M-50 320 C 200 220, 350 310, 490 250 S 720 130, 910 180 S 1140 270, 1260 220"/>
<path d="M-50 280 C 210 170, 370 260, 505 200 S 725 80, 920 130 S 1150 220, 1260 170"/><path d="M-50 600 C 140 560, 250 640, 410 590 S 690 480, 850 520 S 1090 610, 1260 560"/>
</g></svg>"""

PEAKS = """<svg viewBox="0 0 1200 380" preserveAspectRatio="xMidYMax meet" role="img" aria-label="Elevation profile of Rex Walrond's trips: Four Pass Loop 12,500 ft (2019), Mount Rainier 14,411 ft (2020), John Muir Trail 9,926 ft (2021), Teton Crest 10,720 ft (2022), Glacier National Park 7,470 ft (2023), Onion Valley to Whitney Portal 13,600 ft (2025)">
<defs><linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f5d7c"/><stop offset="1" stop-color="#1c3a50"/></linearGradient><linearGradient id="back" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fb3c9"/><stop offset="1" stop-color="#b9cfdc"/></linearGradient></defs>
<path d="M0 380 L0 300 L80 260 L170 290 L260 230 L360 280 L470 220 L560 270 L660 240 L760 285 L860 235 L960 275 L1060 245 L1200 280 L1200 380 Z" fill="url(#back)" opacity=".55"/>
<path d="M40 380 L150 143 L260 380 Z" fill="url(#snow)"/><path d="M150 143 L128 190 L142 182 L150 195 L160 180 L172 190 Z" fill="#f6f3ee"/>
<path d="M200 380 L340 110 L480 380 Z" fill="url(#snow)"/><path d="M340 110 L312 165 L328 156 L340 172 L352 154 L368 165 Z" fill="#f6f3ee"/>
<path d="M420 380 L520 188 L620 380 Z" fill="url(#snow)"/>
<path d="M570 380 L680 174 L790 380 Z" fill="url(#snow)"/><path d="M680 174 L662 210 L674 204 L680 214 L688 203 L698 210 Z" fill="#f6f3ee"/>
<path d="M740 380 L840 230 L940 380 Z" fill="url(#snow)"/>
<path d="M880 380 L1020 124 L1160 380 Z" fill="url(#snow)"/><path d="M1020 124 L994 172 L1009 164 L1020 180 L1031 163 L1046 172 Z" fill="#f6f3ee"/>
<g text-anchor="middle">
<text class="peak-label" x="150" y="118">12,500 FT</text><text class="peak-name" x="150" y="100">Four Pass Loop</text><text class="peak-meta" x="150" y="84">Maroon Bells &#183; 2019</text>
<text class="peak-label" x="340" y="85">14,411 FT</text><text class="peak-name" x="340" y="67">Mount Rainier</text><text class="peak-meta" x="340" y="51">Summit &#183; 2020</text>
<text class="peak-label" x="520" y="163">9,926 FT</text><text class="peak-name" x="520" y="145">John Muir Trail</text><text class="peak-meta" x="520" y="129">Yosemite &#183; 2021</text>
<text class="peak-label" x="680" y="149">10,720 FT</text><text class="peak-name" x="680" y="131">Teton Crest</text><text class="peak-meta" x="680" y="115">Grand Teton &#183; 2022</text>
<text class="peak-label" x="840" y="205">7,470 FT</text><text class="peak-name" x="840" y="187">Boulder Pass</text><text class="peak-meta" x="840" y="171">Glacier NP &#183; 2023</text>
<text class="peak-label" x="1020" y="99">13,600 FT</text><text class="peak-name" x="1020" y="81">Onion Valley to Whitney Portal</text><text class="peak-meta" x="1020" y="65">High Sierra &#183; 2025</text>
</g></svg>"""

POSTS = [
    {
        "slug": "blog/brain-bleeds-and-alzheimers-the-question-behind-my-research/",
        "title": "Brain Bleeds and Alzheimer's: The Question Behind My Research",
        "date": "2026-10-17", "date_text": "October 2026", "tag": "Research",
        "summary": "A plain-language look at the question I worked on at UF's McKnight Brain Institute: whether a subarachnoid hemorrhage can raise the risk of Alzheimer's disease years later.",
        "image": None,
        "body": """
<p>From 2022 to 2023 I worked on a project at the University of Florida's McKnight Brain Institute that came down to one question: does a subarachnoid hemorrhage make a person more likely to develop Alzheimer's disease later in life? My part was the evidence. I read and analyzed more than 300 studies and helped organize them into a framework the team could use to decide what to test next. This post is the plain-language version of what that question involves. It's a summary for general readers, not medical advice.</p>
<h2>What a subarachnoid hemorrhage is</h2>
<p>The brain sits inside thin layers of tissue, and between two of those layers is a space filled with cerebrospinal fluid: the subarachnoid space. A subarachnoid hemorrhage is bleeding into that space. When it isn't caused by a head injury, the usual culprit is a ruptured aneurysm, a weak, ballooning spot in an artery. It's a medical emergency, often announced by a sudden, severe headache.</p>
<h2>Why anyone connects it to Alzheimer's</h2>
<p>Many people who survive a subarachnoid hemorrhage recover well on paper but still notice lasting problems with memory, attention or processing speed. Alzheimer's disease, meanwhile, is defined by two kinds of protein buildup in the brain, amyloid plaques and tau tangles, along with the loss of nerve cells. The research question is whether the injury from a bleed nudges the brain toward that Alzheimer's process, or whether it causes a different kind of damage that only looks similar from the outside.</p>
<h2>The possible links researchers study</h2>
<ul>
<li><strong>Blood where it doesn't belong.</strong> As blood breaks down, it releases hemoglobin and iron, which can damage cells through oxidative stress.</li>
<li><strong>Inflammation that lingers.</strong> The brain's immune response to a bleed doesn't always switch off neatly, and long-running inflammation is also part of the Alzheimer's story.</li>
<li><strong>Clearance.</strong> The brain flushes out waste, including amyloid, partly through the movement of cerebrospinal fluid. Animal studies suggest blood in the subarachnoid space can slow that flow.</li>
<li><strong>The blood vessels themselves.</strong> Vascular injury and reduced blood flow are risk factors for cognitive decline in their own right.</li>
</ul>
<p>Each of these is a hypothesis that researchers are testing, not a settled answer.</p>
<h2>Why the evidence is hard to pin down</h2>
<p>Going through hundreds of papers made one thing clear: the studies don't line up neatly. Some use animal models and some follow patients. Some measure memory with cognitive tests, some look at biomarkers and some count dementia diagnoses. Follow-up periods are often short compared with how slowly Alzheimer's develops. And the same factors that raise the risk of an aneurysm, such as high blood pressure and smoking, also raise the risk of cognitive decline, which makes cause and effect hard to separate.</p>
<h2>What I took away</h2>
<p>A single study rarely settles a question like this. What helps is laying many studies side by side and seeing where they agree, where they conflict and where nobody has looked yet. Those gaps are what point to the next experiment. It's also the habit I've carried out of the lab: organize the evidence before deciding what it means.</p>
<p>More on my time at UF is on the <a href="{root}university-of-florida/">University of Florida page</a>, and a longer summary of my research experience is <a href="https://issuu.com/theodorewalrond/docs/the_journey_of_an_aspiring_scientist_from_classro">on Issuu</a>.</p>
""",
    },
    {
        "slug": "blog/onion-valley-to-whitney-portal/",
        "title": "Onion Valley to Whitney Portal: 50 Miles of High Sierra",
        "date": "2025-08-15", "date_text": "August 2025", "tag": "Backpacking",
        "summary": "Kearsarge Pass, Forester Pass and the climb to Trail Crest: the most sustained time at altitude of any trip I've done.",
        "image": None,
        "body": """
<p>In August 2025 I backpacked about fifty miles of the High Sierra, starting at the Onion Valley trailhead and finishing at Whitney Portal. Of every trip on my list, it's the one that kept me at altitude the longest.</p>
<h2>The route</h2>
<ul>
<li><strong>Onion Valley over Kearsarge Pass:</strong> the way in, climbing out of the Owens Valley side to join the John Muir Trail.</li>
<li><strong>South on the John Muir Trail:</strong> including Forester Pass, one of the highest passes on the trail.</li>
<li><strong>Trail Crest at about 13,600 feet:</strong> a long switchback climb, then the descent to Whitney Portal.</li>
</ul>
<p>The totals come out to roughly 50 miles and 12,000 feet of elevation gain. Those are published route figures, not GPS numbers, but they're close enough to plan around.</p>
<h2>What made it hard</h2>
<p>Altitude was the story of the whole trip. Most backpacking routes climb to a pass and drop back down. This one stays high for days, with multiple passes over 13,000 feet. Everything takes more effort when the air is that thin, from the climbs themselves to sleeping and eating well enough to recover.</p>
<p>The other challenge was carrying enough. There are long stretches between resupply points in this part of the Sierra, so the pack is heaviest exactly when the trail is highest.</p>
<h2>What I'd tell someone planning it</h2>
<ul>
<li><strong>Respect the altitude.</strong> Build in time to acclimatize, and plan your days around how you'll feel at 12,000 feet, not at sea level.</li>
<li><strong>Plan food and water carefully.</strong> Weight matters more than usual when every climb is above treeline.</li>
<li><strong>Sort out permits early.</strong> Popular High Sierra trailheads and the Whitney area are permit-controlled.</li>
</ul>
<p>It's the trip I'd point to if someone asked what the High Sierra is really like. Shorter trip notes for this route and others are in my <a href="https://rexwalrond.github.io/RexWalrond/trips.html">field notes</a>.</p>
""",
    },
    {
        "slug": "blog/half-dome-and-clouds-rest-john-muir-trail/",
        "title": "Half Dome and Clouds Rest on the John Muir Trail",
        "date": "2021-06-20", "date_text": "June 2021", "tag": "Backpacking",
        "summary": "Several days south from Tuolumne on the John Muir Trail, with detours up Half Dome's cables and along the granite spine of Clouds Rest.",
        "image": ("rex-walrond-yosemite-granite-dome.jpg", "Rex Walrond on top of Half Dome in Yosemite National Park, 2021"),
        "body": """
<p>In June 2021 I spent several days backpacking south out of Tuolumne Meadows on the John Muir Trail through Yosemite National Park. The route itself is beautiful, but the two side trips are what made it worth doing: Half Dome and Clouds Rest.</p>
{figure}
<h2>Half Dome</h2>
<p>Half Dome is the one everyone knows: the cables, the line of hikers waiting their turn, and the famous view from the top. The cable route goes up steep, exposed granite, and a permit is required. Standing on top is as good as the photos suggest.</p>
<h2>Clouds Rest</h2>
<p>Clouds Rest gets less attention, and I think it has the better view. The summit is a long granite spine you walk the length of, with Yosemite Valley falling away on both sides. At 9,926 feet it was the high point of the trip.</p>
<h2>The numbers</h2>
<p>All in, the trip covered about 40 miles with roughly 7,500 feet of elevation gain, using published route figures.</p>
<h2>What I took away</h2>
<p>This was the trip where I learned how much the side trips can define a route. The main trail gets you through the park; the detours are what you remember. It also confirmed that I'd rather do a little more planning to fit in the hard extras than skip them.</p>
<p>More of my trips, with routes and conditions, are in my <a href="https://rexwalrond.github.io/RexWalrond/trips.html">field notes</a>.</p>
""",
    },
]


# Old WordPress URLs -> closest new page, so links pointing at the retired posts still count.
REDIRECTS = {"rex-walrond-note-dame-m-s-in-finance-candidate/": "/", "privacy-policy/": "/contact/", "category/blog/": "/blog/"}
for slug in ["unlock-your-skiing-potential-advanced-techniques", "exploring-the-thrills-of-backcountry-skiing-a-guide-to-adventure-and-freedom",
             "scaling-peaks-the-thrill-and-challenge-of-mountain-climbing", "mastering-advanced-skiing-techniques",
             "start-backcountry-skiing-basics", "elevating-your-skiing-skills-expert-techniques-for-advanced-skiers"]:
    REDIRECTS[slug + "/"] = "/blog/"
for slug in ["the-journey-of-an-aspiring-scientist-from-classroom-to-research-lab", "the-journey-of-an-aspiring-scientist-from-classroom-to-research-lab-2",
             "from-classroom-to-research-lab-a-guide-to-becoming-a-scientist", "how-academic-research-prepares-you-for-real-world-challenges",
             "inside-romark-laboratories-partnering-with-industry-leaders-to-shape-the-future-of-pharmaceuticals",
             "scientific-discovery-from-classroom-to-cutting-edge-research"]:
    REDIRECTS[slug + "/"] = "/portfolio/"
for slug in ["conquer-stem-challenges-strategies-for-academic-success", "navigating-the-complex-world-of-stem-education",
             "personal-journey-from-high-school-student-to-scuba-dive-master"]:
    REDIRECTS[slug + "/"] = "/about/"


def redirect(path, target):
    dest = os.path.join(OUT, path, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Moved</title>
<link rel="canonical" href="{BASE}{target}">
<meta http-equiv="refresh" content="0; url={target}">
</head><body><p>This page has moved: <a href="{target}">{BASE}{target}</a></p></body></html>
""")


def post_card(p, root):
    img = (f'<img src="{root}images/{p["image"][0]}" alt="{p["image"][1]}" loading="lazy">'
           if p["image"] else '<div class="thumb"></div>')
    return (f'<a class="post-card" href="{root}{p["slug"]}">{img}<div class="body"><div class="mono">{p["tag"]} &#183; {p["date_text"]}</div>'
            f'<h3>{p["title"]}</h3><p>{p["summary"]}</p></div></a>')


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copy(os.path.join(HERE, "src", "style.css"), OUT)
    shutil.copytree(os.path.join(HERE, "src", "images"), os.path.join(OUT, "images"))
    # Real photos kept at their old WordPress URLs (GPS stripped) so existing image-search entries stay valid.
    shutil.copytree(os.path.join(HERE, "src", "wp-content"), os.path.join(OUT, "wp-content"))

    # ---------------- Home
    cards = "".join(post_card(p, "{root}") for p in POSTS)
    home = f"""
<section class="hero">{TOPO}
  <div class="wrap hero-grid">
    <div>
      <div class="mono">Neuroscience &#183; Healthcare &#183; Finance &#183; Higher elevations</div>
      <h1>Rex<br><span>Walrond</span></h1>
      <p class="lede">Neuroscience grad turned builder in St. Petersburg, Florida, usually happiest somewhere above treeline or below the surface.</p>
      <div class="cta"><a class="btn btn-solid" href="{{root}}about/">More about me &#8594;</a><a class="btn btn-ghost" href="https://rexwalrond.github.io/RexWalrond/trips.html">Field notes</a></div>
    </div>
    <div class="portrait">
      <img src="{{root}}wp-content/uploads/2026/07/Headshot.jpg" alt="Rex Walrond, University of Florida neuroscience graduate" width="1200" height="1500">
      <div class="tag"><span class="dot"></span><div><b>14,411 ft</b><small>Mount Rainier summit</small></div></div>
    </div>
  </div>
</section>

<section class="dark sec">
  <div class="wrap two-col">
    <div><div class="mono">Hi, I'm Rex</div><h2 style="margin-top:12px;font-size:clamp(30px,3.6vw,44px)">Curious about how the brain works, how healthcare gets built, and what's over the next pass.</h2></div>
    <div>
      <p>I'm <strong>Theodore Rex Walrond</strong>, though almost everyone calls me Rex. I studied behavioral and cognitive neuroscience at the <strong><a href="{{root}}university-of-florida/">University of Florida</a></strong>, where I got hooked on research: working through hundreds of studies on how brain bleeds relate to Alzheimer's disease, and tracking COVID-19 drug candidates during the pandemic.</p>
      <p>From there I moved toward the business side of healthcare and completed graduate coursework in finance at the <strong>University of Notre Dame</strong>. Today I'm focused on building an early-stage venture in consumer health.</p>
      <p>Home base is St. Petersburg, on Tampa Bay. When I'm not working, I'm usually planning the next trip, out on the water, or over-analyzing my sleep data.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head"><div><div class="mono">The path so far</div><h2>A few chapters</h2></div><p>Not a resume, just the parts that shaped how I think.</p></div>
    <div class="cards">
      <article class="card"><div class="mono">The lab years</div><h3>Brains, bleeds &amp; a pandemic pipeline</h3><p>At UF's McKnight Brain Institute I synthesized 300+ studies on links between subarachnoid hemorrhage and Alzheimer's. Before that, a summer at Romark Laboratories building dashboards for 25+ COVID-19 drug candidates.</p><div class="when mono">2021 &#8211; 2023</div></article>
      <article class="card"><div class="mono">Giving back</div><h3>Parkinson's support, one session at a time</h3><p>As an Impact Partner with the American Parkinson Disease Association, I led a monthly support group of 15&#8211;20 people: planning sessions, bringing in guest speakers, and presenting.</p><div class="when mono">2025 &#8211; 2026</div></article>
      <article class="card now"><div class="mono">Right now</div><h3>Building something in consumer health</h3><p>I'm putting my research background and finance training to work on an early-stage consumer health venture. More to share down the road.</p><div class="when mono">Today</div></article>
    </div>
  </div>
</section>

<section class="peaks">
  <div class="wrap"><div class="sec-head"><div><div class="mono">High points</div><h2>Ground covered</h2></div><p>The trips that matter most to me, drawn to scale by high point. Full trip reports live in my <a href="https://rexwalrond.github.io/RexWalrond/trips.html">field notes</a>.</p></div></div>
  {PEAKS}
  <div class="wrap peaks-list">
    <div><span>Mount Rainier &#183; 2020</span><span class="mono">14,411 ft</span></div><div><span>Onion Valley to Whitney Portal &#183; 2025</span><span class="mono">13,600 ft</span></div>
    <div><span>Four Pass Loop &#183; 2019</span><span class="mono">12,500 ft</span></div><div><span>Teton Crest &#183; 2022</span><span class="mono">10,720 ft</span></div>
    <div><span>John Muir Trail &#183; 2021</span><span class="mono">9,926 ft</span></div><div><span>Boulder Pass, Glacier NP &#183; 2023</span><span class="mono">7,470 ft</span></div>
  </div>
</section>

<section class="sec">
  <div class="wrap photos">
    <figure><img src="{{root}}images/rex-walrond-yosemite-granite-dome.jpg" alt="Rex Walrond on top of Half Dome in Yosemite National Park" loading="lazy" width="1200" height="1600"><figcaption>Rex Walrond on top of Half Dome, Yosemite National Park, 2021.</figcaption></figure>
    <figure><img src="{{root}}images/rex-walrond-skiing.jpg" alt="Rex Walrond skiing in Telluride, Colorado" loading="lazy" width="739" height="1162"><figcaption>Rex Walrond skiing in Telluride, Colorado.</figcaption></figure>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:56px;align-items:start">
    <div><div class="mono">Below the surface</div><h2 style="font-size:clamp(30px,3.6vw,42px);margin:10px 0 18px">Divemaster, University of Florida Scientific Diving</h2>
      <p class="muted">From 2020 to 2023 I helped teach scuba courses for UF's Scientific Diving Program, from Open Water through Master Diver: in-water skills, out-of-water skills, and classroom lectures on dive planning, physics and physiology. Most of my diving has been in Florida's freshwater springs.</p>
      <div class="mono" style="margin-top:6px">SDI Divemaster &#183; Rescue Diver &#183; Master Scuba Diver</div></div>
    <div><div class="mono">Off the clock</div><h2 style="font-size:clamp(30px,3.6vw,42px);margin:10px 0 22px">Things I'll happily talk your ear off about</h2>
      <div class="chips"><span class="chip">Mountaineering</span><span class="chip">Backpacking</span><span class="chip">Skiing</span><span class="chip">Scuba</span><span class="chip">Golf</span><span class="chip">Acoustic guitar</span><span class="chip">Zach Bryan deep cuts</span><span class="chip">Over-engineered sleep tracking</span></div></div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><div class="mono">Writing</div><h2>From the blog</h2></div><a class="btn btn-ghost" href="{{root}}blog/">All posts</a></div>
    <div class="posts">{cards}</div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><div class="mono">Elsewhere online</div><h2>Find Rex Walrond elsewhere</h2></div><p>Profiles, publications and my second site, theodorewalrond.com.</p></div>
    <div class="elsewhere">{profile_links(PROFILES)}</div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap"><div class="close"><h2>Planning a trip, or just want to say hello?</h2><div class="cta" style="margin-top:0"><a class="btn btn-solid" href="{{root}}contact/">Get in touch</a><a class="btn btn-ghost" href="https://www.linkedin.com/in/theodore-rex-walrond/">LinkedIn</a></div></div></div>
</section>
"""
    page("", "Rex Walrond | UF Neuroscience Graduate, St. Petersburg, Florida",
         "Rex Walrond is a University of Florida neuroscience graduate in St. Petersburg, FL, with brain and drug research experience, now starting a consumer health company.",
         home, "Home", jsonld(PERSON))

    # ---------------- About
    about = """
<div class="wrap narrow">
  <div class="page-head"><div class="mono">About</div><h1>About Rex Walrond</h1>
  <p>Theodore Rex Walrond, who goes by Rex, is a University of Florida neuroscience graduate based in St. Petersburg, Florida, whose work has moved from the research lab toward healthcare and finance. He is currently building an early-stage venture in consumer health.</p></div>
  <div class="prose">
    <figure><img src="{root}images/rex-walrond-portrait.jpg" alt="Rex Walrond in a navy blazer and open-collar shirt" style="max-width:320px;border-radius:18px" width="960" height="1200"><figcaption>Rex Walrond, St. Petersburg, Florida.</figcaption></figure>
    <h2>Education</h2>
    <p><strong><a href="{root}university-of-florida/">University of Florida</a></strong>: B.S. in Psychology, Behavioral and Cognitive Neuroscience, cum laude (2025)<br><strong>University of Notre Dame</strong>: completed graduate coursework in finance</p>
    <h2>Research background</h2>
    <h3>McKnight Brain Institute, University of Florida</h3>
    <p class="muted">Neuroscience Researcher, 2022&#8211;2023</p>
    <p>Rex conducted literature reviews and statistical analyses across more than 300 studies on subarachnoid hemorrhage and Alzheimer's disease. He developed an analytical framework identifying variables that link vascular trauma to neurodegeneration, helping the team prioritize future experiments, and presented findings to faculty and researchers across three departments.</p>
    <h3>Romark Laboratories</h3>
    <p class="muted">Research Assistant, Summer 2021</p>
    <p>Rex built Excel dashboards tracking more than 25 COVID-19 drug candidates by efficacy, trial phase and mechanism, and synthesized over 400 articles and multi-drug datasets to evaluate the antiviral potential of niclosamide.</p>
    <h2>Service</h2>
    <h3>American Parkinson Disease Association</h3>
    <p class="muted">Impact Partner, 2025&#8211;2026</p>
    <p>Rex led a monthly Parkinson's disease support group of 15 to 20 participants, planning and running each session, coordinating guest speakers, facilitating caregiver-focused conversations and reporting on APDA outreach.</p>
    <h3>University of Florida Scientific Diving Program</h3>
    <p class="muted">Divemaster, 2020&#8211;2023</p>
    <p>Rex helped teach scuba courses from Open Water through Master Diver, covering in-water and out-of-water skills and classroom lectures on dive planning, dive physics and physiology, for more than 30 students across the program's certification courses. He holds SDI certifications through Divemaster.</p>
    <h2>Outside of work</h2>
    <figure><img src="{root}wp-content/uploads/2025/03/rex-walrond-receives-cum-laude-honor-upon-graduation-768x1024.jpg" alt="Rex Walrond below the Half Dome cables in Yosemite National Park" style="max-width:360px;border-radius:18px" width="768" height="1024" loading="lazy"><figcaption>Rex Walrond below the Half Dome cables, Yosemite National Park, June 2021.</figcaption></figure>
    <p>Rex spends as much time as he can at higher elevations or below the surface: mountaineering, backpacking, skiing and diving. He has summited Mount Rainier and covered long stretches of the John Muir Trail, the Teton Crest Trail and Glacier National Park's backcountry. He also plays golf and acoustic guitar, and tracks his training, nutrition and sleep data more closely than strictly necessary. Trip reports, gear notes and an ever-changing ranking of Zach Bryan's discography live on his <a href="https://rexwalrond.github.io/RexWalrond/">personal site</a>.</p>
    <p><a href="https://www.linkedin.com/in/theodore-rex-walrond/">LinkedIn</a> &#183; <a href="{root}contact/">Contact</a></p>
  </div>
</div>
<div style="height:72px"></div>
"""
    page("about/", "About Rex Walrond | University of Florida Neuroscience Graduate",
         "About Rex Walrond: St. Petersburg-based UF neuroscience graduate, former McKnight Brain Institute and Romark researcher, APDA volunteer and SDI Divemaster.",
         about, "About", jsonld(PERSON), image="/images/rex-walrond-portrait.jpg")

    # ---------------- University of Florida (targets "rex walrond uf", where every result used to be negative)
    uf = """
<div class="wrap narrow">
  <div class="page-head"><div class="mono">University of Florida</div><h1>Rex Walrond at the University of Florida</h1>
  <p>Rex Walrond (Theodore Rex Walrond) is a University of Florida graduate. At UF he studied behavioral and cognitive neuroscience, worked on research at the McKnight Brain Institute and from 2020 to 2023 helped teach scuba for the university's Scientific Diving Program.</p></div>
  <div class="prose">
    <p><strong>Degree:</strong> B.S. in Psychology, Behavioral and Cognitive Neuroscience, cum laude<br><strong>Research:</strong> McKnight Brain Institute, 2022&#8211;2023<br><strong>Diving:</strong> UF Scientific Diving Program, divemaster and teaching assistant, 2020&#8211;2023<br><strong>Today:</strong> St. Petersburg, Florida</p>
    <h2>The degree</h2>
    <p>Rex Walrond earned a Bachelor of Science in Psychology from UF with a concentration in behavioral and cognitive neuroscience, graduating cum laude. The concentration sits where psychology meets biology: how the brain produces behavior, memory, attention and emotion, and how injury or disease changes them. It was the coursework that got him interested in research.</p>
    <h2>Research at the McKnight Brain Institute</h2>
    <p>From 2022 to 2023 Walrond worked on a research project at UF's McKnight Brain Institute, which focuses on brain health and cognitive aging. The project asked whether a subarachnoid hemorrhage, bleeding into the space around the brain, can leave a person more vulnerable to Alzheimer's disease later in life. He conducted literature reviews and statistical analyses across more than 300 studies, helped build a framework of the variables that appear to link vascular injury to neurodegeneration, and presented the findings to faculty and researchers across three departments.</p>
    <h2>Teaching scuba with UF Scientific Diving</h2>
    <p>From 2020 to 2023 he was a divemaster and teaching assistant for the University of Florida's Scientific Diving Program. He helped run courses from Open Water through Master Diver for more than 30 students, covering in-water skills, out-of-water skills and classroom sessions on dive planning, dive physics and physiology. Much of that diving took place in Florida's freshwater springs. He holds SDI certifications through Divemaster.</p>
    <h2>After UF</h2>
    <p>After graduating, Walrond completed graduate coursework in finance at the University of Notre Dame and volunteered as an Impact Partner with the American Parkinson Disease Association. He now lives in St. Petersburg, Florida, where he is building an early-stage venture in consumer health.</p>
    <h2>Further reading</h2>
    <p><a href="{root}about/">About Rex Walrond</a> &#183; <a href="https://issuu.com/theodorewalrond/docs/the_journey_of_an_aspiring_scientist_from_classro">Research experience in neuroscience and drug development</a> &#183; <a href="https://issuu.com/rexwalrond/docs/the_journey_of_an_aspiring_scientist_navigating_t">Resume</a> &#183; <a href="https://www.linkedin.com/in/theodore-rex-walrond/">LinkedIn</a></p>
  </div>
</div>
<div style="height:72px"></div>
"""
    page("university-of-florida/", "Rex Walrond at UF | Neuroscience, Research &amp; Scientific Diving",
         "Rex Walrond's years at the University of Florida (UF): a cum laude neuroscience degree, research at the McKnight Brain Institute and teaching scuba with UF Scientific Diving.",
         uf, None, jsonld(PERSON))

    # ---------------- Portfolio
    portfolio = """
<div class="wrap">
  <div class="page-head narrow"><div class="mono">Portfolio</div><h1>Selected work</h1><p>Research, service and the outdoors: the projects Rex Walrond is proudest of.</p></div>
  <div class="cards">
    <article class="card"><div class="mono">Research &#183; 2022&#8211;2023</div><h3>Subarachnoid hemorrhage &amp; Alzheimer's</h3><p>Evidence synthesis across 300+ studies at UF's McKnight Brain Institute, and a framework the team used to prioritize experiments.</p></article>
    <article class="card"><div class="mono">Research &#183; 2021</div><h3>COVID-19 drug candidate tracking</h3><p>Dashboards covering 25+ candidates by efficacy, trial phase and mechanism at Romark Laboratories.</p></article>
    <article class="card"><div class="mono">Service &#183; 2025&#8211;2026</div><h3>Parkinson's support group</h3><p>Monthly sessions for 15&#8211;20 participants with the American Parkinson Disease Association. <a href="https://rexwalrond.weebly.com/blog/what-leading-a-parkinsons-support-group-taught-me">What it taught me</a>.</p></article>
    <article class="card"><div class="mono">Teaching &#183; 2020&#8211;2023</div><h3>Scientific diving instruction</h3><p>Divemaster for UF's Scientific Diving Program, Open Water through Master Diver.</p></article>
    <article class="card"><div class="mono">Outdoors &#183; 2019&#8211;now</div><h3>Field notes</h3><p>Trip reports from the Four Pass Loop to a Mount Rainier summit and fifty miles of High Sierra. <a href="https://rexwalrond.github.io/RexWalrond/trips.html">Read them</a>.</p></article>
    <article class="card"><div class="mono">Writing</div><h3>Blog</h3><p>Longer write-ups of trips and lessons learned. <a href="{root}blog/">See all posts</a>.</p></article>
  </div>
</div>
<div style="height:88px"></div>
"""
    page("portfolio/", "Portfolio | Rex Walrond",
         "Selected work by Rex Walrond: neuroscience research synthesis, COVID-19 drug candidate tracking, Parkinson's support group leadership and scientific diving instruction.",
         portfolio, "Portfolio")

    # ---------------- Blog index + posts
    entries = "".join(post_card(p, "{root}") for p in sorted(POSTS, key=lambda p: p["date"], reverse=True))
    page("blog/", "Blog | Rex Walrond", "Trip reports and lessons learned from Rex Walrond.",
         f'<div class="wrap"><div class="page-head narrow"><div class="mono">Blog</div><h1>Writing</h1><p>Trip reports and lessons learned.</p></div><div class="posts">{entries}</div></div><div style="height:88px"></div>',
         "Blog")
    for p in POSTS:
        fig = (f'<figure><img src="{{root}}images/{p["image"][0]}" alt="{p["image"][1]}" width="1200" height="1600" style="border-radius:18px"><figcaption>{p["image"][1]}.</figcaption></figure>'
               if p["image"] else "")
        body = p["body"].replace("{figure}", fig)
        art = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"],
               "author": {"@type": "Person", "name": "Rex Walrond", "url": BASE + "/"}, "mainEntityOfPage": BASE + "/" + p["slug"]}
        if p["image"]:
            art["image"] = BASE + "/images/" + p["image"][0]
        html = (f'<div class="wrap narrow"><div class="page-head"><div class="mono">{p["tag"]} &#183; {p["date_text"]}</div><h1>{p["title"]}</h1>'
                f'<p>By Rex Walrond</p></div><article class="prose">{body}</article>'
                f'<p style="margin-top:40px"><a href="{{root}}blog/">&#8592; All posts</a></p></div><div style="height:72px"></div>')
        page(p["slug"], f'{p["title"]} | Rex Walrond', p["summary"].replace('"', "&quot;"), html, "Blog", jsonld(art),
             image=("/images/" + p["image"][0]) if p["image"] else "/wp-content/uploads/2026/07/Headshot.jpg")

    # ---------------- Resources
    articles = [
        ("Theodore Rex Walrond Explores Subarachnoid Hemorrhages and Alzheimer's Research", "The American Reporter", "2024", "https://www.theamericanreporter.com/theodore-rex-walrond-explores-subarachnoid-hemorrhages-and-alzheimers-research/"),
        ("Theodore Rex Walrond: Inside the Internship at Romark and Its Role in Pharmaceutical Research", "Disrupt Magazine", "2024", "https://disruptmagazine.com/theodore-rex-walrond-inside-the-internship-at-romark-and-its-role-in-pharmaceutical-research/"),
        ("Cognitive Neuroscience: Theodore Walrond's Passion and Work", "Kivo Daily", "2024", "https://kivodaily.com/lifestyle/cognitive-neuroscience-theodore-walronds-passion-and-work/"),
        ("Exploring the Outdoors with Theodore Walrond: Hiking, Climbing, and More", "Travel Daily News", "2024", "https://www.traveldailynews.com/column/featured-articles/exploring-the-outdoors-with-theodore-walrond-hiking-climbing-and-more/"),
        ("Theodore Walrond's Guide to Safe and Enjoyable SCUBA Diving", "South Florida Reporter", "2024", "https://southfloridareporter.com/theodore-walronds-guide-to-safe-and-enjoyable-scuba-diving/"),
        ("How Psychological Research Translates into Pharmaceutical Innovations", "MedicalResearch.com", "2025", "https://medicalresearch.com/how-psychological-research-translates-into-pharmaceutical-innovations/"),
        ("Theodore Rex Walrond Highlights the Connection between Cognitive Psychology and Healthcare", "Health Works Collective", "2025", "https://www.healthworkscollective.com/theodore-rex-walrond-highlights-the-connection-between-cognitive-psychology-and-healthcare/"),
        ("Theodore Rex Walrond Discusses How Data Analysis Powers Breakthroughs in Medical Research", "Let's Be Game Changers", "2025", "https://letsbegamechangers.com/blog/theodore-rex-walrond-discusses-how-data-analysis-powers-breakthroughs-in-medical-research/"),
        ("Theodore Rex Walrond: The Impact of Research Internships on Career Development in Science", "HHM Global", "2025", "https://www.hhmglobal.com/health-wellness/theodore-rex-walrond-the-impact-of-research-internships-on-career-development-in-science"),
        ("Theodore Rex Walrond: How Cognitive Neuroscience Explains Learning and Memory Formation", "MediTech Today", "2025", "https://meditechtoday.com/cognitive-neuroscience-learning-memory-formation/"),
    ]
    art_html = "".join(f'<a href="{u}" rel="noopener"><b>{t}</b><span>{pub} &#183; {y}</span></a>' for t, pub, y, u in articles)
    prof_html = profile_links(PROFILES)
    resources = f"""
<div class="wrap narrow">
  <div class="page-head"><div class="mono">Resources</div><h1>Articles &amp; links</h1><p>Articles featuring Theodore Rex Walrond, and where to find him elsewhere online.</p></div>
  <h2 style="font-size:28px;margin:12px 0 8px">Featured articles</h2>
  <div class="list">{art_html}</div>
  <h2 style="font-size:28px;margin:44px 0 8px">Publications on Issuu</h2>
  <div class="list">{profile_links(PUBLICATIONS)}</div>
  <h2 style="font-size:28px;margin:44px 0 8px">Profiles</h2>
  <div class="list">{prof_html}</div>
</div>
<div style="height:88px"></div>
"""
    page("resources/", "Resources | Rex Walrond", "Articles featuring Theodore Rex Walrond, plus links to his profiles and personal site.", resources, "Resources")

    # ---------------- Contact
    contact = """
<div class="wrap narrow">
  <div class="page-head"><div class="mono">Contact</div><h1>Get in touch with Rex Walrond</h1><p>The best way to reach me is by email or LinkedIn.</p></div>
  <div class="cta"><a class="btn btn-solid" href="mailto:rexwalrond@gmail.com">Email me</a><a class="btn btn-ghost" href="https://www.linkedin.com/in/theodore-rex-walrond/">LinkedIn</a></div>
</div>
<div style="height:120px"></div>
"""
    page("contact/", "Contact | Rex Walrond", "Get in touch with Rex Walrond by email or LinkedIn.", contact, "Contact")

    # ---------------- 404 (GitHub Pages serves /404.html; use absolute links)
    page("404.html", "Page not found | Rex Walrond", "This page doesn't exist.",
         '<div class="wrap narrow"><div class="page-head"><div class="mono">404</div><h1>Page not found</h1><p>That page has moved or no longer exists.</p></div><div class="cta"><a class="btn btn-solid" href="/">Go to the home page</a><a class="btn btn-ghost" href="/blog/">Read the blog</a></div></div><div style="height:120px"></div>')

    # ---------------- Redirects for retired WordPress URLs
    for old, new in REDIRECTS.items():
        redirect(old, new)

    # ---------------- robots, sitemap, CNAME
    urls = ["", "about/", "university-of-florida/", "blog/", "portfolio/", "resources/", "contact/"] + [p["slug"] for p in POSTS]
    updated = {"": "2026-10-17", "about/": "2026-10-17", "university-of-florida/": "2026-10-17", "resources/": "2026-10-17", "blog/": "2026-10-17", "blog/brain-bleeds-and-alzheimers-the-question-behind-my-research/": "2026-10-17"}
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')
        # Image entries help Google Images associate each real photo with the page and the name.
        page_images = {"": ["/wp-content/uploads/2026/07/Headshot.jpg", "/images/rex-walrond-yosemite-granite-dome.jpg", "/images/rex-walrond-skiing.jpg"],
                       "about/": ["/images/rex-walrond-portrait.jpg", "/wp-content/uploads/2025/03/rex-walrond-receives-cum-laude-honor-upon-graduation-768x1024.jpg"]}
        for p in POSTS:
            if p["image"]:
                page_images[p["slug"]] = ["/images/" + p["image"][0]]
        for u in urls:
            imgs = "".join(f"<image:image><image:loc>{BASE}{i}</image:loc></image:image>" for i in page_images.get(u, []))
            f.write(f"  <url><loc>{BASE}/{u}</loc><lastmod>{updated.get(u, '2026-10-15')}</lastmod>{imgs}</url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n" if LIVE else "User-agent: *\nDisallow: /\n")
    if LIVE:
        with open(os.path.join(OUT, "CNAME"), "w") as f:
            f.write("rexwalrond.com\n")
        # Google Search Console ownership file (keep it, or the property loses verification).
        with open(os.path.join(OUT, "google489e379d499b3d8e.html"), "w") as f:
            f.write("google-site-verification: google489e379d499b3d8e.html")
    with open(os.path.join(OUT, ".nojekyll"), "w") as f:
        f.write("")
    print("built", "LIVE" if LIVE else "PREVIEW", "->", OUT)


if __name__ == "__main__":
    build()
