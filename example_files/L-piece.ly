#(define usep '())
#(define buildp '()) 
#(define ((schoenberg-accidentals clear) music)
  (let* ((es (ly:music-property music 'elements))
         (e (ly:music-property music 'element))
         (p  (ly:music-property music 'pitch))
         (ts  (ly:music-property music 'types)))

    (if (memq 'note-event ts) 
	(begin
	  (set! buildp (cons p buildp))
	  (if (not (member p usep))
	      (ly:music-set-property! music 'force-accidental #t))))

    (if (ly:music? e)
        (ly:music-set-property!
         music 'element
         ((schoenberg-accidentals clear) e)))

    (if (pair? es)
        (ly:music-set-property!
         music 'elements
         (map (schoenberg-accidentals (memq 'sequential-music ts)) es)))

    (if clear (begin (set! usep buildp) (set! buildp '())))

    music))

\version "2.4.5"

\header {
  title = "Grundmelodie für das L-Stück"
  composer = "Matthias Geier"
}
\include "deutsch.ly"

#(set-global-staff-size 13)

Grundmelodie =  \relative c' {
  \set Score.timing = ##f
  \override Staff.TimeSignature #'break-visibility = #all-invisible
  \clef violin
  c4 << {\times 2/3 {b'8 a b} h2} \\ {es,8( b) as4 ges8( fes)} >>
    \bar "||"
}

\layout {
  indent = 0\mm % erste Zeile nicht einrücken
  raggedright = ##t
}


\score {
  \applymusic #(schoenberg-accidentals #t) {
    \set Score.autoAccidentals = ##f
    \set Score.TimeSignature = ##f
      \Grundmelodie
  }
  \header {
    piece = Grundmelodie
%    opus = Test
  }
}
