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
pair sceneLabelLoc = (-30, 70);
pair cFreeLabelLoc = (-10, 30);

pair q_i = (-20, 30);
pair q_g = (55, 58);

// Obstacle parameters (two triangles)
pair box1LL = (20, 0);
pair box1Size = (50, 20);
pair box1Center = box1LL + .5 * box1Size;

pair box2LL = (20, 40);
pair box2Size = (50, 20);
pair box2Center = box2LL + .5 * box2Size;



// Path that the robot would take to trace Cobs around box
path boxPath = 
  box1LL + (-rightOffset, 0) --
  box1LL + (-rightOffset, box1Size.y) --
  
  box1LL + (-rightOffset + 22.36, box1Size.y + 10) -- // NOTCH
  
  box2LL + (-rightOffset, 0) --
  box2LL + (-rightOffset, box2Size.y) --
  box2LL + (-leftOffset,
	    box2Size.y + robot_height/2) --
  box2LL + (-leftOffset + box2Size.x,
	    robot_height/2 + box2Size.y) --
  box1LL + (-leftOffset + box1Size.x,
	    -robot_height/2) --
  box1LL + (-leftOffset, -robot_height/2) --
  cycle;
  

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
  
  filldraw(box(box1LL, box1LL + box1Size), mediumgray);
  label(L=Label("$\mathcal{O}_2$"), box1Center);
  
  filldraw(box(box2LL, box2LL + box2Size), mediumgray);
  label(L=Label("$\mathcal{O}_2$"), box2Center);


}

// Draw Cobs and Cfree
void drawFinal() {
  // Show the final result
  filldraw(boxPath, mediumgray);

  label(Label("$\mathcal{C}$"), sceneLabelLoc);
  label(Label("$\mathcal{C}_{free}$"), cFreeLabelLoc);

  label(Label("$\mathcal{C}_{obs}$",(box1Center + box2Center) / 2.));
  dot((box1LL.x + box1Size.x + 20, box1LL.y - 20), invisible);

}



// Create the full workspace figure including labels
void workspaceFigure() {
  drawStart();
  path bot_path = drawRobot(q_i);
  filldraw(bot_path, mediumgray);
  dot(q_i);
  

  dot((box1LL.x + box1Size.x + 10, box1LL.y - 10), invisible);
}



settings.outformat="pdf";

  
size(1.5inch,0);
workspaceFigure();
shipout("workspace_hw", format="pdf");
    
erase();
drawFinal();
shipout("c_obs_final_hw", format="pdf");
  


