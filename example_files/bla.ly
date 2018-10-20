\version "2.18.0"

\header {
  title = "Grundmelodie für das L-Stück"
  composer = "Matthias Geier"
}
\include "deutsch.ly"

#(set-global-staff-size 13)

Grundmelodie =  \relative c' {
  \set Score.timing = ##f
  \override Staff.TimeSignature.break-visibility = #all-invisible
  \clef violin
  c4 << {\tuplet 3/2 {b'8 a b} h2} \\ {es,8( b) as4 ges8( fes)} >>
    \bar "||"
}

\layout {
  indent = 0\mm % erste Zeile nicht einrücken
  ragged-right = ##t
}


\score {
  \Grundmelodie
  \header {
    piece = Grundmelodie
%    opus = Test
  }
}
