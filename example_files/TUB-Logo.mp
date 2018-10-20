% Converted from PostScript(TM) to MetaPost by pstoedit
% MetaPost backend contributed by Scott Pakin <pakin_AT_uiuc.edu>
% pstoedit is Copyright (C) 1993 - 2007 Wolfgang Glunz <wglunz34_AT_pstoedit.net>

% Modified by Matthias Geier, March 2008

%prologues := 1; % Generate structured PostScript (EPS)

beginfig(1);
linecap := butt;
linejoin := mitered;

color TUcolor;
%TUcolor = (0.290196078,0.290196078,0.549019608); % blau (74,74,140) laut TIF
%TUcolor = (0.6,0,0); % rot (#990000) laut TUB WebDesign-Richtlinie
TUcolor = black;
%TUcolor = white;

%TUcolor = (0.88627451,0,0.454901961); % Telekom Magenta (226,0,116)
%TUcolor = (0.6,0.6,0.6); % Telekom Grau (153,153,153)

drawoptions (withcolor TUcolor);

picture Upart;
Upart := image(
% U (rechter Teil)
fill (328.48,69.4688)--(352.195,69.4688)--(347.801,23.8477)
	..controls (347.246,10.582) and (336.316,0)..(322.91,0)
	--(321.789,0.0078125)--cycle;
); % end of picture "Upart"

% MetaPost cannot cut "holes" into areas, it can only clip things away
% As a little trick, I define a path which surrounds the object (Upart) and
% combine it with the path of the "hole" to a closed path and clip the object
% with this path. There is a connection between the two paths but it has zero
% width and shouldn't be visible (I hope!).

path box[];
box1 = bbox Upart; % start/end on lower left corner
box2 = box1 rotatedaround (center box1,180);

path b,e,r,l,i[],n;
b = (332.34,26.7383)--(341.066,26.7383)
	..controls (344.406,26.7383) and (346.594,28.6484)..(346.84,31.3359)
	..controls (347.055,33.6484) and (345.316,35.7539)..(341.805,35.7539)
	..controls (339.188,35.7539) and (336.395,34.0859)..(336.18,31.7695)
	..controls (336.098,30.8984) and (336.316,30.4766)..(336.648,29.8789)
	--(332.594,29.8789)--cycle;
e = (343.012,44.0938)
	..controls (343.957,43.4609) and (344.539,42.1016)..(344.457,41.2266)
	..controls (344.43,40.9375) and (344.355,40.5469)..(344.199,40.3203)
	--(340.652,44.6562)
	..controls (338.617,43.9648) and (337.191,42.4883)..(337.012,40.5625)
	..controls (336.789,38.168) and (338.68,36.1953)..(342.176,36.1953)
	..controls (344.988,36.1953) and (347.484,38.0547)..(347.727,40.6758)
	..controls (347.875,42.2617) and (347.598,43.0273)..(346.801,44.3398)
	--cycle;
r = (348.102,45.4883)--(348.395,48.5078)--(343.508,48.5078)
	..controls (342.141,48.5078) and (341.578,49.1602)..(341.652,49.9414)
	..controls (341.676,50.1719) and (341.688,50.2969)..(341.719,50.4219)
	--(337.953,50.4375)
	..controls (337.844,49.3008) and (338.438,48.5859)..(339.684,48.3555)
	--(339.684,48.3242)--(338.027,48.3242)--(337.789,45.4883)
	--cycle;
l = (348.934,54.1445)--(334.734,54.1445)--(334.445,51.1445)
	--(348.645,51.1445)--cycle;
i1 = (349.328,58.1914)--(339.109,58.1914)--(338.805,55.168)
	--(349.02,55.168)--cycle;
i2 = (338.23,58.1914)--(334.988,58.1914)--(334.684,55.168)
	--(337.922,55.168)--cycle;
n = (339.203,59.5039)--(349.438,59.5039)--(349.754,62.5781)
	--(343.719,62.5781)
	..controls (343.25,62.5781) and (342.477,62.7227)..(342.477,63.3516)
	..controls (342.477,63.9883) and (343.125,64.1562)..(343.531,64.1562)
	--(349.902,64.1562)--(350.195,67.2109)--(343.438,67.2109)
	..controls (341.465,67.2109) and (339.641,66.4609)..(339.492,64.8594)
	..controls (339.422,64.082) and (339.879,63.1445)..(340.855,62.5117)
	--(340.848,62.4492)--(339.5,62.4492)--cycle;

clip Upart to box1 -- reverse b -- cycle;
clip Upart to box2 -- reverse e -- cycle;
clip Upart to box1 -- reverse r -- cycle;
clip Upart to box2 -- reverse l -- cycle;
clip Upart to box2 -- reverse i1 -- cycle;
clip Upart to box2 -- reverse i2 -- cycle;
clip Upart to box1 -- reverse n -- cycle;

draw Upart;

%% uncomment the following lines to see the "clipping paths":
%draw box1 -- b -- cycle withcolor red;
%draw box2 -- e -- cycle withcolor red;
%draw box1 -- r -- cycle withcolor red;
%draw box2 -- l -- cycle withcolor red;
%draw box2 -- i1 -- cycle withcolor red;
%draw box2 -- i2 -- cycle withcolor red;
%draw box1 -- n -- cycle withcolor red;

% b - Loch
fill (341.355,29.8789)..controls (340.496,29.8789) and (339.801,30.3789)..(339.871,31.1406)
	..controls (339.938,31.8828) and (340.727,32.3867)..(341.59,32.3867)
	..controls (342.449,32.3867) and (343.145,31.8828)..(343.074,31.1406)
	..controls (343.004,30.3789) and (342.215,29.8789)..(341.355,29.8789)
	--cycle;
% e - Loch
fill (342.387,39.3516)..controls (342.207,39.2852) and (342.086,39.2188)..(341.652,39.2188)
	..controls (340.777,39.2188) and (339.949,39.7539)..(340.02,40.5312)
	..controls (340.059,40.9375) and (340.184,41.2617)..(340.621,41.5195)
	--(342.387,39.3516)--cycle;

% T (oberer Teil) und U (linker Teil)
fill (325.129,62.8711)--(319.109,0.238281)..controls (305.707,2.58203) and (296.68,9.52734)..(297.895,22.5156)
	--(297.883,22.543)--(300.762,52.4531)--(261.934,52.4531)
	..controls (255.535,52.5) and (250.363,57.7031)..(250.363,64.1133)
	..controls (250.363,70.5234) and (255.535,75.7266)..(261.934,75.7773)
	--(313.562,75.7773)..controls (319.992,75.7617) and (325.195,70.5469)..(325.195,64.1133)
	..controls (325.195,63.6953) and (325.172,63.2773)..(325.129,62.8711)
	--cycle;
% T (unterer Teil)
fill (274.098,49.8711)--(295.398,49.8711)--(291.199,6.25)
	--(269.898,6.25)--(274.098,49.8711)--cycle;

endfig;
bye.
