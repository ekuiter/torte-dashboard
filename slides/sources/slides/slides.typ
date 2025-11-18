#let titleSlide(
  title,
  authors: (),
  date: datetime.today(),
  body
) = {
  set text(font: "New Computer Modern Sans", 16pt)
  set page(
    paper: "presentation-16-9", 
    margin: (top: 3.5cm, rest: 1.5cm),
   header: [
      #align(horizon)[
        #context pad(
          x: -page.margin.left, 
          line(length: 100%, stroke: rgb("0069b4") + 2.5pt)
        )
      ]
      #place(top, dx: -1cm, dy: 0.5cm, 
        image("/slides/fin.svg", width: 50%)
      )
     
      
    ],
    footer: context {
      align(bottom, pad(x: -page.margin.left, rect(width: 100%, height: 1.5cm, fill: rgb("0069b4"))[
        #set align(horizon)
        #set text(white, 13pt)
        #grid(columns: (1fr, auto, 1fr), align: (left, center, right), inset: 0.5em,hide("hi"),
[          #authors,
          #date.display("[day].[month].[year]")],
        )
      ]))
    },
    footer-descent: 0em
  )
  
  set enum(indent: 1em)
  set list(indent: 1em)
  set cite(style: "ieee")
  set bibliography(title: "References")
  
  show cite: set text(luma(75))
  show regex("^" + sym.dash.em + "$"): pagebreak()
  show heading.where(level: 1): set text(20pt)
  show heading.where(level: 1): set block(spacing: 1em)
  show heading.where(level: 2): set block(spacing: 1em)
  show heading.where(level: 2): set text(0.9em)
  
  set enum(numbering: (..n) => text(luma(75), numbering("1.", ..n)))

  show figure.where(kind: image): set figure(supplement: "Fig.")
  show figure.caption: c => context [
    *#c.supplement #c.counter.display()#c.separator*#c.body
  ]

  body
}


#let slides(
  title,
  chapter: (),
  subchapter: "",
  authors: (),
  date: datetime.today(),
  body
) = {
  set text(font: "New Computer Modern Sans", 16pt)
  set page(
    paper: "presentation-16-9", 
    margin: (top: 3.5cm,bottom: 1.6cm, rest: 1.5cm),
    header: [
      #align(horizon)[
        #context pad(
          x: -page.margin.left, 
          line(length: 100%, stroke: rgb("0069b4") + 2.5pt)
        )
      ]
      #place(top, dx: -1cm, dy: 0.5cm, 
        image("/slides/fin.svg", width: 50%)
      )
      #place(top+end, dy:0.7cm,dx: 1cm,authors)
      
    ],
    footer: context {
      align(bottom, pad(x: -page.margin.left, rect(width: 100%, height: 1.2cm, fill: rgb("0069b4"))[
        #set align(top)
        #set text(white, 13pt)
        #let chapterText = (a) => if a == chapter {stack(spacing: 23%,underline(text(a, weight: "bold")), if subchapter != ""{[#sym.arrow #subchapter]})} else {text(a, weight: "thin")}
        #grid(columns: 5, gutter: 1fr, inset: 0em,
          chapterText("Introduction"),
          chapterText("Concept"),
          chapterText("Implementation & Demo"),
          chapterText("Conclusion"),
          counter(page).display()
        )
      ]))
    },
    footer-descent: 0em
  )
  
  set enum(indent: 1em)
  set list(indent: 1em)
  set cite(style: "ieee")
  set bibliography(title: "References")
  
  show cite: set text(luma(75))
  show regex("^" + sym.dash.em + "$"): pagebreak()
  show heading.where(level: 1): set text(20pt)
  show heading.where(level: 1): set block(spacing: 1em)
  show heading.where(level: 2): set block(spacing: 1em)
  show heading.where(level: 2): set text(0.9em)
  
  set enum(numbering: (..n) => text(luma(75), numbering("1.", ..n)))

  show figure.where(kind: image): set figure(supplement: "Fig.")
  show figure.caption: c => context [
    *#c.supplement #c.counter.display()#c.separator*#c.body
  ]
  body
}


