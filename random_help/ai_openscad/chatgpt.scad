//
// Bottom enclosure for 75x75mm PCB (rounded corners, mounting posts + locating pins)
// Fully parametric; adjust values in the PARAMETERS section.
//

// ---------- PARAMETERS ----------
/* PCB */
pcb_w              = 75;          // mm
pcb_h              = 75;          // mm
pcb_corner_r       = 4;           // mm (PCB corner radius)
hole_d             = 3;           // mm (PCB mounting hole diameter)
hole_edge_offset   = 4;           // mm (center of holes from each PCB edge)

/* Enclosure clearances & geometry */
clearance_xy       = 0.5;         // mm (free space around PCB on each side)
base_th            = 2;           // mm (bottom plate thickness)
wall_th            = 2;           // mm (perimeter wall thickness)
wall_h             = 8;           // mm (height of walls above base)
corner_r_extra     = 0;           // mm (additive tweak for inner corner radius if you want a hair more)
$fn                = 64;          // segment resolution for cylinders/fillets

/* Mounting posts */
post_h             = 5;           // mm (post height above base)
post_d             = 8;           // mm (post outer diameter)

/* Locating pins (to fit into the PCB's 3mm holes) */
pin_h              = 3;           // mm (height of locating pin)
pin_fit_clearance  = 0.3;         // mm (diameter undersize vs. hole_d; e.g., 0.3 => 2.7mm for 3.0mm hole)
pin_d              = hole_d - pin_fit_clearance;

/* Derived (do not edit) */
inner_w            = pcb_w + 2*clearance_xy;
inner_h            = pcb_h + 2*clearance_xy;
inner_r            = pcb_corner_r + clearance_xy + corner_r_extra;
outer_w            = inner_w + 2*wall_th;
outer_h            = inner_h + 2*wall_th;
outer_r            = inner_r + wall_th;

// ---------- HELPERS ----------
module rounded_rect_2d(w, h, r, center=true) {
    // Robust rounded rectangle using offset on a centered square
    // r = corner radius
    // Requires r <= min(w,h)/2
    translate(center ? [0,0] : [w/2, h/2])
        offset(r=r)
            offset(delta=-r)
                square([w, h], center=center);
}

module enclosure_outline_2d() {
    rounded_rect_2d(outer_w, outer_h, outer_r, center=true);
}

module cavity_outline_2d() {
    rounded_rect_2d(inner_w, inner_h, inner_r, center=true);
}

function hole_positions() =
    // Four hole centers relative to (0,0) at enclosure center
    let(dx = pcb_w/2 - hole_edge_offset,
        dy = pcb_h/2 - hole_edge_offset)
    [
        [ +dx, +dy ],
        [ -dx, +dy ],
        [ -dx, -dy ],
        [ +dx, -dy ]
    ];

// ---------- MODEL ----------
module base_plate() {
    linear_extrude(height = base_th)
        enclosure_outline_2d();
}

module perimeter_walls() {
    // Walls above the base
    translate([0,0,base_th])
        linear_extrude(height = wall_h)
            difference() {
                enclosure_outline_2d();
                cavity_outline_2d();
            }
}

module mounting_post_at(x, y) {
    // Solid post + locating pin
    translate([x, y, base_th])
        cylinder(h = post_h, d = post_d);
    translate([x, y, base_th + post_h])
        cylinder(h = pin_h, d = pin_d);
}

module mounting_posts() {
    for (p = hole_positions())
        mounting_post_at(p[0], p[1]);
}

module enclosure_bottom() {
    union() {
        base_plate();
        perimeter_walls();
        mounting_posts();
    }
}

// ---------- PREVIEW ----------
enclosure_bottom();
