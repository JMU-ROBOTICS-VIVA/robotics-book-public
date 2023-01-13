import animation;
import math;

defaultpen(fontsize(10pt));

//unitsize(3inch);
//size(2inch,0);

real speed = 1; // inches per second ??

// Robot dimensions
real robot_height = 25;
real robot_width = sqrt(robot_height^2 - (robot_height/2.0)^2); // equilateral
real rightOffset = 2. * robot_width / 3.;
real leftOffset = -robot_width / 3.;


// Set up environment and paths...
pair sceneLabelLoc = (-30, 90);
pair cFreeLabelLoc = (45, 80);

pair q_i = (-10, 20);
pair q_g = (55, 58);

// Obstacle parameters
pair boxLL = (20, 0);
pair boxSize = (50, 40);
pair boxCenter = boxLL + .5 * boxSize;
pair center = (0, 73);
real radius = 10;

// Path that the robot would take to trace Cobs around box
path boxPath = 
  boxLL + (-rightOffset, 0) --
  boxLL + (-rightOffset, boxSize.y) --
  boxLL + (-leftOffset,
	    boxSize.y + robot_height/2) --
  boxLL + (-leftOffset + boxSize.x,
	    robot_height/2 + boxSize.y) --
  boxLL + (-leftOffset + boxSize.x,
	    -robot_height/2) --
  boxLL + (-leftOffset, -robot_height/2) --
  cycle;


// Path that the robot would take to trace Cobs around circle
path circlePath =
  arc(center + (-leftOffset, robot_height/2), radius, 120, 0) --
  arc(center + (-leftOffset, -robot_height/2), radius, 0, -120) --
  arc(center + (-rightOffset, 0), radius, -120, -240) -- cycle;

// Path represnting robot triangle at a particular position
path robotPath(pair position) {
  return  (position + (leftOffset, robot_height / 2) --
	   position + (rightOffset, 0) --
	   position + (leftOffset, -robot_height / 2) -- cycle);
}

// Path representing full robot including a central dot
path drawRobot(pair position, pen morePen=defaultpen) {
  path triangle = robotPath(position);
  filldraw(triangle, mediumgray + morePen, defaultpen + morePen);
  dot(position, defaultpen + morePen);
  return triangle;
}

// Create an animation showing the robot following a path
void animatePath(real speed, path points, animation a){

  real len = arclength(points);
  real n = len / speed;
  for(int i=0; i <= n; ++i) {
    save();
    real frac = i/n;

    pair cur = relpoint(points, frac);
    draw(subpath(points, 0.0, reltime(points, frac))); 
    drawRobot(cur);
    
    a.add(); // Add currentpicture to animation.
    restore();
   }
}

// Draw the starting configuration of W
void drawStart() {
  label(Label("$\mathcal{W}$"), sceneLabelLoc);
  
  filldraw(box(boxLL, boxLL + boxSize), mediumgray);
  label(L=Label("$\mathcal{O}_2$"), boxCenter);
  
  filldraw(circle(center, radius), mediumgray);
  label(L=Label("$\mathcal{O}_1$"), center);

}

// Draw Cobs and Cfree
void drawFinal() {
  // Show the final result
  filldraw(boxPath, mediumgray);
  filldraw(circlePath, mediumgray);

  label(Label("$\mathcal{C}$"), sceneLabelLoc);
  label(Label("$\mathcal{C}_{free}$"), cFreeLabelLoc);

  label(Label("$\mathcal{C}_{obs}$",boxCenter));
  label(Label("$\mathcal{C}_{obs}$", center));
  // Label obsLabel = Label("$\mathcal{C}_{obs}$",(45, 0));
  // Label obsLabel = Label("$\mathcal{C}_{obs}$",(45, 0));

  
  
  // Label obsLabel = Label("$\mathcal{C}_{obs}$",(45, 0));
  // label(obsLabel);
  // path[] p=texpath(obsLabel);
  // pair minl = min(p);
  // pair maxl = max(p);

  
  // draw((45, maxl.y) -- boxLL + .5 * boxSize, arrow=Arrow(TeXHead));
  // draw((minl.x, 0) -- center, arrow=Arrow(TeXHead));
}


