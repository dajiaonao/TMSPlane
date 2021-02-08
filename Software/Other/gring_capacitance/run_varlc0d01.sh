gmsh   Gring_realreal_varlc0d01.geo  -3 -order 2
ElmerGrid  14 2 Gring_realreal_varlc0d01.msh  -autoclean

cd Gring_realreal_varlc0d01
ElmerSolver ../case.sif
