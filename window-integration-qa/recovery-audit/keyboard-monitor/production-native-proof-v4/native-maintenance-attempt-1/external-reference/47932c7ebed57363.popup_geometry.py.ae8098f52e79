"""Validate real toolkit observations before selecting a native popup target."""
import math

def ready_popup(row):
 try:
  button=row['button'];popover=row['popoverAllocation'];allocated=row['buttonAllocation']
  values=[*row['position'],*row['surfaceTransform'],button['x'],button['y'],button['width'],button['height'],*popover,*allocated]
  return (row['nativeMapped'] is True and row['centerPickedButton']=='Actual popup target A'
          and all(math.isfinite(v) for v in values)
          and all(v>0 for v in [button['width'],button['height'],*popover,*allocated]))
 except (KeyError,TypeError,ValueError):return False

def popup_target(window,row):
 if not ready_popup(row):raise ValueError('actual popup allocation/hit is not ready')
 box=row['button'];position=row['position'];transform=row['surfaceTransform']
 return (window['at'][0]+position[0]+box['x']+box['width']/2-transform[0],
         window['at'][1]+position[1]+box['y']+box['height']/2-transform[1])
