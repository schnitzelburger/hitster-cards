#let songs = json("songs.json")

//this is a4
#let page_width = 210mm
#let page_height = 297mm

#let margin_x = 2cm
#let margin_y = 1cm

#let rows = 11
#let cols = 8
#let card_size = 2cm

#let marking_padding = 1cm

#assert(rows * card_size + 2 * marking_padding + margin_y <= page_height)
#assert(cols * card_size + 2 * marking_padding + margin_x <= page_width)

#set page(
  width: page_width,
  height: page_height,
  margin: (
    x: margin_x,
    y: margin_y
  )
)

#set text(font: "New Computer Modern")

#set square(
  stroke: none
)

#let qr_front_side(song) = {
  square(
    size: card_size,
    image(
      "qr_codes/" + song.id + ".svg",
      width: 100%
    )
  )
}

#let text_back_side(song) = {
  square(
    size: card_size,
    inset: 0.05 * card_size,
    stack(
      block(
        height: 0.25 * card_size,
        width: 100%,
        align(
          center + horizon,
          text(
            //for no-wrap of artist names
            song.artists.map(artist => box(artist)).join([, ]),
            size: 0.06 * card_size
          )
        ),
      ),
      block(
        height: 0.1 * card_size,
        width: 100%,
        align(
          center + horizon,
          text(
            [#song.day.#song.month.],
            size: 0.07 * card_size
          )
        ),
      ),
      block(
        height: 0.2 * card_size,
        width: 100%,
        align(
          center + horizon,
          text(
            weight: "black",
            song.year,
            size: 0.28 * card_size
          )
        ),
      ),
      block(
        height: 0.35 * card_size,
        width: 100%,
        align(
          center  + horizon,
          text(
            [_ #song.name _],
            size: 0.06 * card_size
          )
        )
      )
    )
  )
}

#let marking_line = line(
  stroke: (
    paint: black,
    thickness: 0.5pt
  ),
  length: marking_padding / 2
)

//a rotatable box with cut markings
#let marking(angle) = {
  rotate(
    angle,
    reflow: true,
    box(
      width: marking_padding,
      height: card_size,
      stack(
        spacing: card_size,
        ..(marking_line,) * 2
      )
    )
  )
}

//a row of markings
#let marking_row(angle) = {
  (
    square(
      size: marking_padding,
    ),
    ..(marking(angle),) * cols,
    square(
      size: marking_padding,
    ),
  )
}


#let arrange(songs) = {
  let result = ()

  //add test and qr codes
  for page_songs in songs.chunks(rows*cols) {
    let fronts = ()
    let backs = ()

    for song in page_songs {
      fronts.push(qr_front_side(song))
      backs.push(text_back_side(song))
    }

    //fill remaining slots with empty boxes if needed
    for _ in range(rows * cols - page_songs.len()) {
      fronts.push(
        square(
          size: card_size
        )
      )
      backs.push(
        square(
          size: card_size
        )
      )
    }

    //reverse back side
    let back_rows = backs.chunks(cols)
    let reversed_back_rows = back_rows.map(row => row.rev())
    let reversed_backs = reversed_back_rows.flatten()

    result += fronts
    result += reversed_backs
  }

  //add cut marks on the sides
  let page_rows = result.chunks(cols)
  let x_padded_rows = page_rows.map(
    row => (
      marking(0deg),
      ..row,
      marking(180deg)
    )
  )
  result = x_padded_rows.flatten()

  //add top and bottom marks
  let pages = result.chunks(rows * (cols + 2))
  let y_padded_pages = pages.map(
    page => (
      marking_row(90deg),
      ..page,
      marking_row(270deg)
    )
  )
  result = y_padded_pages.flatten()

  return result
}

#for page in arrange(songs).chunks((rows + 2) * (cols + 2)) {
  grid(
    columns: cols + 2,
    ..page
  )
  pagebreak()
}
