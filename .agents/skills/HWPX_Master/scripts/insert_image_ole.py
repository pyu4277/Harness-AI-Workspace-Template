import win32com.client as win32
import os
import sys
from PIL import Image

def main():
    img_path = r"d:\OneDrive - 순천대학교\003_AI_Project\Projects\260308_HWPX_Master_Test\다운로드.jpg"
    out_path = r"d:\OneDrive - 순천대학교\003_AI_Project\Projects\260308_HWPX_Master_Test\TrackC_Image_Test.hwpx"
    
    if not os.path.exists(img_path):
        print(f"Image not found: {img_path}")
        return

    # Image size calculation
    with Image.open(img_path) as img:
        w_px, h_px = img.size
        # Get DPI
        dpi_x, dpi_y = img.info.get("dpi", (96, 96))
        
    print(f"Image Size (px): {w_px} x {h_px}, DPI: {dpi_x} x {dpi_y}")
    
    # Calculate HWP units (1 mm = 283.465 HWPU)
    # width/height in mm
    w_mm = (w_px / dpi_x) * 25.4
    h_mm = (h_px / dpi_y) * 25.4
    
    w_hwpu = int(w_mm * 283.465)
    h_hwpu = int(h_mm * 283.465)
    
    # Table size (1.5x)
    tbl_w = int(w_hwpu * 1.5)
    tbl_h = int(h_hwpu * 1.5)
    
    print(f"Image HWPU: {w_hwpu} x {h_hwpu}")
    print(f"Table HWPU: {tbl_w} x {tbl_h}")

    # Launch HWP
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FileCheck") # Bypass security warning
    
    hwp.XHwpWindows.Item(0).Visible = True
    hwp.Clear(1) # Empty Document

    # Create new page (in empty doc, we already have one, but just to make sure we have a "new page" as requested)
    hwp.HAction.Run("BreakPage")

    # Insert Table
    act = hwp.CreateAction("TableCreate")
    pset = act.CreateSet()
    act.GetDefault(pset)
    pset.SetItem("Rows", 1)
    pset.SetItem("Cols", 1)
    pset.SetItem("WidthType", 2)  # Exact numeric value
    pset.SetItem("HeightType", 1) # Exact numeric value
    pset.SetItem("WidthValue", tbl_w)
    pset.SetItem("HeightValue", tbl_h)
    pset.SetItem("TreatAsChar", 1)
    act.Execute(pset)
    
    # Table border thickness 0.4
    # Select inside the table cell
    hwp.HAction.Run("TableCellBlock") # F5 selection
    
    act_border = hwp.CreateAction("CellBorder")
    pset_border = act_border.CreateSet()
    act_border.GetDefault(pset_border)
    pset_border.SetItem("BorderTypeAll", 1) # Solid
    pset_border.SetItem("BorderWidthAll", 6) # 0.4mm
    act_border.Execute(pset_border)
    
    # Deselect and move cursor inside cell to insert image
    hwp.HAction.Run("Cancel")
    
    # Insert Image
    # Using InsertPicture with sizeoption=3 (Treat as Char)
    # Usage: InsertPicture(Path, Embedded, sizeoption, Reverse, watermark, effect, width, height)
    ctrl = hwp.InsertPicture(img_path, True, 3, False, False, 0)
    
    if ctrl is not None:
        print("Image inserted successfully via InsertPicture")
    else:
        print("Failed to insert image, trying Action...")
        act_pic = hwp.CreateAction("InsertPicture")
        pset_pic = act_pic.CreateSet()
        act_pic.GetDefault(pset_pic)
        pset_pic.SetItem("FileName", img_path)
        pset_pic.SetItem("TreatAsChar", 1)
        pset_pic.SetItem("SizeOption", 0)
        act_pic.Execute(pset_pic)
        
    print(f"Saving to: {out_path}")
    hwp.SaveAs(out_path, "HWPX")
    hwp.Quit()

if __name__ == "__main__":
    main()
