



from city_metrix.layers import *

BASE_URL = "dev.cities-data-api.wri.org"


import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject

from tests.resources.bbox_constants import BBOX_SMALL


def align_rasters_with_nodata(lst_path, worldpop_path, output_path, manual_nodata=None):
    """
    Resamples 30m LST raster to align perfectly with 100m WorldPop grid.
    
    Args:
        lst_path (str): Path to LST source raster (30m).
        worldpop_path (str): Path to WorldPop reference raster (100m).
        output_path (str): Where to save the new aligned raster.
        manual_nodata (float): Force a NoData value (e.g. -9999) if missing in source.
    """
    
    # 1. Open Reference (WorldPop) to capture its grid/geometry
    with rasterio.open(worldpop_path) as ref_ds:
        ref_transform = ref_ds.transform
        ref_crs = ref_ds.crs
        ref_height = ref_ds.height
        ref_width = ref_ds.width
        # Copy profile to use as a template for output
        out_profile = ref_ds.profile.copy()

    # 2. Open Source (LST)
    with rasterio.open(lst_path) as src_ds:
        
        # --- Handle NoData Logic ---
        if manual_nodata is not None:
            nodata_val = manual_nodata
        elif src_ds.nodata is not None:
            nodata_val = src_ds.nodata
        else:
            nodata_val = -9999 
            print(f"Warning: No NoData found in LST metadata. Defaulting to {nodata_val}")

        # --- Prepare Output Array ---
        # Use float32 to preserve temperature precision (e.g. 24.5 degrees)
        # Initialize with NoData so empty areas are marked correctly
        destination_array = np.full(
            (src_ds.count, ref_height, ref_width), 
            fill_value=nodata_val, 
            dtype='float32' 
        )

        # --- Perform Reprojection ---
        reproject(
            source=rasterio.band(src_ds, list(range(1, src_ds.count + 1))),
            destination=destination_array,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            # Use bilinear (or average) for Temperature. NEVER use nearest.
            resampling=Resampling.bilinear, 
            src_nodata=nodata_val,
            dst_nodata=nodata_val
        )

        # --- Update Metadata ---
        out_profile.update({
            'driver': 'GTiff',
            'height': ref_height,
            'width': ref_width,
            'transform': ref_transform,
            'crs': ref_crs,
            'count': src_ds.count,
            'dtype': 'float32',  # Explicitly save as float
            'nodata': nodata_val
        })

        # 3. Write Result
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            dst.write(destination_array)
            print(f"Success! LST aligned to WorldPop grid saved at: {output_path}")


import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject


def align_lst_robust(lst_path, worldpop_path, output_path, manual_nodata=None):
    
    with rasterio.open(worldpop_path) as ref_ds:
        ref_transform = ref_ds.transform
        ref_crs = ref_ds.crs
        ref_height = ref_ds.height
        ref_width = ref_ds.width
        out_profile = ref_ds.profile.copy()

    with rasterio.open(lst_path) as src_ds:
        
        if manual_nodata is not None:
            src_nodata = manual_nodata
        elif src_ds.nodata is not None:
            src_nodata = src_ds.nodata
        else:
            src_nodata = -999
        
        destination_array = np.full(
            (src_ds.count, ref_height, ref_width), 
            fill_value=src_nodata, 
            dtype='float32'
        )

        reproject(
            source=rasterio.band(src_ds, list(range(1, src_ds.count + 1))),
            destination=destination_array,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.average, 
            src_nodata=src_nodata,
            dst_nodata=src_nodata
        )

        out_profile.update({
            'driver': 'GTiff',
            'height': ref_height,
            'width': ref_width,
            'transform': ref_transform,
            'crs': ref_crs,
            'count': src_ds.count,
            'dtype': 'float32',
            'nodata': src_nodata
        })

        with rasterio.open(output_path, 'w', **out_profile) as dst:
            dst.write(destination_array)
            print(f"Saved to {output_path}")


