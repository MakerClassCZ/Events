/*
OpenSCAD Enclosure Script
* Generates a bottom enclosure box for a PCB with rounded corners
and mounting posts.
 */
// --- OpenSCAD Global Settings ---
$fn = 100; // Resolution for curved surfaces
// ==========================================================
// --- Parameters (Adjust these values) ---
// ==========================================================
// --- 1. PCB Specifications ---
pcb_width         = 75;  // PCB width in mm
pcb_length        = 75;  // PCB length in mm
pcb_corner_radius = 4;   // Corner radius of the PCB
pcb_hole_diameter = 3;   // Diameter of the mounting holes in the PCB
pcb_hole_inset    = 4;   // Distance from the outer edge to the center of the hole
pcb_thickness     = 1.6; // Assumed PCB thickness (for visualization)
// --- 2. Enclosure Specifications ---
clearance         = 0.5; // Space between PCB and inner wall
wall_thickness    = 2;   // Thickness of the enclosure walls
wall_height       = 8;   // Total height of the wall from the base plate
base_thickness    = 2;   // Thickness of the bottom plate
// --- 3. Mounting Post Specifications ---
post_base_height    = 5;   // Height of the standoff post (PCB rests on this)
post_pin_height     = 3;   // Height of the locating pin (goes through PCB hole)
post_outer_diameter = 7;   // Outer diameter of the cylindrical post
pin_clearance       = 0.3; // How much smaller the pin is than the PCB hole
// ==========================================================
// --- Calculated Variables (Do not edit) ---
// ==========================================================
// --- Inner Dimensions ---
inner_width  = pcb_width + 2 * clearance;
inner_length = pcb_length + 2 * clearance;
inner_radius = pcb_corner_radius + clearance;
// --- Outer Dimensions ---
outer_width  = inner_width + 2 * wall_thickness;
outer_length = inner_length + 2 * wall_thickness;
outer_radius = inner_radius + wall_thickness;
// --- Post/Pin Dimensions ---
post_pin_diameter = pcb_hole_diameter - pin_clearance;
// --- Post Positions (relative to center) ---
hole_pos_x = pcb_width / 2 - pcb_hole_inset;
hole_pos_y = pcb_length / 2 - pcb_hole_inset;
// ==========================================================
// --- Helper Modules ---
// ==========================================================
/*
Creates a 2D rounded rectangle centered at origin
size: [width, length]
radius: corner radius
 */
module rounded_rectangle(size, radius) {
    w = size[0];
    l = size[1];
    minkowski() {
        square([w - 2 * radius, l - 2 * radius], center = true);
        circle(r = radius);
    }
}
// ==========================================================
// --- Component Modules ---
// ==========================================================
/*
Creates the main box (base + walls)
 */
module main_box() {
    difference() {
        // --- 1. Outer Shell (Solid Block) ---
        linear_extrude(height = base_thickness + wall_height) {
            rounded_rectangle(size = [outer_width, outer_length], radius = outer_radius);
        }
        // --- 2. Inner Cutout (Hollows the box) ---
        translate([0, 0, base_thickness]) {
            linear_extrude(height = wall_height + 1) { // +1 for a clean boolean cut
                rounded_rectangle(size = [inner_width, inner_length], radius = inner_radius);
            }
        }
    }
}
/*
Creates a single mounting post with a locating pin
 */
module mounting_post() {
    union() {
        // --- 1. Post Base (Standoff) ---
        cylinder(h = post_base_height, d = post_outer_diameter, center = false);
        // --- 2. Locating Pin ---
        translate([0, 0, post_base_height]) {
            cylinder(h = post_pin_height, d = post_pin_diameter, center = false);
        }
    }
}
/*
Creates and positions all four mounting posts
 */
module all_posts() {
    // Move posts up to sit on the base plate
    translate([0, 0, base_thickness]) {
        // Top-Right
        translate([hole_pos_x, hole_pos_y, 0])
            mounting_post();
        // Top-Left
        translate([-hole_pos_x, hole_pos_y, 0])
            mounting_post();
        // Bottom-Left
        translate([-hole_pos_x, -hole_pos_y, 0])
            mounting_post();
        // Bottom-Right
        translate([hole_pos_x, -hole_pos_y, 0])
            mounting_post();
    }
}
/*
Creates a translucent preview of the PCB
(Uses '%' to make it a background modifier object in OpenSCAD)
 */
module preview_pcb() {
    %translate([0, 0, base_thickness + post_base_height]) {
        color("green", 0.5) {
            linear_extrude(height = pcb_thickness) {
                rounded_rectangle(size = [pcb_width, pcb_length], radius = pcb_corner_radius);
            }
        }
    }
}
// ==========================================================
// --- Main Assembly ---
// ==========================================================
// --- 1. Build the Enclosure ---
union() {
    main_box();
    all_posts();
}
// --- 2. Show PCB Preview (optional) ---
// Uncomment the line below to see a preview of the PCB placement
// preview_pcb();