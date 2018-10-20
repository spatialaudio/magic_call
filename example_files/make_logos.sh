#!/bin/sh

# two logos are generated, one with just the logo and another one with a square
# background

n=SSR-Logo

# run MetaPost to generate the PostScript (EPS) versions
mpost $n

# rename them to something more meaningful
mv $n-1.mps $n.mps
mv $n-2.mps $n-square.mps

CONVERT="convert -density 1000"

# just add other widths in pixels if you want other sizes, too
for SIZE in 310 ; do
$CONVERT -resize $SIZE $n.mps $n-$SIZE.png
done

for SIZE in 64; do
# we don't want an alpha channel in this case!
$CONVERT -resize ${SIZE}x$SIZE -alpha off $n-square.mps $n-square-$SIZE.png
done

rm $n.log
