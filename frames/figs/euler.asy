//settings.outformat="";
//settings.render=-1;

settings.outformat="png";
settings.render=16;
settings.maxtile=(100,100);

defaultpen(fontsize(10pt));

import three;
import teapot;
import objects;
import obj;

Embedded.targetsize = true;
Billboard.targetsize = true;



void draw_axes(transform3 trans, string label,
	       triple xAlign=X, triple yAlign=Y, triple zAlign=Z,
	       real opac=1.0, bool bw=false, real sizeMult=1)
{

  pen red = red;
  pen green = green;
  pen blue = blue;
  if (bw) {
    red = black;
    green = black;
    blue = black;
  }
  draw(trans * (O -- X *.75),
       arrow=Arrow3(size=8.0 * sizeMult),
       L=Label("$x" + label + "$", position=EndPoint,align=xAlign),
       red+opacity(opac)+linewidth(.8*sizeMult));
  draw(trans * (O -- Y *.75),
       arrow=Arrow3(size=8.0 * sizeMult),
       L=Label("$y" + label+ "$", position=EndPoint,align=yAlign),
       green+opacity(opac)+linewidth(.8*sizeMult));
  draw(trans * (O -- Z *.75),
       arrow=Arrow3(size=8.0 * sizeMult),
       L=Label("$z" + label+ "$", position=EndPoint,align=zAlign),
       blue+opacity(opac)+linewidth(.8*sizeMult));
}

void drawAirplane(transform3 trans) {
  //pen[] surfacepen={white,white,blue};
  //surfacepen.cyclic=true;
 
  material surfacepen=material(diffusepen=gray(0.5), emissivepen=gray(0.4),
			       ambientpen=black,specularpen=black);
  draw(trans * shift(0,0,-.02) * scale3(.04) *
       rotate(angle=90, u=O, v=Z)*rotate(angle=90, u=O, v=X) *
       //obj("F_18.obj",verbose=false,surfacepen));
       obj("F_18.obj",verbose=false,surfacepen));
}



void drawGradientSurface(path3 p, real startAngle, real endAngle,
			 triple c, triple theAxis, 
			 int increments, real startOpac, real endOpac,
			 pen color)
{
  real opac = startOpac;
  real ang_inc = (endAngle-startAngle)/increments;
  real prev_ang = startAngle;
  for (real ang=startAngle + ang_inc; ang <=endAngle+.0001;
       ang += ang_inc) {
    opac += 1/increments * endOpac;
    draw(surface(p,   c=c,   axis=theAxis,angle1=prev_ang, angle2=ang),
	 surfacepen=material(diffusepen=color*0+opacity(opac),
			     emissivepen=color+opacity(opac),
			     specularpen=color*0+opacity(opac)));
    prev_ang = ang;
  }
}


