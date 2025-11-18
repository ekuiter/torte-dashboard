#import "slides/slides.typ": *
#import "@preview/drafting:0.2.2": *
#set text(lang: "DE")

#let arrowList =  [#hide("  ")#sym.arrow]
#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Tech Stack I", 
  authors: ("Lukas Petermann"),
)
= 3 Implementation 
- Initial Setup
  - ExpressJS + Astro
#set list(marker: ([#text(fill: gray)[•]], [#text(fill: gray)[‣]]))
#text(weight: "extralight", fill:gray)[
 - Second Setup
  - Flask + Svelte

- Third Setup
  // - "Not having to host#linebreak() a server would be#linebreak()  convenient"
  - Serverless, static, and #linebreak() vanilla HTML 
]
#place(horizon+end,dx: 3%, dy:-10%,
 figure(
   rect(radius: 5%,
      image(width:73%,"tech1.png")
    )
  )
)
---
#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Tech Stack II", 
  authors: ("Lukas Petermann"),
)
= 3 Implementation 

#set list(marker: ([#text(fill: gray)[•]], [#text(fill: gray)[‣]]))
#text(weight: "extralight", fill:gray)[
- Initial Setup
  - ExpressJS + Astro
]
#set list(marker: ([•], [‣]))

- Second Setup
  - Flask + Svelte
#set list(marker: ([#text(fill: gray)[•]], [#text(fill: gray)[‣]]))
#text(weight: "extralight", fill:gray)[
- Third Setup
  // - "Not having to host#linebreak() a server would be#linebreak()  convenient"
  - Serverless, static, and #linebreak() vanilla HTML 
] 
#place(horizon+end,dx: 3%, dy:-10%,
rect(radius: 5%, figure(
    image(width:70%,"tech2.png")
  ))
) 
---
#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Tech Stack III", 
  authors: ("Lukas Petermann"),
)
= 3 Implementation 
#set list(marker: ([#text(fill: gray)[•]], [#text(fill: gray)[‣]]))
#text(weight: "extralight", fill:gray)[
- Initial Setup
  - ExpressJS + Astro
- Second Setup
  - Flask + Svelte
]
#set list(marker: ([•], [‣]))
- Third Setup
  // - "Not having to host#linebreak() a server would be#linebreak()  convenient"
  - Serverless, static, and #linebreak() vanilla HTML 
// #image("tech3.5.png")
#place(horizon+end,dx: 3%, dy:-10%,
rect(radius: 5%, figure(
    image(width:70%,"techn3.png")
  ))
)  
---
#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Tech Stack III", 
  authors: ("Lukas Petermann"),
)
= 3 Implementation 
#set list(marker: ([#text(fill: gray)[•]], [#text(fill: gray)[‣]]))
#text(weight: "extralight", fill:gray)[
- Initial Setup
  - ExpressJS + Astro
- Second Setup
  - Flask + Svelte
]
#set list(marker: ([•], [‣]))
- Third Setup
  // - "Not having to host#linebreak() a server would be#linebreak()  convenient"
  - Serverless, static, and #linebreak() vanilla HTML 
// #image("tech3.5.png")
#place(horizon+end,dx: 3%, dy:-10%,
rect(radius: 5%, 
  figure(
    image(width:70%,"tech3.5.png")
  ))
)  
---
#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Final Tech Stack",
  authors: ("Lukas Petermann"),
)
#place(horizon + center, dy:-17%)[
    = Final Iteration #sym.arrow Demo!
    
    #link("https://lupeterm.github.io")
    (also #sub[kind of] works on mobile!)
]

#place(bottom+end, dx:5%,
  image(width:25%,"qrcode.png")
) 

---
// #show: slides.with(
//   [],
//   chapter: "Implementation & Demo",
//   subchapter: "Preprocessing",
//   authors: ("Lukas Petermann"),
// )
// = 3.1 Data & Figure Generation 
// #inline-note[todo: Merge  these two slides and add ablaufdiagramm]
// - Tech used: Python, Plotly, Pandas, json
//   - Extract and polish data according to json config file using pandas
//   - Export figures to html using plotly
//   - Populate JSON file with metrics

// ---

#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Workflow",
  authors: ("Lukas Petermann"),
)
= 3.1 Workflow of Integrating New Data
+ Scientist generates new experiment results with #raw("Torte")
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
2. Scientist modifies `gen_init.json`
3. The script autogenerates all figures and metrics
  - New Figures are saved directly into the frontend sources folder 
  - New Metrics are merged into the pre-existing `init.json`
4. Run local development server 
  1. Review the generated metrics and plots
  2. Repeat from 2., if necessary (e.g. incorrect #raw("gen_init.json"))

5. Publish updated dashboard
#hide("sohfwef")#sym.arrow Share results with the scientific community
]
#place(horizon+end, dy:-5%, dx:3%,
 figure(
    image(height: 100%, "flow1.svg"),
    caption: [Dashboard Extension Workflow]
  )
)
---




