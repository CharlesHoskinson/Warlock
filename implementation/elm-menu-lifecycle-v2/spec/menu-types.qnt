// Reexport the explicitly approved sketch without changing its type/state body.
module menu_types {
  import menu_sketch.* from "./menu-sketch"
  export menu_sketch.*
}
