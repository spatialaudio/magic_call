% METAPOST source file for circular loudspeaker array at T-Labs, Berlin
% Matthias Geier, November 2007

prologues := 2; % Generate structured PostScript (EPS)
filenametemplate "%j.eps";

beginfig(1);

m  := 4cm;  % one meter is drawn as this length
r1 := 1.675m; % outer radius (175 mm more than inner radius)
r2 := 1.5m; % inner radius
r3 := r2;   % radius where loudspeakers are aligned on
a  := 0.15; % scaling factor for "perspective" view
t  := .02m; % thickness of the boards
height := .24m; % total height of ring

number_of_boxes := 56;
box_height := .12m;
box_width  := .09m;
box_space  := .002m; % space below box

color box_color; box_color := .8white;
color ring_color; ring_color = .9white;
color box_color; box_color := white;
color ring_color; ring_color = white;

path p[];
% lower half circle
p1 = halfcircle scaled 2r1 yscaled a;
% upper half circle
p2 = p1 shifted (0,height);
% lower inner half circle
p3 = halfcircle scaled 2r2 yscaled a;
% upper inner circle
p4 = p3 yscaled -1 shifted (0,height);
% and other half

% invisible lines for construction of loudspeaker boxes
p5 = halfcircle scaled 2r3 yscaled -a shifted (0,t+box_space);
p6 = p5 shifted (0,box_height);
p7 = fullcircle scaled 2r3 shifted (0,-r3-a*r1-height);

% first of all, draw the loudspeakers, they are clipped later
for i = 0 upto (number_of_boxes/2):
  save start, x; % make variables local (begingroup/endroup needed?)
  start = (arclength p7)*i/number_of_boxes;
  x1 = xpart(point (arctime start of p7) of p7);
  x2 = xpart(point (arctime start+box_width of p7) of p7);
  path ls;
  ls = buildcycle(p5,(x1,-infinity)--(x1,infinity),p6,
		  (x2,-infinity)--(x2,infinity));
  fill ls withcolor box_color;
  draw ls;
%  draw buildcycle(p5,point (arctime start of p7) of p7--(0,infinity),p6,
%		  point (arctime start+box_width of p7) of p7--(0,infinity));
endfor;

clip currentpicture to buildcycle(p3,reverse p3 yscaled -1 shifted (0,t));
picture loudspeakers;
loudspeakers := currentpicture;
% tabula rasa
currentpicture := nullpicture;

% fill background before drawing anything
fill p1 yscaled -1--reverse p2--cycle withcolor ring_color;
unfill buildcycle(p3,reverse p4); % leave the "eye" unfilled

%draw p5 withcolor red;
%draw p6 withcolor red;
%drawarrow p7  shifted (0,r1) withcolor red;

% the edge visible inside the ring
draw halfcircle scaled 2(r1-t) yscaled -a shifted (0,height-t)
		cutbefore p3 cutafter p3;

draw loudspeakers;

% now start drawing the circular frame

% near end of lower and upper outer circle (incl. vertical lines)
draw p1--reverse p2--cycle;
% far end of lower circle
draw p1 yscaled -1;

draw p3--reverse p3 yscaled -1--cycle; % lower inner circle
draw p3 yscaled -1 shifted (0,t) cutbefore p3 cutafter p3;

draw p4 cutbefore p3 cutafter p3; % visible part of upper inner circle
draw p4 shifted (0,-t) cutbefore p3 cutafter p3;

endfig;
end.
