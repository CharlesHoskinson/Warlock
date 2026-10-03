"""Strict environment authority for the private Qt fixture; no native actions."""
from pathlib import Path
import os,stat

def assert_private_environment(main,private):
 for key in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY'):
  assert main.get(key) and private.get(key) and main[key]!=private[key],key+' must identify distinct private target'
 runtime=Path(private['XDG_RUNTIME_DIR']);assert runtime.is_absolute()
 assert runtime.resolve()!=Path(main['XDG_RUNTIME_DIR']).resolve()
 for key in ('HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_STATE_HOME'):
  path=Path(private[key]);assert path.is_absolute() and path.resolve().is_relative_to(runtime.resolve()),key+' must be private'
 for key in ('DISPLAY','WAYLAND_SOCKET','AT_SPI_BUS_ADDRESS','SESSION_MANAGER'):
  assert not private.get(key),key+' must not inherit main handle'
 assert not main.get('DBUS_SESSION_BUS_ADDRESS') or private.get('DBUS_SESSION_BUS_ADDRESS')!=main['DBUS_SESSION_BUS_ADDRESS'],'private bus cannot inherit main bus'
 display=Path(private['WAYLAND_DISPLAY'])
 path=display if display.is_absolute() else runtime/display
 assert path.resolve().is_relative_to(runtime.resolve()),'private Wayland socket must be inside private runtime'
 return path

def verify_socket(main,private):
 path=assert_private_environment(main,private);st=path.stat()
 assert stat.S_ISSOCK(st.st_mode) and st.st_uid==os.getuid(),'private socket must be owned user socket'
 display=Path(main['WAYLAND_DISPLAY']);original=display if display.is_absolute() else Path(main['XDG_RUNTIME_DIR'])/display
 original_st=original.stat();assert (st.st_dev,st.st_ino)!=(original_st.st_dev,original_st.st_ino)
 return {'privateSocket':str(path),'privateSocketIdentity':[st.st_dev,st.st_ino],'distinctFromMainSocket':True}