#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Workflow",
  authors: ("Lukas Petermann"),
)
= 3.1 Workflow of Integrating New Data
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
1. Scientist generates new experiment results with #raw("Torte")]
#set enum(numbering: n => [#n.])

2. Scientist modifies `gen_init.json`
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
3. The script autogenerates all figures and metrics
  - New Figures are saved directly into the frontend sources folder 
  - New Metrics are merged into the pre-existing `init.json`
4. Run local development server 
  1. Review the generated metrics and plots
  2. Repeat from 2., if necessary (e.g. incorrect #raw("gen_init.json"))

5. Publish updated dashboard
#hide("sohfwef")#sym.arrow Share results with the scientific community
]
#place(horizon+end, dy:-5%, dx:3%,
 figure(
    image(height: 100%, "flow2.svg"),
    caption: [Dashboard Extension Workflow]
  )
)
---



#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Workflow",
  authors: ("Lukas Petermann"),
)
= 3.1 Workflow of Integrating New Data
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
1. Scientist generates new experiment results with #raw("Torte")]
#set enum(numbering: n => [#n.])

2. Scientist modifies `gen_init.json`
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
3. The script autogenerates all figures and metrics
  - New Figures are saved directly into the frontend sources folder 
  - New Metrics are merged into the pre-existing `init.json`
4. Run local development server 
  1. Review the generated metrics and plots
  2. Repeat from 2., if necessary (e.g. incorrect #raw("gen_init.json"))

5. Publish updated dashboard
#hide("sohfwef")#sym.arrow Share results with the scientific community
]
#place(horizon+end, dy:-5%, dx:3%,
 figure(
    image(width: 38%, "before2.png"),
    caption: [Dashboard Extension Workflow]
  )
)
---


#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Workflow",
  authors: ("Lukas Petermann"),
)
= 3.1 Workflow of Integrating New Data
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
1. Scientist generates new experiment results with #raw("Torte")

2. Scientist modifies `gen_init.json`]
#set enum(numbering: n => [#n.])

3. The script autogenerates all figures and metrics
  - New Figures are saved directly into the frontend sources folder 
  - New Metrics are merged into the pre-existing `init.json`
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
4. Run local development server 
  1. Review the generated metrics and plots
  2. Repeat from 2., if necessary (e.g. incorrect #raw("gen_init.json"))

5. Publish updated dashboard
#hide("sohfwef")#sym.arrow Share results with the scientific community
]
#place(horizon+end, dy:-5%, dx:3%,
 figure(
    image(height: 100%, "flow3.svg"),
    caption: [Dashboard Extension Workflow]
  )
)
---
#place(start+top,
[= 3.1.3 Metric Generation from Config]
)
#place(horizon, dy: -5%)[
#grid(
  columns: (5fr,1fr, 1fr, 1fr, 5fr),
  align: (horizon,horizon,horizon,horizon,horizon),
  figure(
    image(width: 120%, "before.png"),
    caption: [Entry in #raw("gen_init.json")]
  ),
  [],
  sym.arrow.long,
  [],
  figure(
    image("after.png"),
    caption: [Generated values in #raw("init.json")]
  )
)
]
---




#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Workflow",
  authors: ("Lukas Petermann"),
)
= 3.1 Workflow of Integrating New Data
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
1. Scientist generates new experiment results with #raw("Torte")

2. Scientist modifies `gen_init.json`
3. The script autogenerates all figures and metrics
  - New Figures are saved directly into the frontend sources folder 
  - New Metrics are merged into the pre-existing `init.json`]
#set enum(numbering: n => [#n.])
  
4. Run local development server 
  1. Review the generated metrics and plots
  2. Repeat from 2., if necessary (e.g. incorrect #raw("gen_init.json"))
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
5. Publish updated dashboard
#hide("sohfwef")#sym.arrow Share results with the scientific community
]
#place(horizon+end, dy:-5%, dx:3%,
 figure(
    image(height: 100%, "flow4.svg"),
    caption: [Dashboard Extension Workflow]
  )
)
---






#show: slides.with(
  [],
  chapter: "Implementation & Demo",
  subchapter: "Workflow",
  authors: ("Lukas Petermann"),
)
= 3.1 Workflow of Integrating New Data
#set enum(numbering: n => text(fill:gray, [#n.]))
#text(weight: "extralight", fill:gray)[
1. Scientist generates new experiment results with #raw("Torte")

2. Scientist modifies `gen_init.json`
3. The script autogenerates all figures and metrics
  - New Figures are saved directly into the frontend sources folder 
  - New Metrics are merged into the pre-existing `init.json`
4. Run local development server 
  1. Review the generated metrics and plots
  2. Repeat from 2., if necessary (e.g. incorrect #raw("gen_init.json"))]
#set enum(numbering: n => [#n.])

5. Publish updated dashboard
#hide("sohfwef")#sym.arrow Share results with the scientific community

#place(horizon+end, dy:-5%, dx:3%,
 figure(
    image(height: 100%, "flow5.svg"),
    caption: [Dashboard Extension Workflow]
  )
)
