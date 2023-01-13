//settings.outformat="";
//settings.render=-1;

settings.outformat="png";
settings.render=16;

import three;
import teapot;
import objects;


Embedded.targetsize = true;
Billboard.targetsize = true;


size(15cm, 0);

//currentprojection = perspective(2,-5,1,autoadjust=false);


void intitialScene()
{
  currentlight=(-5,-5, 10);
  currentprojection = perspective(-2,-10,2,target=(2,2,0),
				  up=Z,showtarget=false,autoadjust=false);

  real floorSizeX = 3.0;
  real floorSizeY = 5.0;

  //AXES AND GRID
  //draw_axes(shift((0,0,0)), "w");

  //FLOOR AND GRID
  surface plane = surface(O -- floorSizeX * X --
			  floorSizeX*X + floorSizeY*Y --
			  floorSizeY* Y --cycle);
  draw(plane,surfacepen=white+opacity(.2) );
  grid3(XYXgrid(0));


  //ROBOT
  transform3 trans =   shift((2, 2, 0)) * rotate(angle=180, u=O, v=Z);
  transform3 camera_transform = draw_robot(trans, -22, false, 1);

  pen dashed=linetype(new real[] {8,8});
  draw(camera_transform *(O -- X*.7),dashed);
     

  //TABLE
  transform3 trans =   shift((1, 2, 0));
  draw_table(trans, brown * 1.5 +opacity(1));

  //TEAPOT
  transform3 teapotTransform = shift((1.35, 2, .5)) * rotate(angle=-45, u=O, v=Z);
  draw(teapotTransform * Teapot,blue+opacity(1),render(compression=Low));

}


void justTeapot()
{
  currentprojection = perspective(-2,-10,2,target=(2,2,0),
				  up=Z,showtarget=false,autoadjust=false);

  real floorSizeX = 3.0;
  real floorSizeY = 5.0;
  //currentlight=(2,2,0);
  //currentlight=Headlamp;
  currentlight=Viewport;
  transform3 trans =   shift((2, 2, 0)) * rotate(angle=180, u=O, v=Z);
  transform3 camera_transform = draw_robot(trans, -22, false, 0);


  //TABLE
  transform3 trans =   shift((1, 2, 0));
  draw_table(trans, brown * 1.5 +opacity(1));

  //TEAPOT
  transform3 teapotTransform = shift((1.35, 2, .5)) *
    rotate(angle=-45, u=O, v=Z);
  
  draw(teapotTransform * Teapot,blue+opacity(1),render(compression=Low));

  triple behind= camera_transform * (X * -5);
  //  currentlight=(-5,-5, 10);

  write(stdout, behind );

  currentprojection = perspective(xpart(behind), ypart(behind), zpart(behind),target=(1.4,2,.5),showtarget=false,autoadjust=false);
  //  currentlight=(xpart(behind),ypart(behind), zpart(behind));

}


void diffChapter() { 
size(12.5cm, 0);
 currentlight=(-5,-5, 10);
  currentprojection = perspective(2.25,-10,4,target=(2.25,2.25,0),
				  up=Z,showtarget=false,autoadjust=false);

  real floorSizeX = 4.5;
  real floorSizeY = 4.5;

  //AXES AND GRID
  //draw_axes(shift((0,0,0)), "w");

  //FLOOR AND GRID
  surface plane = surface(O -- floorSizeX * X --
			  floorSizeX*X + floorSizeY*Y --
			  floorSizeY* Y --cycle);
  draw(plane,surfacepen=white+opacity(.2) );

  grid3(new grid3routines[] {XYXgrid(0)},
	pGrid=new pen[] {lightgray*.9},
	pgrid=new pen[] {lightgray*.9});

  //ROBOT

  draw( ((1,2,.5) -- (1,2,.25)),
	arrow=Arrow3(TeXHead2),
	L=Label("Robot", position=BeginPoint,align=Relative(N)));
  transform3 trans =   shift((1, 2, 0)) * rotate(angle=45, u=O, v=Z);
  transform3 camera_transform = draw_robot(trans, -22, false, 1, false);
  path3 arr = shift(0,0, .11250) * trans * (O -- X*.2);
  draw(arr,arrow=Arrow3);

  //GOAL

  draw( ((3.5,1,.5) -- (3.5,1,.25)),
	arrow=Arrow3(TeXHead2),
	L=Label("Goal", position=BeginPoint,align=Relative(N)));
  drawStar(shift((3.5,1, 0)) * rotate(angle=180, u=O, v=Z), .1, .05, orange);
}