// Create an animation of Cobs being generated
void animateCObsMovie() {
  animation a;
  drawStart();

  for (int i = 0; i < 10; ++i) {// add a delay
    a.add(); 
  }

  animatePath(speed, boxPath, a);
  draw(boxPath);
  
  for (int i = 0; i < 10; ++i) {// add a delay
    a.add(); 
  }
  
  animatePath(speed, circlePath, a);
  draw(circlePath);

  for (int i = 0; i < 10; ++i) {// add a delay
    a.add(); 
  }
  
  erase();
  drawFinal();

  a.add();

  a.movie(BBox(0.25cm),loops=1,delay=50);
}


// Create a pdf animation with many fewer frames.
void animateCObsPaper() {
  animation a;

  
  filldraw(box(boxLL, boxLL + boxSize), mediumgray);
  filldraw(circle(center, radius), mediumgray);

  animatePath(30, boxPath, a);
  draw(boxPath);
  
  animatePath(30, circlePath, a);
  draw(circlePath);
  erase();
  drawFinal();

  a.add();

  a.movie(BBox(0.25cm),loops=1,delay=50, format="pdf");
}

// Create the full workspace figure including labels
void workspaceFigure() {
  drawStart();
  path bot_path = drawRobot(q_i);
  filldraw(bot_path, mediumgray);
  dot(q_i);
  label(Label("$q$"), q_i, align=NW);
  
  draw(q_i + (10,12) -- q_i + (4, 1), arrow=Arrow(TeXHead),
       L=Label("$\mathcal{A}(q)$", position=BeginPoint));
}

// Path represeting a solution from qi to qg.
path solPath() {
  pair waypoint1 = center - (1, robot_height +8);
  pair waypoint3 =  boxLL + (-leftOffset,
			     boxSize.y + robot_height/2) + (0, 4);
  pair waypoint2 = midpoint(waypoint1 -- waypoint3) + (0,.5);
  pair waypoint4 = midpoint(waypoint3 -- q_g)+ (0,.5);
  
  path solPath = q_i .. waypoint1 .. waypoint2 .. waypoint3 .. waypoint4 .. q_g;
  return solPath;
}

// Create a complete figure showing the solution path in the final C
// space
void pathFigureCObs() {
  drawFinal();
  
  dot(q_i);
  label(Label("$\mathbf{q}_I$"), q_i, align=SW);
  path solPath = solPath();
  draw(solPath, ArcArrow());
  //dot(solPath);
  dot(q_g);
  label(Label("$\mathbf{q}_G$"), q_g, align=NE);

}

// Create a figure showing the solution path in the world
void pathFigureWorld() {
  drawStart();
  path solPath = solPath();
  

  real len = arclength(solPath);
  int steps = 5;
  for(int i=0; i <= steps; ++i) {
    real frac = i/(real)steps;
    write(frac);

    pair cur = relpoint(solPath, frac);
    drawRobot(cur, opacity(frac* .8 + .2));
   }

}


picture fileGrid(string fileName, real cell_width) {
   real[][] data = input(fileName).line().csv().dimension(0,0);
   int Nx = (int)data[0][0];
   int Ny = (int)data[0][1];

   // First draw the grid itself...
   picture pic;
   for(int i=0; i < Nx; ++i) {
     for(int j=0; j < Ny; ++j) {
       path box =  scale(cell_width) * shift(i, j) * unitsquare;
       draw(pic, box);
     }
   }

   // Now draw all the marked cells.
   for (int i = 1; i < data.length; ++i) {
     pen p = rgb(data[i][2],data[i][3], data[i][4]);
     path box =  scale(cell_width) * shift(data[i][1], data[i][0]) * unitsquare;
     filldraw(pic, box, p);
    }
   return pic;
       
}