import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject


def align_lst_permissivew(lst_path, worldpop_path, output_path):
    """
    Manually calculates average by summing values and counts.
    Ensures EVERY pixel with valid overlap gets a value (no skipped edges).
    """
    
    # 1. Open Reference (WorldPop) to get the target grid
    with rasterio.open(worldpop_path) as ref_ds:
        ref_transform = ref_ds.transform
        ref_crs = ref_ds.crs
        ref_height = ref_ds.height
        ref_width = ref_ds.width
        out_profile = ref_ds.profile.copy()

    # 2. Open Source (LST)
    with rasterio.open(lst_path) as src_ds:
        src_nodata = src_ds.nodata if src_ds.nodata is not None else -999
        
        # Read data and create a mask
        lst_data = src_ds.read(1)
        
        # Create 'Value' array: Replace NoData with 0.0 for summing
        # (Must be float to store temperature sums)
        # valid_mask = (lst_data != src_nodata)
        valid_mask = (lst_data != src_nodata)
        values_to_sum = np.where(valid_mask, lst_data, 0.0).astype('float32')
        
        # Create 'Weight' array: 1.0 where data exists, 0.0 where NoData
        weights_to_sum = np.where(valid_mask, 1.0, 0.0).astype('float32')

        # --- STEP 3: Create Destination Arrays ---
        # One for the total temperature, one for the count of pixels
        sum_array = np.zeros((ref_height, ref_width), dtype='float32')
        count_array = np.zeros((ref_height, ref_width), dtype='float32')

        # --- STEP 4: Reproject Both Using SUM ---
        # This adds up the temperature values
        reproject(
            source=values_to_sum,
            destination=sum_array,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.sum, # CRITICAL: Sum, not Average
        )
        
        # This adds up the number of valid pixels (the weight)
        reproject(
            source=weights_to_sum,
            destination=count_array,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.sum, # CRITICAL: Sum, not Average
        )

        # --- STEP 5: Calculate Average (Sum / Count) ---
        # Avoid division by zero
        out_data = np.full_like(sum_array, src_nodata) # Initialize with NoData
        
        # Only update pixels where we actually found data (count > 0)
        valid_pixels = count_array > 0
        out_data[valid_pixels] = sum_array[valid_pixels] / count_array[valid_pixels]

        # Update metadata
        out_profile.update({
            'driver': 'GTiff',
            'height': ref_height,
            'width': ref_width,
            'transform': ref_transform,
            'crs': ref_crs,
            'dtype': 'float32',
            'nodata': src_nodata
        })

        # Save
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            dst.write(out_data, 1)
            print(f"Saved permissive aligned raster to: {output_path}")

        with rasterio.open("weights_to_sum.tif", 'w', **out_profile) as dst:
            dst.write(weights_to_sum, 1)
            print(f"Saved permissive aligned raster to: {output_path}")

        with rasterio.open("count.tif", 'w', **out_profile) as dst:
            dst.write(count_array, 1)
            print(f"Saved permissive aligned raster to: {output_path}")
# --- USAGE ---
# align_lst_permissive('lst_30m.tif', 'worldpop_100m.tif', 'lst_permissive.tif')
lst_array = HighLandSurfaceTemperature().get_data(bbox=BBOX_SMALL)
lst_array.rio.to_raster(raster_path="lst_final.tif", driver="GTiff")

# wp_array = WorldPop().get_data(bbox=BBOX_SMALL)
# wp_array.rio.to_raster(raster_path="world_pop.tif", driver="GTiff")


import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject


def align_lst_gapfill(lst_path, worldpop_path, output_path):
    """
    1. Computes weighted average of LST for the WorldPop grid.
    2. Identifies 'gaps' (NoData) that occurred at the edges.
    3. Fills those specific gaps using Nearest Neighbor (taking the pixel it falls under).
    """
    
    # 1. Open Reference (WorldPop) to get the strict target grid
    with rasterio.open(worldpop_path) as ref_ds:
        ref_data = ref_ds.read(1)
        ref_meta = ref_ds.profile.copy()
        ref_transform = ref_ds.transform
        ref_crs = ref_ds.crs
        ref_nodata = ref_ds.nodata if ref_ds.nodata is not None else -999
        
        # Create a boolean mask of where WorldPop actually expects data
        # (We only care about filling pixels where WorldPop is VALID)
        target_valid_mask = (ref_data != ref_nodata)

    # 2. Open Source (LST)
    with rasterio.open(lst_path) as src_ds:
        src_nodata = src_ds.nodata if src_ds.nodata is not None else -999
        
        # Prepare Output Array
        # Initialize with NaNs (or a distinct NoData value)
        out_data = np.full(ref_data.shape, np.nan, dtype='float32')

        # --- STEP A: The "Average" Pass (High Quality) ---
        # This computes the mean of all LST pixels under the target pixel.
        # It works great for the center, but often fails at edges (the "Pink Gaps").
        print("Pass 1: Computing Average...")
        reproject(
            source=rasterio.band(src_ds, 1),
            destination=out_data,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=ref_transform,
            dst_crs=ref_crs,
            resampling=Resampling.average, # Strict averaging
            src_nodata=src_nodata,
            dst_nodata=np.nan # Use NaN temporarily for easier math
        )

        # --- STEP B: The "Nearest" Pass (Edge Fixing) ---
        # We assume that if 'Average' returned NaN but WorldPop is valid, 
        # it's an edge case. We force it to take the value of the LST pixel it touches.
        
        # Identify Gaps: pixels that are valid in WorldPop but NaN in our output
        gaps_mask = target_valid_mask & np.isnan(out_data)
        
        if np.any(gaps_mask):
            print(f"Pass 2: Filling {np.sum(gaps_mask)} gap pixels using Nearest Neighbor...")
            
            # Create a temporary array just for the nearest neighbor values
            nearest_fill = np.full(ref_data.shape, np.nan, dtype='float32')
            
            reproject(
                source=rasterio.band(src_ds, 1),
                destination=nearest_fill,
                src_transform=src_ds.transform,
                src_crs=src_ds.crs,
                dst_transform=ref_transform,
                dst_crs=ref_crs,
                resampling=Resampling.nearest, # FORCE value capture
                src_nodata=src_nodata,
                dst_nodata=np.nan
            )
            
            # Fill the holes!
            # Where we have a gap, copy the value from 'nearest_fill'
            out_data[gaps_mask] = nearest_fill[gaps_mask]

        # --- STEP C: Clean up and Save ---
        # Replace remaining NaNs (areas outside both WorldPop and LST) with final NoData
        final_nodata_value = -9999.0
        out_data = np.where(np.isnan(out_data), final_nodata_value, out_data)

        ref_meta.update({
            'driver': 'GTiff',
            'dtype': 'float32',
            'nodata': final_nodata_value,
            'count': 1
        })

        with rasterio.open(output_path, 'w', **ref_meta) as dst:
            dst.write(out_data, 1)
            print(f"Success. Saved gap-filled raster to: {output_path}")

# Run the function
# align_lst_gapfill("lst.tif", "world_pop.tif", "lst_aligned_filled.tif")


import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject


def align_lst_permissive(lst_path, worldpop_path, output_path):
    """
    1. Creates a blank grid based on WorldPop dimensions.
    2. Fills it by averaging ALL valid LST pixels that overlap each cell.
    3. Guarantees no edge gaps (permissive alignment).
    """
    
    # --- STEP 1: Get Target Grid from WorldPop ---
    # We only read the profile/transform. We DO NOT read the data.
    with rasterio.open(worldpop_path) as ref_ds:
        dst_transform = ref_ds.transform
        dst_crs = ref_ds.crs
        dst_height = ref_ds.height
        dst_width = ref_ds.width
        dst_profile = ref_ds.profile.copy()

    # --- STEP 2: Prepare Source (LST) Data ---
    with rasterio.open(lst_path) as src_ds:
        src_nodata = src_ds.nodata if src_ds.nodata is not None else -999
        lst_data = src_ds.read(1)

        # Create "Clean" Arrays for math
        # 1. Mask of valid data (True where we have LST, False where NoData)
        valid_mask = (lst_data != src_nodata)
        
        # 2. Values to Sum: Replace NoData with 0.0 so we can add them up safely
        # (Where mask is True, keep data. Where False, use 0.0)
        values_source = np.where(valid_mask, lst_data, 0.0).astype('float32')
        
        # 3. Weights to Sum: 1.0 where we have data, 0.0 where we don't
        weights_source = np.where(valid_mask, 1.0, 0.0).astype('float32')

        # --- STEP 3: Initialize Destination Arrays ---
        # These match the WorldPop dimensions exactly
        dst_sum = np.zeros((dst_height, dst_width), dtype='float32')
        dst_weight = np.zeros((dst_height, dst_width), dtype='float32')


        with rasterio.open("dst_sum.tif", 'w', **dst_profile) as dst:
            dst.write(dst_sum, 1)
            print(f"Saved strictly LST-derived grid to: {output_path}")
        # --- STEP 4: Reproject (The Magic Step) ---
        # We use Resampling.sum to accumulate all overlapping pixel contributions.
        # CRITICAL: We pass src_nodata=None. We want to treat 0.0 as a real number 
        # to ensure it gets added to the total.
        
        # A. Accumulate Values
        reproject(
            source=values_source,
            destination=dst_sum,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.sum, 
        )

        # B. Accumulate Weights (Counts)
        reproject(
            source=weights_source,
            destination=dst_weight,
            src_transform=src_ds.transform,
            src_crs=src_ds.crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.sum,
        )

    # --- STEP 5: Calculate Average (Sum / Weight) ---
    # Initialize output with NoData
    out_nodata = -999.0
    final_output = np.full((dst_height, dst_width), out_nodata, dtype='float32')

    # Only divide where we actually have data (weight > 0)
    # This handles the edges perfectly: even if weight is 0.1 (partial overlap),
    # the math works: (Value * 0.1) / 0.1 = Value.
    valid_pixels = dst_weight > 0
    final_output[valid_pixels] = dst_sum[valid_pixels] / dst_weight[valid_pixels]

    # --- STEP 6: Save Result ---
    dst_profile.update({
        'dtype': 'float32',
        'nodata': out_nodata,
        'count': 1,
        'compress': 'lzw'
    })

    with rasterio.open(output_path, 'w', **dst_profile) as dst:
        dst.write(final_output, 1)
        print(f"Saved strictly LST-derived grid to: {output_path}")


# Example Usage
# align_lst_permissive("lst_input.tif", "worldpop_grid.tif", "lst_aligned.tif")

# align_lst_permissive("lst.tif", "world_pop.tif", output_path="aligned_lst.tif")


import numpy as np
import rasterio
from scipy.interpolate import NearestNDInterpolator