void eulerStatic(real x, real y, real z)
{
  size(4.5cm, 0);
  erase();
  transform3 rotX = rotate(angle=x, u=O, v=X);
  transform3 rotY = rotate(angle=y, u=O, v=Y);
  transform3 rotZ = rotate(angle=z, u=O, v=Z);

  currentlight=(2.6,3.7,2.2);
  //currentprojection = perspective(2.6,3.8,2.2,target=(0,0,0),
  //				  up=Z,showtarget=false,autoadjust=false);
  // currentprojection = perspective(3.7,3.2,1.4,target=(0,0,0),
  // 				  up=Z,showtarget=false,autoadjust=false);
  currentprojection = orthographic(3.7,3.2,1.4,target=(0,0,0));
  // BEFORE ROTATIONS
  draw_axes(shift((0,0,0)), "_0", opac=.9, bw=true);
  drawAirplane(shift((0,0,0)));
  shipout("euler_static_0.png");
  erase();

   
  // FIRST THE X ROTATION:
  draw_axes(shift((0,0,0)), "_0", opac=.9, bw=true);
  draw_axes(rotX , "_1",opac=1);
  drawAirplane(rotX);

  // Angle lines
  //draw(arc(O, (0,.5,0), rotX * (0,.5,0)),
  //     arrow=Arrow3);

  // Rotation symbols
  draw(arc((.45,0,0), (.45,0.05,0.05),   (.45,0.05,-.05), X),
       arrow=Arrow3(size=3bp), red+linewidth(.5));
 label(L=Label("$" +string(x)+"^o$"),(.45,0,.12) );

  // DRAW GRADIENT SURFACES
  path3 xc1 = (O -- (.75, 0, 0));
  path3 yc1 = (O -- (0, .75, 0));
  path3 zc1 = (O -- (0, 0, .75));
  drawGradientSurface(xc1, 0, x, O, X, 30, .1, .35, red);
  drawGradientSurface(yc1, 0, x, O, X, 30, .1, .35, green);
  drawGradientSurface(zc1, 0, x, O, X, 30, .1, .35, blue);

  shipout("euler_static_1.png");

  

  // Y ROTATION:
  erase();
  draw_axes(shift((0,0,0)), "_0", opac=.9,bw=true);
  //draw_axes(rotX , "_1",opac=.2, bw=true);
  draw_axes(rotY * rotX , "_2",opac=1);
  drawAirplane(rotY * rotX);

  // around y axis
  draw(arc( (0,.45,0),  (-.05,0.45,0.05),    (-.05,0.45,-.05),
  	    Y),
       arrow=Arrow3(size=3bp), green+linewidth(.5));
  label(L=Label("$" +string(y)+"^o$"),(0,.45,.12) );
  // draw(arc(O, rotX *(.5,0,0),  rotY * rotX * (.5,0,0), Y),
  //      arrow=Arrow3);

  // DRAW GRADIENT SURFACES
  path3 xc1 = (O -- rotX  * (.75, 0, 0));
  path3 yc1 = (O -- rotX  * (0, .75, 0));
  path3 zc1 = (O -- rotX  * (0, 0, .75));
  drawGradientSurface(xc1, 0, y, O, Y, 30, .1, .35, red);
  drawGradientSurface(yc1, 0, y, O, Y, 30, .1, .35, green);
  drawGradientSurface(zc1, 0, y, O, Y, 30, .1, .35, blue);

  shipout("euler_static_2.png");

  // Z ROTATION:
  erase();
  draw_axes(shift((0,0,0)), "_0", opac=.9, bw=true);
  //draw_axes(rotY * rotX , "_2",opac=.2, bw=true);
  draw_axes(rotZ* rotY * rotX , "_3",opac=1);
  drawAirplane(rotZ * rotY * rotX);

  // around Z axis
  draw(arc( (0,0,.45),  (-.05,0.05,0.45),    (.05,0.05,.45),
  	    Z),
       arrow=Arrow3(size=3bp), blue+linewidth(.5));
  label(L=Label("$" +string(z)+"^o$"),(.12,-.12,.45) );
  
  //  draw(arc(O, (0,.5,0),  rotZ * (0,.5,0), Z),
  //       arrow=Arrow3);

  // DRAW GRADIENT SURFACES
  path3 xc1 = (O -- rotY * rotX  * (.75, 0, 0));
  path3 yc1 = (O -- rotY * rotX  * (0, .75, 0));
  path3 zc1 = (O -- rotY * rotX  * (0, 0, .75));
  drawGradientSurface(xc1, 0, z, O, Z, 30, .1, .35, red);
  drawGradientSurface(yc1, 0, z, O, Z, 30, .1, .35, green);
  drawGradientSurface(zc1, 0, z, O, Z, 30, .1, .35, blue);

  shipout("euler_static_3.png");

  
}

