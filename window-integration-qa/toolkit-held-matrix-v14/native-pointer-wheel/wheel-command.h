/* One exact wheel detent; original commands are handled by the unchanged loop. */
static int pointer_qa_wheel(const char *line,struct zwlr_virtual_pointer_v1 *pointer) {
    if(strncmp(line,"wheel ",6))return 0;
    int direction;if(!strcmp(line,"wheel 1\n"))direction=1;else if(!strcmp(line,"wheel -1\n"))direction=-1;else return -1;
    zwlr_virtual_pointer_v1_axis_discrete(pointer,now(),WL_POINTER_AXIS_VERTICAL_SCROLL,wl_fixed_from_double(15.0*direction),direction);
    zwlr_virtual_pointer_v1_axis_source(pointer,WL_POINTER_AXIS_SOURCE_WHEEL);
    zwlr_virtual_pointer_v1_frame(pointer);
    return 1;
}
