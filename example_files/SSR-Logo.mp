% This is the Metapost source for the Logo of the SoundScape Renderer

% $Id: SSR-Logo.mp 424 2008-11-14 11:19:26Z geier.matthias $

% Created June 2008. Design by Fabian Hemmert. MetaPost code by Matthias Geier.

% In ASCII art, it could look something like this:
%                            ___
%                           /  ___
%                       ___/  /  ___
%                         ___/  /    SoundScape Renderer
%                              /
%                      

prologues := 1; % Generate structured PostScript (EPS)
filenametemplate "%j-%c.mps";

vardef drawlogo(expr logocolor) =

drawoptions (withcolor logocolor);

linejoin := mitered;

u := 1cm; % basic unit
linewidth := .15u;
rund := .4u; % size of rounded corners (maximum: u)

%                  z3 ------- z4
%                 /
%                /
%               /
%  z1 ------- z2        z6 ------- z7
%                      /
%                     /
%                    /
%                   z5

z7 - z6 = z6 - z2 = z2 - z1 = z4 - z3 = (u,0);
z3 - z2 = z6 - z5 = (.5u,u);

z1 = origin; % arbitrarily put there

pickup pencircle scaled linewidth;

% define auxiliary circles for the rounded corners
path circle[];
circle2 = fullcircle scaled rund shifted z2;
circle3 = fullcircle scaled rund shifted z3;
circle6 = fullcircle scaled rund shifted z6;

% define the "s" shape
path p;
p = (z1--z2 cutafter circle2) .. (z2--z3 cutbefore circle2 cutafter circle3)
		.. (z3--z4 cutbefore circle3);
% draw the first "s"
draw p;
% draw the second "s"
draw p shifted (u/4,-u/2);
% draw the "r"
draw (z5--z6 cutafter circle 6) .. (z6--z7 cutbefore circle6);

enddef; % vardef drawlogo()

beginfig(1); % this just the logo in black, with transparent background
drawlogo(black);
endfig;

beginfig(2); % this has a non-transparent square background
drawlogo(black); % this is just to get the size, it gets deleted later!
pair ll, ur, ctr;
ll := llcorner currentpicture;
ur := urcorner currentpicture;
ctr := center currentpicture;
currentpicture := nullpicture; % delete everything

width := (xpart ur - xpart ll) * 1.04; % make a few percent larger

color bg;
bg := (237,237,230)/255;
fill unitsquare scaled width shifted (ctr - .5*(width,width)) withcolor bg;
drawlogo(black); % now it's drawn for real ...
endfig;

bye.