void eulerNonStatic(real x, real y, real z)
{
  size(4.5cm, 0);
  erase();
  transform3 rotX = rotate(angle=x, u=O, v=X);
  transform3 rotY = rotate(angle=y, u=O, v=Y);
  transform3 rotZ = rotate(angle=z, u=O, v=Z);
  
  currentlight=(2.6,5.7,2.6);
  //  currentprojection = perspective(3.7,3.2,1.4,target=(0,0,0),
  //				  up=Z,showtarget=false,autoadjust=false,
  //				  center=true);
  //currentprojection = perspective(4.5, 2,.9,target=(0,0,0),
  //				  up=Z,showtarget=false,autoadjust=false,
  // 				  center=true);
  currentprojection = orthographic(3.7,3.2,1.4,target=(0,0,0));

  
  // BEFORE ROTATIONS
  draw_axes(shift((0,0,0)), "_0", opac=1.0, bw=true);
  drawAirplane(shift((0,0,0)));
  shipout("euler_nonstatic_0.png");
  erase();
  
  
  // FIRST THE X ROTATION:
  draw_axes(shift((0,0,0)), "_0", opac=.9,bw=true);
  draw_axes(rotX , "_1",opac=1,sizeMult=1);
  drawAirplane(rotX);
  
  // Angle lines
  //draw(arc(O, (0,.5,0), rotX * (0,.5,0)),
  //     arrow=Arrow3);

  // Rotation symbols
  draw(arc((.45,0,0), (.45,0.05,0.05),   (.45,0.05,-.05), X),
       arrow=Arrow3(size=3), red+linewidth(.5));
  label(L=Label("$" +string(x)+"^o$"),(.45,0,.12) );
  

  // DRAW GRADIENT SURFACES
  path3 xc1 = (O -- (.75, 0, 0));
  path3 yc1 = (O -- (0, .75, 0));
  path3 zc1 = (O -- (0, 0, .75));
  drawGradientSurface(xc1, 0, x, O, X, 30, .1, .35, red);
  drawGradientSurface(yc1, 0, x, O, X, 30, .1, .35, green);
  drawGradientSurface(zc1, 0, x, O, X, 30, .1, .35, blue);

  shipout("euler_nonstatic_1.png");

  

  // Y ROTATION:
  erase();
  draw_axes(shift((0,0,0)), "_0", opac=.9,bw=true);
  //draw_axes(rotX , "_1",opac=.2, bw=true);
  draw_axes(rotX * rotY , "_2",opac=1);
  drawAirplane(rotX * rotY);

  draw(arc(rotX* (0,.45,0),  rotX*(-.05,0.45,0.05),  rotX *(-.05,0.45,-.05),
	   rotX * Y),
        arrow=Arrow3(size=3), green+linewidth(.5));
  label(L=Label("$" +string(y)+"^o$"),rotX *(0,.45,.12) );
  
  // draw(arc(O, rotX *(.5,0,0),  rotY * rotX * (.5,0,0), Y),
  //      arrow=Arrow3);

  // DRAW GRADIENT SURFACES
  path3 xc1 = (O -- rotX  * (.75, 0, 0));
  path3 yc1 = (O -- rotX  * (0, .75, 0));
  path3 zc1 = (O -- rotX  * (0, 0, .75));
  drawGradientSurface(xc1, 0, y, O, rotX * Y, 30, .1, .35, red);
  drawGradientSurface(yc1, 0, y, O, rotX * Y, 30, .1, .35, green);
  drawGradientSurface(zc1, 0, y, O, rotX * Y, 30, .1, .35, blue);

  shipout("euler_nonstatic_2.png");

  // Z ROTATION:
  erase();
  draw_axes(shift((0,0,0)), "_0", opac=.9, bw=true);
  //draw_axes(rotY * rotX , "_2",opac=.2, bw=true);
  draw_axes(rotX* rotY * rotZ , "_3",opac=1,xAlign=+Y,yAlign=Z);
  drawAirplane(rotX * rotY * rotZ);

  // around Z axis
  draw(arc( rotX * rotY *(0,0,.45),
	    rotX * rotY *(-.05,0.05,0.45),
	    rotX * rotY *(.05,0.05,.45),
  	    rotX * rotY *Z),
        arrow=Arrow3(size=3), blue+linewidth(.5));
  label(L=Label("$" +string(z)+"^o$"),rotX * rotY *(0,.15,.45) );
  
  //  draw(arc(O, (0,.5,0),  rotZ * (0,.5,0), Z),
  //       arrow=Arrow3);

  // DRAW GRADIENT SURFACES
  path3 xc1 = (O -- rotX * rotY  * (.75, 0, 0));
  path3 yc1 = (O -- rotX * rotY  * (0, .75, 0));
  path3 zc1 = (O -- rotX * rotY  * (0, 0, .75));
  drawGradientSurface(xc1, 0, z, O, rotX * rotY *Z, 30, .1, .35, red);
  drawGradientSurface(yc1, 0, z, O,rotX * rotY * Z, 30, .1, .35, green);
  drawGradientSurface(zc1, 0, z, O, rotX * rotY *Z, 30, .1, .35, blue);

  shipout("euler_nonstatic_3.png");

  
}

// AXIS ANGLE FOR 45, 30, 75 xyzs
// 0.35720113, -0.89833427,  0.25573988
// 89.04182751525686

