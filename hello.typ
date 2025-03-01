#set page(
  paper: "a4", //210 x 297
  margin: 1.5cm
)

#let songs = json("response.json")

#let back(song) = {
  box(
    height: 5cm,
    width: 5cm,
    stroke: gray,
    [#song.name]
  )
}

#grid(
  columns: 3,
  column-gutter: 1.5cm,
  row-gutter: 1.6cm,
  ..for song in songs {
    (back(song),)
  }
)