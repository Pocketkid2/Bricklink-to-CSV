-- This file was created by Claude 3.5 Sonnet (refreshed) on October 25th, 2024

-- Designs table to track which design IDs we've queried
CREATE TABLE designs (
    design_id INTEGER PRIMARY KEY,
    last_checked TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    has_colors BOOLEAN NOT NULL  -- TRUE if colors exist, FALSE if checked but no colors found
);

-- Create index for faster lookups
CREATE INDEX idx_design_last_checked ON designs(last_checked);

-- Colors associated with designs
CREATE TABLE design_colors (
    design_id INTEGER NOT NULL,
    color_id INTEGER NOT NULL,
    last_checked TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (design_id, color_id),
    FOREIGN KEY (design_id) REFERENCES designs(design_id)
);

-- Create index for faster lookups
CREATE INDEX idx_design_colors ON design_colors(design_id, color_id);

-- Elements table for storing unique elements and their properties
CREATE TABLE elements (
    element_id INTEGER PRIMARY KEY,
    design_id INTEGER NOT NULL,
    color_id INTEGER NOT NULL,
    sold_by_lego BOOLEAN,  -- NULL if not checked yet
    is_bestseller BOOLEAN,  -- NULL if not checked yet
    price DECIMAL(10,2),   -- NULL if not sold by LEGO
    last_checked TIMESTAMP,  -- When we last checked the element's status
    FOREIGN KEY (design_id, color_id) REFERENCES design_colors(design_id, color_id)
);

-- Create indexes for common queries
CREATE INDEX idx_elements_design_color ON elements(design_id, color_id);
CREATE INDEX idx_elements_sold_by_lego ON elements(sold_by_lego);

-- Create views for common queries
CREATE VIEW available_elements AS
SELECT 
    e.element_id,
    e.design_id,
    e.color_id,
    e.price,
    e.is_bestseller
FROM elements e
WHERE e.sold_by_lego = TRUE;

-- Example queries for your common operations:

-- 1. Check if design_id exists and has been checked:
-- SELECT EXISTS(SELECT 1 FROM designs WHERE design_id = ?) as exists_in_db;

-- 2. Get available elements for design_id and color_id combination:
-- SELECT element_id, price, is_bestseller 
-- FROM elements 
-- WHERE design_id = ? AND color_id = ? AND sold_by_lego = TRUE;

-- 3. Find elements needing status check:
-- SELECT element_id, design_id, color_id 
-- FROM elements 
-- WHERE sold_by_lego IS NULL;