void axisAngle(triple vec, real angle)
{

  size(4.5cm, 0);
  erase();
  
  currentlight=(2.6,3.7,2.2);
  currentprojection = orthographic(3.7,3.2,1.4,target=(0,0,0));
  
  draw_axes(shift((0,0,0)), "_0", opac=1.0, bw=true);
  
  dotfactor=5;
  //dot(pnt,L=Label("$(1, 0, 0)$"),align=Z, black);
  dot(vec);

  draw((O -- vec), margin=EndDotMargin3,
       arrow=Arrow3(size=8bp),
       L=Label("$(k_x, k_y, k_z)$", position=EndPoint,align=Y),
       black+linewidth(.8));


  transform3 rotAxis = rotate(angle=angle, u=O, v=vec);

  drawAirplane(rotAxis);
  


  // Rotation symbols
  triple orthog = cross(X, vec);
  real between  = acos(dot(X, vec) / length(vec)) / 3.14159 * 180.0;
  transform3 rotToAxis = rotate(angle=between, v=orthog); 
  draw(rotToAxis * arc((.5,0,0), (.5,0.05,0.05),   (.5,0.05,-.05), X),
        arrow=Arrow3(size=3), linewidth(.5));
  label(L=Label("$\Theta$"),rotToAxis * (.5,-.1,.1) );

  // triple nose = (.23, 0, 0);
  // triple mid = (nose + rotate(angle=180, u=O, v=vec) * nose) * .5 ;
  // draw(arc(mid, nose,   rotAxis * nose, vec),
  //       arrow=Arrow3(size=7bp));

  // triple nose = (-.1, .151, 0);
  // triple mid = (nose + rotate(angle=180, u=O, v=vec) * nose) * .5 ;
  // draw(arc(mid, nose,   rotAxis * nose, vec),
  //       arrow=Arrow3(size=7bp));

  //   triple nose = (-.1, -.151, 0);
  // triple mid = (nose + rotate(angle=180, u=O, v=vec) * nose) * .5 ;
  // draw(arc(mid, nose,   rotAxis * nose, vec),
  //       arrow=Arrow3(size=7bp));


  shipout("axis_angle.png");

  
}


void rotMatrix(triple pnt, real angle)
{
   size(3.5cm, 0);
   erase();
 currentlight=(2.6,3.7,2.2);
  //currentprojection = perspective(2.6,3.8,2.2,target=(0,0,0),
  //				  up=Z,showtarget=false,autoadjust=false);
 currentprojection = orthographic(3.7,3.2,1.4,target=(0,0,0));
  
  pnt = pnt * .3;
  transform3 rotZ = rotate(angle=angle, u=O, v=Z);
  triple transPoint = rotZ * pnt;
  
  draw_axes(shift((0,0,0)), "",opac=1,bw=true);
  dotfactor=5;
  //dot(pnt,L=Label("$(1, 0, 0)$"),align=Z, black);
  dot((0,.3,0));

  //draw(arc(O, pnt, transPoint),   margin=EndDotMargin3,
  //     arrow=Arrow3(size=3bp), linewidth(.5), L=Label("$" +string(90)+"^o$"));

  draw(arc( (0,0,.5),  (-.05,0.05,0.5),    (.05,0.05,.5),
  	    Z),
    arrow=Arrow3(size=3bp), blue+linewidth(.5));
  label(L=Label("$" +string(90)+"^o$"),(.12,-.12,.5) );
  pen dashed=linetype(new real[] {8,8});
  
  draw( (.3, -.2, .1) -- (.3, 0., 0),
	arrow=Arrow3(TeXHead2), dashed, margin=EndDotMargin3,
	L=Label("$(1, 0, 0)$", position=BeginPoint,align=Relative(N)));

  draw( (-.2, .3, .1) -- (0, .3, 0),
	arrow=Arrow3(TeXHead2), dashed, margin=EndDotMargin3,
	L=Label("$(0, 1, 0)$", position=BeginPoint,align=Relative(N)));


  path3 g=(1.03,0,0)..(1,0,.03)..(.97,0,0)..(1,0,-.03)..cycle;
  g = scale3(.3) * g;
  drawGradientSurface(g, 0, 80,
		      (0,0,0), Z, 
		      30, .0, .5,
		      black);
  pen noline=linetype(new real[] {0,100000});
   draw(arc( (0,0,0),  (.3,0,0),    (0,.3,0),
  	    Z), margin=EndDotMargin3,
    arrow=Arrow3(size=7bp), noline+black+linewidth(0));
  
  shipout("rot_matrix.png");
}


//eulerStatic(45, 30, 75);
//eulerNonStatic(45, 30, 75);

//0.23072988,  0.64790345,  0.72593721
//79.6
  
axisAngle((0.23072988,  0.64790345,  0.72593721), 79.6);
//rotMatrix((1,0,0),90.);
