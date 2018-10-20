prologues := 2; % make EPS

beginfig(1);

u := 4mm; % basic unit
linewidth := .15u;
rund := .4u; % size of rounded edges (maximum: u)

%                  z3 ------- z4
%                 /
%                /
%               /
%  z1 ------- z2        z6 ------- z7
%                      /
%                     /
%                    /
%                   z5

y1 = y2 = y6 = y7;
y3 = y4;
x7 - x6 = x6 - x2 = x2 - x1 = u;
z2 + (.5u,u) = z3;
x3 + u = x4;
z5 + (.5u,u) = z6;

z1 = origin; % arbitrarily put there

pickup pencircle scaled linewidth;

path circle[];
circle2 = fullcircle scaled rund shifted z2;
circle3 = fullcircle scaled rund shifted z3;
circle6 = fullcircle scaled rund shifted z6;

path p[];

p1 = (z1--z2 cutafter circle2) .. (z2--z3 cutbefore circle2 cutafter circle3)
		.. (z3--z4 cutbefore circle3);

draw p1;

p2 = p1 shifted (-.5u,u);
draw p2;

p3 = (z5--z6 cutafter circle 6) .. (z6--z7 cutbefore circle6);
draw p3;

endfig;
bye.
