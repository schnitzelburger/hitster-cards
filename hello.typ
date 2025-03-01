#set page(
  paper: "a4",
  margin: 2cm
)

#let songs = json.decode(sys.inputs.data)



#let back(song) = {
  box(
    height: 7.5cm,
    width: 7.5cm,
    fill: gray,
    [#song.name]
  )
}

#grid(
  columns: 2,
  column-gutter: 2cm,
  row-gutter: 1.6cm,
  ..for song in songs {
    (back(song),)
  }
)