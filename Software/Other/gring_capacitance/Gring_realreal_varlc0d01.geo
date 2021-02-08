lc = 0.01;
lca = 1;

s1 = 0.550;
s2 = 0.545;
s0 = 0.5;

lh = 0.001;
z0 = -0.5*lh;

sout = 10;
lhout = 10;
zout = -0.5*lhout;

Point(1) = {-1*s0, 0, z0, lc};
Point(2) = {-0.5*s0, 0.866*s0, z0, lc};
Point(3) = {0.5*s0, 0.866*s0, z0, lc};
Point(4) = {1*s0, 0, z0, lc};
Point(5) = {0.5*s0, -0.866*s0, z0, lc};
Point(6) = {-0.5*s0, -0.866*s0, z0, lc};


Point(101) = {-1*s1, 0, z0, lc};
Point(102) = {-0.5*s1, 0.866*s1, z0, lc};
Point(103) = {0.5*s1, 0.866*s1, z0, lc};
Point(104) = {1*s1, 0, z0, lc};
Point(105) = {0.5*s1, -0.866*s1, z0, lc};
Point(106) = {-0.5*s1, -0.866*s1, z0, lc};

Point(111) = {-1*s2, 0, z0, lc};
Point(112) = {-0.5*s2, 0.866*s2, z0, lc};
Point(113) = {0.5*s2, 0.866*s2, z0, lc};
Point(114) = {1*s2, 0, z0, lc};
Point(115) = {0.5*s2, -0.866*s2, z0, lc};
Point(116) = {-0.5*s2, -0.866*s2, z0, lc};


Point(881) = {-1*sout, 0, zout, lca};
Point(882) = {-0.5*sout, 0.866*sout, zout, lca};
Point(883) = {0.5*sout, 0.866*sout, zout, lca};
Point(884) = {1*sout, 0, zout, lca};
Point(885) = {0.5*sout, -0.866*sout, zout, lca};
Point(886) = {-0.5*sout, -0.866*sout, zout, lca};




Line(1) = {1,2};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,5};
Line(5) = {5,6};
Line(6) = {6,1};

Line(101) = {101,102};
Line(102) = {102,103};
Line(103) = {103,104};
Line(104) = {104,105};
Line(105) = {105,106};
Line(106) = {106,101};

Line(111) = {111,112};
Line(112) = {112,113};
Line(113) = {113,114};
Line(114) = {114,115};
Line(115) = {115,116};
Line(116) = {116,111};

Line(881) = {881,882};
Line(882) = {882,883};
Line(883) = {883,884};
Line(884) = {884,885};
Line(885) = {885,886};
Line(886) = {886,881};

Curve Loop(1) = {1,2,3,4,5,6};
Plane Surface(1) = {1};

Curve Loop(101) = {101,102,103,104,105,106};
//Plane Surface(101) = {101};

Curve Loop(111) = {111,112,113,114,115,116};
//Plane Surface(111) = {111};

Plane Surface(1101) = {111, 101};

//Plane Surface(401) = {101, 1};

Curve Loop(881) = {881,882,883,884,885,886};
Plane Surface(881) = {881};

e[] = Extrude {0, 0, lh} { Surface{1101}; };
ei[] = Extrude {0, 0, lh} { Surface{1}; };
//em[] = Extrude {0, 0, lh} { Surface{401}; };
eout[] = Extrude {0, 0, lhout} { Surface{881}; };

Delete {Volume{1}; Volume{2}; Volume{3};}

Surface Loop(1) = {1, ei[0], ei[2], ei[3], ei[4], ei[5], ei[6], ei[7]};
Surface Loop(1101) = {1101, e[0], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9], e[10], e[11], e[12], e[13]};
Surface Loop(881) = {881, eout[0], eout[2], eout[3], eout[4], eout[5], eout[6], eout[7]};

Physical Surface("mysurface1") = {1, ei[0], ei[2], ei[3], ei[4], ei[5], ei[6], ei[7]};
//Physical Volume("myvolumn1") = {ei[1]};

Physical Surface("mysurface2") ={1101, e[0], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9], e[10], e[11], e[12], e[13]};
//Physical Volume("myvolumn2") = {e[1]};

//Physical Surface("mysurface3") = {401, em[0], em[2], em[3], em[4], em[5], em[6], em[7], em[8], em[9], em[10], em[11], em[12], em[13]};
//Physical Volume("myvolum3") = {em[1]};

Physical Surface("mysurface4") = {881, eout[0], eout[2], eout[3], eout[4], eout[5], eout[6], eout[7]};

Volume(881) = {881, 1, 1101};
//Volume(881) = {881};
Physical Volume("myvolume881") = {881}; 
