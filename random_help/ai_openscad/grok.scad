// Parametric Bottom Enclosure Box for PCB

// PCB Parameters
pcb_length = 75; // mm
pcb_width = 75; // mm
pcb_corner_radius = 4; // mm
hole_diameter = 3; // mm
hole_offset = 4; // mm from each corner

// Box Parameters
clearance = 0.5; // mm around PCB
wall_height = 8; // mm
wall_thickness = 2; // mm (adjustable)
base_thickness = 2; // mm (adjustable)
post_height = 5; // mm
post_radius = 3; // mm (adjustable, should be larger than pin)
pin_height = 3; // mm
pin_clearance = 0.1; // mm for fit

// Calculated Values (do not edit)
inner_length = pcb_length + 2 * clearance;
inner_width = pcb_width + 2 * clearance;
inner_corner_radius = pcb_corner_radius + clearance;
outer_length = inner_length + 2 * wall_thickness;
outer_width = inner_width + 2 * wall_thickness;
outer_corner_radius = inner_corner_radius + wall_thickness;
pin_radius = (hole_diameter / 2) - pin_clearance;

// Hole positions relative to center
hole_bl = [-pcb_length/2 + hole_offset, -pcb_width/2 + hole_offset];
hole_br = [pcb_length/2 - hole_offset, -pcb_width/2 + hole_offset];
hole_tr = [pcb_length/2 - hole_offset, pcb_width/2 - hole_offset];
hole_tl = [-pcb_length/2 + hole_offset, pcb_width/2 - hole_offset];

// Module for rounded square (2D)
module rounded_square(width, length, radius) {
    hull() {
        translate([radius, radius]) circle(r = radius);
        translate([width - radius, radius]) circle(r = radius);
        translate([width - radius, length - radius]) circle(r = radius);
        translate([radius, length - radius]) circle(r = radius);
    }
}

// Main model
union() {
    // Box shell
    difference() {
        // Outer solid
        linear_extrude(height = base_thickness + wall_height)
            translate([-outer_length/2, -outer_width/2])
                rounded_square(outer_length, outer_width, outer_corner_radius);
        
        // Inner cavity
        translate([0, 0, base_thickness])
            linear_extrude(height = wall_height + 1)
                translate([-inner_length/2, -inner_width/2])
                    rounded_square(inner_length, inner_width, inner_corner_radius);
    }
    
    // Mounting posts and pins
    for (pos = [hole_bl, hole_br, hole_tr, hole_tl]) {
        // Post
        translate([pos[0], pos[1], base_thickness])
            cylinder(h = post_height, r = post_radius, $fn = 50);
        
        // Pin
        translate([pos[0], pos[1], base_thickness + post_height])
            cylinder(h = pin_height, r = pin_radius, $fn = 50);
    }
}