void frameScene()
{
size(12.5cm, 0);
  currentlight=(-5,-5, 10);
  // currentprojection = perspective(-2,-10,2,target=(1,1,0),
  //				  up=Z,showtarget=false,autoadjust=false);

currentprojection=perspective(
camera=(1.19935430500841,-9.83608004941522,4.06686998685891),
up=(-4.53974273503788e-05,0.00498937679458066,0.0132963031718612),
target=(1,1,0),
zoom=1,
angle=13.6658376870004,
autoadjust=false);

  


  real floorSizeX = 3.0;
  real floorSizeY = 5.0;

  real objectOpacity=.2;

  //AXES AND GRID
  draw_axes(shift((0,0,0)), "w");

  //FLOOR AND GRID
  surface plane = surface(O -- floorSizeX * X --
			  floorSizeX*X + floorSizeY*Y --
			  floorSizeY* Y --cycle);
  draw(plane,surfacepen=white+opacity(objectOpacity) );
  grid3(new grid3routines[] {XYXgrid(0)},
	pGrid=new pen[] {lightgray*.9},
	pgrid=new pen[] {lightgray*.9});

  //ROBOT
  transform3 trans =   shift((2, 2, 0)) * rotate(angle=180, u=O, v=Z);
  transform3 camera_transform = draw_robot(trans, -22, true, objectOpacity);


  //TABLE
  //transform3 trans =   shift((1, 2, 0));
  //draw_table(trans, brown * 1.5 +opacity(objectOpacity));

  //TEAPOT
  //transform3 teapotTransform = shift((1.35, 2, .5)) * rotate(angle=-45, u=O, v=Z);
  //draw(teapotTransform * Teapot,blue+opacity(objectOpacity),render(compression=Low));

}

void measureLine(real length, triple start, triple end, triple offsetDir,
		 triple norm, triple textAlign) {

  start = start + offsetDir * .1;
  end = end + offsetDir * .1;

  string label = format("%6.1f", length);
  draw((start -- end),
       arrow=Arrows3(TeXHead2(normal=norm)),
       L=Label(label, position=MidPoint,align=textAlign),linewidth(1.0));

  
  draw(start - offsetDir * .05 -- start + offsetDir * .05,linewidth(1.0));
  draw(end - offsetDir * .05 -- end + offsetDir * .05,linewidth(1.0));
}
void translations()
{
size(10cm, 0);
  real transX = 1.5;
  real transY = 1.0;
  real transZ = .5;
  real offset = .1;

  currentlight=(2.6,-3.7,3.3);
  currentprojection = perspective(4.4,-2.2,1.6,target=(transX/2,transY/2,transZ/2),
				  up=Z,showtarget=false,autoadjust=false);

  triple startX = O;
  triple endX =  X * transX;
  triple startY = endX;
  triple endY =  Y* transY + X*transX;
  triple startZ = endY;
  triple endZ = Z * transZ +Y* transY + X*transX;
  
  draw_axes(shift((0,0,0)), "p", xAlign=Y);
  draw_axes(shift((transX,transY,transZ)), "c");
  
  pen dashed=linetype(new real[] {8,8});
  draw((startX -- endX),dashed+gray);
  draw((startY -- endY),dashed+gray);
  draw((startZ -- endZ),dashed+gray);

  measureLine(transX, startX, endX, -Y, Z, -Y-Z );
  measureLine(transY, startY, endY, X, Z, X -Z );
  measureLine(transZ, startZ, endZ, -X, Y, -X);

  dotfactor=10;
  triple pPoint = (0,0,.5);
  dot(pPoint);
  draw(( (0, .25, .5) -- pPoint), margin=Margin3,	arrow=Arrow3(TeXHead2),
       L=Label("$(0,0,.5)_p$", position=BeginPoint,align=Relative(E)),
       linewidth(1.0));


  triple cPoint = (0+transX,0 + transY,.5+transZ);
  dot(cPoint);
  draw(( (1.35, .85, 1) -- cPoint),

       margin=Margin3,	arrow=Arrow3(TeXHead2),
       L=Label("$(0,0,.5)_c$", position=BeginPoint,align=Relative(W)),
       linewidth(1.0));

  //grid3(XYXgrid(0));
  //grid3(XZXgrid(0));


}





//intitialScene();
//justTeapot();
//diffChapter();
//frameScene();
translations();
