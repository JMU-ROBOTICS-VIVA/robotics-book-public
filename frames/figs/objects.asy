import three;
import grid3;

void draw_axes(transform3 trans, string label,
	       triple xAlign=X, triple yAlign=Y, triple zAlign=Z)
{
  //surface xTube =  rotate(90, u=O, v=Y) * scale(.01,.01, .75) *unitcylinder;
  
  draw(trans * (O -- X*.7),  red +linewidth(2),currentlight);
  draw(trans * (O -- Y*.7),  green +linewidth(2),currentlight);
  draw(trans * (O -- Z*.7),  blue +linewidth(2),currentlight);
  
  draw(trans * (O -- X *.75),
       arrow=Arrow3,
       L=Label("$x_" + label + "$", position=EndPoint,align=xAlign), red);
  draw(trans * (O -- Y *.75),
       arrow=Arrow3,
       L=Label("$y_" + label+ "$", position=EndPoint,align=yAlign), green);
  draw(trans * (O -- Z *.75),
       arrow=Arrow3,
       L=Label("$z_" + label+ "$", position=EndPoint,align=zAlign), blue);
}


surface trapezoid3(real back_width, real back_height,
		   real front_width, real front_height,
		   real length)
{
  triple center = O - length * .5 * X;
  
  triple bll = center - Y * .5 * back_width - Z * .5 * back_height;
  triple blr = center + Y * .5 * back_width - Z * .5 * back_height;
  triple bur =  center + Y * .5 * back_width + Z * .5 * back_height;
  triple bul = center - Y * .5 * back_width + Z * .5 * back_height;

  triple center = O  + length * .5 * X;

  triple fll = center - Y * .5 * front_width - Z * .5 * front_height;
  triple flr = center + Y * .5 * front_width - Z * .5 * front_height;
  triple fur = center + Y * .5 * front_width + Z * .5 * front_height;
  triple ful = center - Y * .5 * front_width + Z * .5 * front_height;

  surface back = surface(bll -- blr -- bur -- bul-- cycle);
  surface front = surface(fll -- flr -- fur -- ful-- cycle);
  surface topside  = surface(bul -- bur -- fur -- ful-- cycle);
  surface bottomside  = surface(bll -- blr -- flr -- fll-- cycle);
  surface leftside = surface(bul -- ful -- fll -- bll-- cycle);
  surface rightside = surface(bur -- fur -- flr -- blr-- cycle);

  return surface(back,front, topside, bottomside, leftside, rightside);


}



void draw_closed_unit_cylinder(transform3 trans, pen color ) 
{
  draw(trans * unitcylinder, surfacepen=color);
  draw(trans * shift((0, 0, 1.0))* unitdisk, surfacepen=color);
  draw(trans * unitdisk, surfacepen=color);
} 




void draw_table(transform3 trans, pen color)
{
  real height = .5;
  real leg_diameter = .03;
  real length = 1.0; //x
  real thickness = .03;
  real width = 1.0; // y
  surface cam = trapezoid3(1.0, .02, 1.0, .02, 1.0);

  draw(trans * shift(0, 0, height) * cam, surfacepen=color);

  draw(trans *
       shift(-length *.4, -width * .4, 0) *
       scale(leg_diameter, leg_diameter, height) *
       unitcylinder, surfacepen=color);

  draw(trans *
       shift(length *.4, -width * .4, 0) *
       scale(leg_diameter, leg_diameter, height) *
       unitcylinder, surfacepen=color);
  
  draw(trans *
       shift(-length *.4, width * .4, 0) *
       scale(leg_diameter, leg_diameter, height) *
       unitcylinder, surfacepen=color);
  
  draw(trans *
       shift(length *.4, width * .4, 0) *
       scale(leg_diameter, leg_diameter, height) *
       unitcylinder, surfacepen=color);


}


void drawStar(transform3 trans, real length, real height, pen color) {
  path star;
  for(int i=0; i < 5; ++i)
    star=star--dir(90+144i) * length;
  star=star--cycle;
  surface s = extrude(star,axis=Z*height);
  s = surface(s,surface(star), shift(0, 0, height) *surface(star));
  draw(trans * s,surfacepen=color);
}

void drawBase(transform3 trans, real height, real diameter, real wheelDiameter,
	      real opac=1.)
{
  pen lightgray = lightgray * .8 + opacity(opac);
  pen gray = gray * .8 + opacity(opac);
  
  // base
  draw_closed_unit_cylinder(trans * scale(diameter,diameter,height),
			    lightgray);

  //left wheel
  draw_closed_unit_cylinder(trans *
			    shift((0, diameter * .8,
				   height - .5 * wheelDiameter)) *
			    rotate(angle=90, u=O, v=X) *	    
			    scale(wheelDiameter, wheelDiameter, height * .5),
			    gray);

  //right wheel
  draw_closed_unit_cylinder(trans *
			    shift((0,-diameter *.8,
				   height - .5 * wheelDiameter)) *
			    rotate(angle=90, u=O, v=X)*	    
			    scale(wheelDiameter, wheelDiameter, height * .5),
			    gray);
}

// returns the camera transform.
transform3 draw_robot(transform3 trans, real cameraAngle, bool showAxes=false,
		      real opac=1.0, bool drawCamera=true)
{
  real robot_height = .075;
  real robot_diameter = .25;
  real wheel_diameter = robot_height;

  real mast_height = .2;
  real mast_diameter = .015;
  real camera_offset = -.6 * robot_diameter;

  pen lightgray = lightgray * .8 + opacity(opac);
  
  trans = trans * shift(0, 0, .5 * wheel_diameter);
  
  drawBase(trans, robot_height, robot_diameter, wheel_diameter, opac);

  transform3 camera_trans = trans *
    shift((camera_offset ,0,robot_height + mast_height)) *
    rotate(angle=cameraAngle, u=O, v=Y);

  if (drawCamera) {
    // camera mast
    draw_closed_unit_cylinder(trans * shift((camera_offset,
					     -.2 * robot_diameter,robot_height)) *
			      scale(mast_diameter,mast_diameter,mast_height),
			      lightgray);
    
    // camera mast
    draw_closed_unit_cylinder(trans * shift((camera_offset,
					     .2 * robot_diameter,robot_height)) *
			      scale(mast_diameter,mast_diameter,mast_height),
			      lightgray);
    
    // CAMERA
    surface cam = trapezoid3(.2, .03, .25, .04, .1);
    
    draw(camera_trans * cam, surfacepen=lightgray);
  }
  // AXES
  if (showAxes) {
    draw_axes(trans *shift((0, 0, .5 * robot_height)),"r");
    draw_axes(camera_trans,"c");
  }
  
  return camera_trans;
}