def align_lst_manual(lst_path, worldpop_path, output_path):
    
    # --- 1. Load Reference Grid (WorldPop) ---
    with rasterio.open(worldpop_path) as ref:
        dst_height = ref.height
        dst_width = ref.width
        dst_transform = ref.transform
        dst_profile = ref.profile.copy()
        # We need the inverse transform to convert Lat/Lon -> Row/Col
        dst_transform_inv = ~ref.transform

    # --- 2. Load Source Points (LST) ---
    with rasterio.open(lst_path) as src:
        lst_data = src.read(1)
        src_nodata = src.nodata if src.nodata is not None else -9999
        
        # Create a mask of valid LST pixels
        valid_mask = (lst_data != src_nodata) & (~np.isnan(lst_data))
        
        # Get the Row, Col indices of all VALID LST pixels
        # (This flattens the array, giving us a list of every valid pixel)
        rows, cols = np.where(valid_mask)
        values = lst_data[rows, cols]
        
        # Convert LST Row/Col -> Lat/Lon (Spatial Coordinates)
        # xs = Longitude, ys = Latitude
        xs, ys = rasterio.transform.xy(src.transform, rows, cols, offset='center')
        
        # Convert lists to numpy arrays for speed
        xs = np.array(xs)
        ys = np.array(ys)

    # --- 3. Map LST Points to WorldPop Grid ---
    # Apply the Inverse WorldPop Transform:
    # This tells us: "For this LST coordinate, which WorldPop Row/Col is it in?"
    # The output are floating point indices (e.g., row 10.5, col 5.2)
    dst_cols_float, dst_rows_float = dst_transform_inv * (xs, ys)
    
    # Round down to integer indices to find the specific grid cell
    dst_rows = np.floor(dst_rows_float).astype(int)
    dst_cols = np.floor(dst_cols_float).astype(int)

    # --- 4. Filter "Out of Bounds" Points ---
    # Keep only points that actually fall inside the WorldPop image dimensions
    keep = (
        (dst_rows >= 0) & (dst_rows < dst_height) &
        (dst_cols >= 0) & (dst_cols < dst_width)
    )
    
    # Filter our lists
    final_rows = dst_rows[keep]
    final_cols = dst_cols[keep]
    final_values = values[keep]

    # --- 5. Aggregate (The "Manual Average") ---
    # Create empty grids to accumulate sums and counts
    sum_grid = np.zeros((dst_height, dst_width), dtype='float32')
    count_grid = np.zeros((dst_height, dst_width), dtype='float32')
    
    # MAGIC STEP: np.add.at allows us to sum values at specific indices extremely fast
    # If multiple LST pixels hit the same WorldPop pixel, this adds them up.
    np.add.at(sum_grid, (final_rows, final_cols), final_values)
    np.add.at(count_grid, (final_rows, final_cols), 1)

    # Calculate Average where we have data
    out_data = np.full((dst_height, dst_width), np.nan, dtype='float32')
    
    has_data = count_grid > 0
    out_data[has_data] = sum_grid[has_data] / count_grid[has_data]

    # --- 6. Fill Gaps (Manual Nearest Neighbor) ---
    # Even with the logic above, if LST pixels are bigger than WorldPop pixels,
    # some WorldPop pixels might get "skipped" (count = 0).
    # We fill these empty spots using Scipy's Nearest Interpolator.
    
    mask_missing = np.isnan(out_data)
    
    if np.any(mask_missing):
        print("Filling gaps manually...")
        # Get coordinates of all pixels that HAVE data
        valid_r, valid_c = np.where(~mask_missing)
        valid_vals = out_data[valid_r, valid_c]
        
        # Build interpolator (this acts like a KD-Tree)
        # It learns the surface defined by the valid pixels
        interp = NearestNDInterpolator(list(zip(valid_r, valid_c)), valid_vals)
        
        # Get coordinates of pixels that are MISSING data
        missing_r, missing_c = np.where(mask_missing)
        
        # Predict their values
        filled_vals = interp(missing_r, missing_c)
        
        # Fill them in
        out_data[missing_r, missing_c] = filled_vals

    # --- 7. Save ---
    dst_profile.update(dtype='float32', nodata=-9999, count=1)
    # Replace any remaining NaNs (if any) with nodata
    out_data = np.where(np.isnan(out_data), -9999, out_data)
    
    with rasterio.open(output_path, 'w', **dst_profile) as dst:
        dst.write(out_data, 1)
        print(f"Saved manual alignment to: {output_path}")

# Run It
# align_lst_manual("LST.tif", "WorldPop.tif", "LST_Manual.tif")
# align_lst_manual("lst.tif", "world_pop.tif", output_path="aligned_lst.tif")