picture obstacleGrid(int Nx, int Ny, pair origin, real scale, path[] obstacles,
		     string fileName="", bool showGraph=false,
		     pen gridColor=black,
		     pen obstacleColor=black)
{
  file fout;
  if (length(fileName)>0){
    fout=output(fileName);
    write(fout, "rows: ");
    write(fout, Ny);
    write(fout, " cols: ");
    write(fout,Ny);
    write(fout, '\n');
  }
  picture pic;
  bool[][] occupied = new bool[Ny][Nx];
  path[][] boxes = new path[Ny][Nx];
  for(int col=0; col < Nx; ++col) {
    for(int row=0; row < Ny; ++row) {
      bool fill = false;
      path box =  shift(origin) * scale(scale) * shift(col, row) * unitsquare;
      
      for (path obs: obstacles) {
	if((intersect(obs, box).length > 0) || (inside(obs,box) == 1)) {
	  fill = true;
	}
      }
      occupied[row][col] = fill;
      boxes[row][col] = box;

      if (!fill) {
	draw(pic, box, gridColor);
      } else {
	filldraw(pic, box, obstacleColor, obstacleColor);
	
	if (length(fileName)>0){// Save the occupied cells. 
	  write(fout, col, row);        
	  write(fout, '\n');
	}
      }
    }
  }
  
  if (showGraph) {
    for(int col=0; col < Nx; ++col) {
      for(int row=0; row < Ny; ++row) {
	if (!occupied[row][col]) {
	  int[][] offsets = {{-1, -1}, {-1, 0}, {-1, 1},
			    {0, -1},  {0, 1},
			    {1, -1}, {1, 0}, {1, 1}};
	  for (int[] offset : offsets) {
	    if (occupied.initialized(row+offset[1]) &&
		occupied[row].initialized(col+offset[0]) &&
		!occupied[row+offset[1]][col+offset[0]])
	      {
		pair p1 = .5 * (min(boxes[row][col]) + max(boxes[row][col]));
		pair p2 = .5 * (min(boxes[row+offset[1]][col+offset[0]]) +
				max(boxes[row+offset[1]][col+offset[0]]));
		
		draw(pic, p1 -- p2);
		dot(pic, p1);
		dot(pic, p2);
	      }
					  
	  }
	  
	}
      }
    }
  }
  return pic; 
}

void gridFigure(bool filled, real cellWidth=9,
		bool noGrid=false, string fileName="",
		bool showGraph=false,
		pen gridColor=black,
		pen obstacleColor=black){
  if (!filled) {
    fill(boxPath, mediumgray);
    fill(circlePath, mediumgray);
  } else {
    fill(boxPath, invisible);
    fill(circlePath, invisible);
  }

  pair minP =  min(currentpicture, true);
  pair maxP =  max(currentpicture, true);
  minP = minP - (30,30);
  maxP = maxP + (30,30);
  real width = maxP.x - minP.x;
  real height = maxP.y - minP.y;
  int rows = (int)(height / cellWidth);
  int cols = (int)(width / cellWidth);

  path[] obstacles;
  if (filled) {
    obstacles.push(boxPath);
    obstacles.push(circlePath);
  }
  save();  
  picture cells = obstacleGrid(rows,cols, (minP.x, minP.y),
			       width/cols, obstacles, fileName,showGraph,
			       gridColor, obstacleColor);
  add(cells);

  pair minP =  min(currentpicture, true);
  pair maxP =  max(currentpicture, true);
  write("asymptote bounds of the grid figure:");
  write(minP);
  write(maxP);

  if (noGrid) {
    restore();
    dot(minP, invisible + linewidth(.0001));
    dot(maxP, invisible + linewidth(.0001));
    
  }
}

void gridSearchFigure(string fileName) {
  add(fileGrid(fileName, 10));
}

picture drawGraph(string graphFile, pen nodePen, pen edgePen) {
   real[][] data = input(graphFile).line().csv().dimension(0,0);
   picture pic;
   
   //first draw all of the edges...
   for (int i= 0; i < data.length; ++i) {
     for (int j = 2; j < data[i].length; j += 2) {
       path edge = (data[i][0], data[i][1]) -- (data[i][j], data[i][j+1]);
       draw(pic, edge, edgePen);
     }
   }

   //now draw the nodes...
   for (int i= 0; i < data.length; ++i) {
     pair node =  (data[i][0], data[i][1]);
     dot(pic, node, nodePen);
   }
   return pic;
}


