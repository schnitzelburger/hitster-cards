#set page(
  paper: "a4", //210 x 297
  margin: 1.5cm
)

#set text(font: "New Computer Modern")

#let songs = json("songs.json")
#let rows = 4
#let cols = 3

#let back(song) = {
  box(
    height: 5cm,
    width: 5cm,
    stroke: gray,
    inset: 0.25cm,
    stack(
      block(
        height: 1.25cm,
        width: 100%,
        align(
          center + horizon,
          text(
            weight: "regular",
            //for no-wrap of artist names
            song.artists.map(artist => box(artist)).join([, ]),
            size: 8pt
          )
        ),
      ),
      block(
        height: 0.5cm,
        width: 100%,
        align(
          center + horizon,
          text(
            weight: "bold",
            [#song.day.#song.month.],
            size: 10pt
          )
        ),
      ),
      block(
        height: 1cm,
        width: 100%,
        align(
          center + horizon,
          text(
            weight: "black",
            song.year,
            size: 40pt
          )
        ),
      ),
      block(
        height: 1.75cm,
        width: 100%,
        align(center  + horizon, text(weight: "regular", song.name, size: 8pt))

      )

    )
  )
}

#let front(song) = {
  box(
    height: 5cm,
    width: 5cm,
    stroke: gray,
    align(
      center,
      image("qr_codes/" + song.id + ".svg", width: 5cm)
    )
  )
}

#let arrange(songs) = {
  let result = ()

  for page_songs in songs.chunks(rows*cols) {
    let fronts = ()
    let backs = ()

    for song in page_songs {
      fronts.push(front(song))
      backs.push(back(song))
    }

    // Fill remaining slots with empty boxes if needed
    for _ in range(rows*cols - page_songs.len()) {
      fronts.push(box(height: 5cm, width: 5cm))
      backs.push(box(height: 5cm, width: 5cm))
    }

    let back_rows = backs.chunks(cols)
    let reversed_back_rows = back_rows.map(a => a.rev())
    let reversed_backs = reversed_back_rows.flatten()

    result += fronts
    result += reversed_backs
  }

  return result
}

#grid(
  columns: cols,
  column-gutter: 1.5cm,
  row-gutter: 1.5cm,
  ..arrange(songs)
)