#import "slides/slides.typ": *
#import "@preview/drafting:0.2.2": *
#set text(lang: "DE")

#let arrowList =  [#hide("  ")#sym.arrow]
#show: titleSlide.with(
  [],
  authors: ("Lukas Petermann"),
  date: datetime.today() // konkretes Datum mit: datetime(year: 2025, month: 01, day: 22)
)

/* ------------------------ */
#place(horizon + center, dy:-17%)[
    = Final Presentation:
    =
    = "A Dashboard for Evolving Variability in Configurable System Software"
]
---
#show: slides.with(
  [],
  chapter: "Introduction",
  authors: ("Lukas Petermann"),
)
= 1 Introduction

- Software systems evolve constantly
  - Configurability is often expected or required
  
- Especially interesting: *System software*
  - Safety and security: System software is the connecting link#linebreak() between hardware and software
  - Flexibility: Virtually countless combinations of hardware#linebreak() and software #sym.arrow Variability
- System software is often developed in product lines (SPL)
  - Related products that share the same core but otherwise differ in functionality
  - Effective and systematic development, variability management
// #inline-note[graph zeigen (evolution), was ist variability]
#place(top+end, dy:-18%, dx:5%)[
  #figure(
    image(width:32%, "evol.png"),
  caption: [\#Configurations of the Linux kernel @elias]
    
  )
]
---
#show: slides.with(
  [],
  chapter: "Introduction",
  subchapter: "Feature Models",
  authors: ("Lukas Petermann"),
)
- This variability of SPLs can be modeled via *feature models*
  - Describe valid configurations of an SPL by modeling features and dependencies
  
- System software variability is often described in DSLs like *KConfig*
  - No direct mapping between KConfig and SPL feature model
  - But: features can be extracted and analyzed automatically
#place(bottom+center)[  
  #figure(
    caption: [Example feature model for a vending machine product line @splexample],
    image("figures/spl.png", width: 75%)
)
]
---
#show: slides.with(
  [],
  chapter: "Introduction",
  subchapter: "Feature Models",
  authors: ("Lukas Petermann"),
)
- This variability of SPLs can be modeled via *feature models*
  - Describe valid configurations of an SPL by modeling features and dependencies
  
- System software variability is often described in DSLs like *KConfig*
  - No direct mapping between KConfig and SPL feature model
  - But: features can be extracted and analyzed automatically
#place(bottom+center)[  
  #figure(
    caption: [Excerpt of the bluetooth driver KConfig],
    image("kconfig.png", width: 58%)
)
]
--- 
#show: slides.with(
  [],
  chapter: "Introduction",
  subchapter: "Automated Analysis",
  authors: ("Lukas Petermann"),
)
- Automated system software product line analysis
  - Feature model *analysis* #sym.arrow Analysis of configuration space, i.e., feature model semantics
  
  - Feature model *evolution* #sym.arrow Analysis of configuration history, i.e., feature model evolution over time 
  
- Evolution is especially interesting:
  - Iterative development, open source #sym.arrow Development history is available
  
  - Usage in various settings #sym.arrow All revisions are interesting, not just the most recent
- Papers have been published with static tables and figures @elias,@thumAbstractFeaturesFeature2011,@niekeAnomalyAnalysesFeaturemodel2020,@lotufoEvolutionLinuxKernel2010
- Tools like Torte#footnote[https://github.com/ekuiter/torte] can automatically extract and analyze features 

#place(bottom+end, dy:-0%)[
_If only there was a way to better communicate these experiment results..._
]
---
#show: slides.with(
  [],
  chapter: "Concept",
  authors: ("Lukas Petermann"),
)
#place(top+end, dy:-15%, dx:5%)[
#figure(
  image("selection.png", width: 50%),
  caption: [Torte dashboard concept]
)
]
= 2 Torte Dashboard

- *Goal*: Visualization of current state & historical evolution
  - Choice of system software project and metric
  - Interactive plot illustrates growth over time and per revision 
  
- *Vision:* Support for researchers:
  - Interactive plots add additional information (to static tables)
  // example plots from paper where he had to extract stuff and zoom
  - Reference dashboard from publication for more information
  // - Multiple dimensions can be shown simultaneously
  - Room for more plots than in publication due to page limit
  - Other researchers can create their own dashboards
  - Easily extendable with new projects and metrics

---
#show: slides.with(
  [],
  chapter: "Concept",
  subchapter: "Projects & Metrics",
  authors: ("Lukas Petermann"),
)
// #inline-note[
// characteristiken des dashboards ansehen und begründen warum die gut sind etc
// ggf benennen (analog zu RQ.x)
// ]
= 2.1 Projects & Metrics


#quote[_what you dont measure, you cannot control_]

- All metrics relate different projects in terms of size, complexity and variability
- Quantitative metrics give insight on system complexity
  - Lines of code, \#Features, \#Configurations
  
- Computation times hint at necessary effort of analysis
  - For instance, the Linux kernel has grown too complex to analyze

- Differentiate between Linux and non-Linux projects

#place(bottom+end, dx:5%)[
  #figure(
    image(width:29%, "evol.png"),
  caption: [\#Configurations of the Linux kernel @elias]
    
  )
]
// - current value -> numerical
// - historical -> graph
//     #inline-note("konkrete beispiele, figures, zb torte exp")
//   - Problems:
//     1. Where does the data come from?
//       // - preprocessing scripts that automatically extract required data from #raw("Torte") experiments
//       // - also pre-generates static figures
//     2. The experimental results may differ between projects, (Linux vs Non-Linux)

// - Linux can choose either a specific architecture or an aggregation for the whole kernel
// #inline-note("is linux really the only project with diff. between arch? if so, why?")

// ---
//   #show: slides.with(
//   [],
//   chapter: "Implementation",
//   subchapter: "Technology Stack",
//   authors: ("Lukas Petermann"),
// )
// = 3 Implementation
// - Sticking to the theme of iterative development..
// #inline-note("merge lessons learned into this")
// - Final Setup:
//   - Dev: Vuetify+Nuxt (Node development server)
//   - "Prod": use Static Site Generation (SSG) to generate Static HTML 
//     - Hostable on github pages
//     - permalink via hash mode
--- 
#include "implementation.typ"
#show: figureSlide.with(
  [],
  chapter: "Conclusion",
  authors: ("Lukas Petermann"),
)
#place(center+top,dy: 5%,
 figure(
    image(width:110%,"segway.png")
  ))
// ) )
---
#show: slides.with(
  [],
  chapter: "Conclusion",
  authors: ("Lukas Petermann"),
)
= 4 Conclusion
#align(center)[
  #table(
    columns: (auto, auto),
    align: (left, left),
    inset: 10pt,
    table.header(
      table.cell(align: left)[*Stakeholder*],
      table.cell(align: left)[*Benefit of a Scientific Dashboard*],
    ),
    "Scientists", [
      \+ Quick insight on metric evolution and current state#linebreak()  
      \+ Easy Comparison between projects and extractors#linebreak()
      \+ Supplementary to publications
    ],
    "Maintainer", [
      \+ Same benefits as above!#linebreak()
      \+ Automatic extraction of data & figure generation#linebreak()
  ],
    "Developer" , [\+ Valuable lessons learned]
  )
]
#place(center+bottom, dy:-7%)[*Thanks for listening!*]
---
#bibliography("bibliography/refs.bib")