void RRTFigure(string treeFile, string solFile="") {
  gridFigure(false, true);
  
  add(drawGraph(treeFile, currentpen + black, currentpen + black));
  if (length(solFile) !=0) {
    add(drawGraph(solFile, currentpen + blue, currentpen + red));
  }
}

if(false) {
  settings.outformat="pdf";

  size(1.0inch,0);
  animateCObsPaper();
  erase();
  
  size(1.5inch,0);
  workspaceFigure();
  shipout("workspace", format="pdf");
    
  erase();
  drawFinal();
  shipout("c_obs_final", format="pdf");
  
  
  size(1.75inch,0);
  erase();
  pathFigureCObs();
  shipout("path_c_obs", format="pdf");
  
  //size(1.75inch,0); // opacity bug in asymptote :(
  //erase();
  //pathFigureWorld();
  //shipout("path_world", format="pdf");
  
  
  
  size(1.25inch,0);
  erase();
  gridFigure(false, cellWidth=15);
  shipout("grid1", format="pdf");
  
  size(1.25inch,0);
  erase();
  gridFigure(true, cellWidth=15);
  shipout("grid2", format="pdf");

  size(1.25inch,0);
  erase();
  gridFigure(true, cellWidth=15, showGraph=true,
	     gridColor=lightgray, obstacleColor=invisible);
  shipout("grid3", format="pdf");

  size(1.75inch,0);
  erase();
  gridFigure(true, cellWidth=5, fileName="filled_grid_cells.dat");
  shipout("dummy", format="pdf");
  
  // BFS TRACE FIGURES...
  string[] which = {"0001", "0002", "0009", "0081", "0350", "0641"};
  for (int i = 0; i < which.length; ++i) {
    
    size(1.75inch,0);
    erase();
    gridSearchFigure("dat/bfs" + which[i] + ".dat");
    shipout("bfs_" + which[i], format="pdf");
  }
  
  // DFS TRACE FIGURES...
  string[] which = {"0001", "0002", "0009", "0081", "0350", "0477"};
  for (int i = 0; i < which.length; ++i) {
    
    size(1.75inch,0);
    erase();
    gridSearchFigure("dat/dfs" + which[i] + ".dat");
    shipout("dfs_" + which[i], format="pdf");
  }
  
  // DIJKSTRA TRACE FIGURES...
  string[] which = {"0001", "0002", "0013", "0100", "0350", "0674"};
  for (int i = 0; i < which.length; ++i) {
    
    size(1.75inch,0);
    erase();
    gridSearchFigure("dat/dijkstra" + which[i] + ".dat");
    shipout("dijkstra_" + which[i], format="pdf");
  }
  
  // A STAR TRACE FIGURES... 
  string[] which = {"0001", "0002", "0013", "0100", "0350", "0373"};
  for (int i = 0; i < which.length; ++i) {
    
    size(1.75inch,0);
    erase();
    gridSearchFigure("dat/astar" + which[i] + ".dat");
    shipout("astar_" + which[i], format="pdf");
  }
  
  size(7inch,0);
  erase();
  gridFigure(filled=false, noGrid=true);
  shipout("no_grid_c_obs", format="png");
  
  // size(1.75inch,0);
  // erase();
  // RRTFigure("dat/rrt_tree120.dat");
  // shipout("rrt_sol1", format="pdf");
  
  // size(1.75inch,0);
  // erase();
  // RRTFigure("dat/rrt_tree200.dat");
  // shipout("rrt_sol2", format="pdf");
  
  
  // size(1.75inch,0);
  // erase();
  // RRTFigure("dat/rrt_tree380.dat", "dat/rrt_sol.dat");
  // shipout("rrt_final", format="pdf");
  
  
  
  // size(1.75inch,0);
  // erase();
  // RRTFigure("dat/prm_edges60.dat");
  // shipout("prm_final", format="pdf");
} else {

  
  animateCObsMovie();
}