#let figureSlide(
  title,
  chapter: (),
  subchapter: "",
  authors: (),
  date: datetime.today(),
  body
) = {
  set text(font: "New Computer Modern Sans", 16pt)
  set page(
    paper: "presentation-16-9", 
    margin: (top: 0cm,bottom: 1.6cm, rest: 1.5cm),
    header: [
    ],
    footer: context {
      align(bottom, pad(x: -page.margin.left, rect(width: 100%, height: 1.2cm, fill: rgb("0069b4"))[
        #set align(top)
        #set text(white, 13pt)
        #let chapterText = (a) => if a == chapter {stack(spacing: 23%,underline(text(a, weight: "bold")), if subchapter != ""{[#sym.arrow #subchapter]})} else {text(a, weight: "thin")}
        #grid(columns: 5, gutter: 1fr, inset: 0em,
          chapterText("Introduction"),
          chapterText("Concept"),
          chapterText("Implementation & Demo"),
          chapterText("Conclusion"),
          counter(page).display()
        )
      ]))
    },
    footer-descent: 0em
  )
  
  set enum(indent: 1em)
  set list(indent: 1em)
  set cite(style: "ieee")
  set bibliography(title: "References")
  
  show cite: set text(luma(75))
  show regex("^" + sym.dash.em + "$"): pagebreak()
  show heading.where(level: 1): set text(20pt)
  show heading.where(level: 1): set block(spacing: 1em)
  show heading.where(level: 2): set block(spacing: 1em)
  show heading.where(level: 2): set text(0.9em)
  
  set enum(numbering: (..n) => text(luma(75), numbering("1.", ..n)))

  show figure.where(kind: image): set figure(supplement: "Fig.")
  show figure.caption: c => context [
    #move(dy: -5%,
 [   *#c.supplement #c.counter.display()#c.separator*#c.body]
    )
      
  ]
  body
}



#let appendix(
  title,
  chapter: (),
  subchapter: "",
  authors: (),
  date: datetime.today(),
  body
) = {
  set text(font: "New Computer Modern Sans", 16pt)
  set page(
    paper: "presentation-16-9", 
    margin: (top: 3.5cm,bottom: 1.6cm, rest: 1.5cm),
    header: [
      #align(horizon)[
        #context pad(
          x: -page.margin.left, 
          line(length: 100%, stroke: rgb("0069b4") + 2.5pt)
        )
      ]
      #place(top, dx: -1cm, dy: 0.5cm, 
        image("/slides/fin.svg", width: 50%)
      )
      #place(top+end, dy:0.7cm,dx: 1cm,authors)
      
    ],
    footer: context {
      align(bottom, pad(x: -page.margin.left, rect(width: 100%, height: 1.2cm, fill: rgb("0069b4"))[
        #set align(top)
        #set text(white, 13pt)
        #let chapterText = (a) => if a == chapter {stack(spacing: 23%,underline(text(a, weight: "bold")), if subchapter != ""{[#sym.arrow #subchapter]})} else {text(a, weight: "thin")}
        #grid(columns: 3, gutter: 1fr, inset: 0em,
        [],
          chapterText("Appendix"),
          counter(page).display()
        )
      ]))
    },
    footer-descent: 0em
  )
  
  set enum(indent: 1em)
  set list(indent: 1em)
  set cite(style: "ieee")
  set bibliography(title: "References")
  
  show cite: set text(luma(75))
  show regex("^" + sym.dash.em + "$"): pagebreak()
  show heading.where(level: 1): set text(20pt)
  show heading.where(level: 1): set block(spacing: 1em)
  show heading.where(level: 2): set block(spacing: 1em)
  show heading.where(level: 2): set text(0.9em)
  
  set enum(numbering: (..n) => text(luma(75), numbering("1.", ..n)))

  show figure.where(kind: image): set figure(supplement: "Fig.")
  show figure.caption: c => context [
    *#c.supplement #c.counter.display()#c.separator*#c.body
  ]
  body
}