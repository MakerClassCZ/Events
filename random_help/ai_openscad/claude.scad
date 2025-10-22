// ========================================
// PCB Bottom Enclosure Box - OpenSCAD Script
// ========================================
// Fully parametric design for easy customization

// ========================================
// PARAMETERS - Adjust these as needed
// ========================================

// PCB Dimensions
pcb_length = 75;           // PCB length in mm
pcb_width = 75;            // PCB width in mm
pcb_corner_radius = 4;     // PCB corner radius in mm
pcb_hole_diameter = 3;     // Mounting hole diameter in mm
pcb_hole_offset = 4;       // Distance from PCB edge to hole center in mm

// Box Dimensions
clearance = 0.5;           // Clearance around PCB in mm
wall_thickness = 2;        // Thickness of the walls in mm
wall_height = 8;           // Height of the walls in mm
base_thickness = 2;        // Thickness of the base plate in mm

// Mounting Posts
post_diameter = 6;         // Diameter of mounting posts in mm
post_height = 5;           // Height of mounting posts from base in mm
pin_diameter = 2.8;        // Diameter of locating pins (slightly smaller than hole)
pin_height = 3;            // Height of locating pins above post in mm
pin_chamfer = 0.3;         // Chamfer on pin tip for easy insertion in mm

// Rendering Quality
$fn = 50;                  // Fragment number for circles (higher = smoother)

// ========================================
// CALCULATED VALUES
// ========================================

// Inner cavity dimensions (PCB + clearance)
inner_length = pcb_length + 2 * clearance;
inner_width = pcb_width + 2 * clearance;

// Outer box dimensions
outer_length = inner_length + 2 * wall_thickness;
outer_width = inner_width + 2 * wall_thickness;

// Box corner radius (matches PCB + clearance)
box_corner_radius = pcb_corner_radius + clearance;
outer_corner_radius = box_corner_radius + wall_thickness;

// Mounting post positions (relative to PCB center)
post_offset_x = pcb_length / 2 - pcb_hole_offset;
post_offset_y = pcb_width / 2 - pcb_hole_offset;

// ========================================
// MAIN MODULE
// ========================================

module pcb_bottom_enclosure() {
    difference() {
        union() {
            // Base plate with walls
            base_with_walls();
            
            // Mounting posts with locating pins
            mounting_posts();
        }
        
        // No subtractions needed for bottom enclosure
    }
}

// ========================================
// COMPONENT MODULES
// ========================================

// Base plate with perimeter walls
module base_with_walls() {
    difference() {
        // Outer shell (base + walls)
        rounded_box(
            outer_length, 
            outer_width, 
            base_thickness + wall_height, 
            outer_corner_radius
        );
        
        // Inner cavity
        translate([0, 0, base_thickness])
            rounded_box(
                inner_length, 
                inner_width, 
                wall_height + 1,  // +1 to ensure clean boolean operation
                box_corner_radius
            );
    }
}

// Mounting posts with locating pins
module mounting_posts() {
    // Create posts at all four corners
    for (x = [-1, 1]) {
        for (y = [-1, 1]) {
            translate([x * post_offset_x, y * post_offset_y, base_thickness]) {
                // Mounting post
                cylinder(h = post_height, d = post_diameter);
                
                // Locating pin with chamfer
                translate([0, 0, post_height])
                    locating_pin();
            }
        }
    }
}

// Locating pin with chamfered tip
module locating_pin() {
    cylinder(h = pin_height - pin_chamfer, d = pin_diameter);
    
    // Chamfered tip
    translate([0, 0, pin_height - pin_chamfer])
        cylinder(h = pin_chamfer, d1 = pin_diameter, d2 = pin_diameter - 2 * pin_chamfer);
}

// Rounded box module (centered)
module rounded_box(length, width, height, radius) {
    hull() {
        for (x = [-1, 1]) {
            for (y = [-1, 1]) {
                translate([
                    x * (length / 2 - radius), 
                    y * (width / 2 - radius), 
                    0
                ])
                    cylinder(h = height, r = radius);
            }
        }
    }
}

// ========================================
// RENDER
// ========================================

pcb_bottom_enclosure();

// ========================================
// HELPER VISUALIZATION (uncomment to see PCB reference)
// ========================================

// Uncomment the section below to visualize the PCB in the enclosure
/*
%translate([0, 0, base_thickness + post_height]) {
    difference() {
        rounded_box(pcb_length, pcb_width, 1.6, pcb_corner_radius);
        
        // Mounting holes
        for (x = [-1, 1]) {
            for (y = [-1, 1]) {
                translate([
                    x * post_offset_x, 
                    y * post_offset_y, 
                    -0.1
                ])
                    cylinder(h = 2, d = pcb_hole_diameter);
            }
        }
    }
}
*/
