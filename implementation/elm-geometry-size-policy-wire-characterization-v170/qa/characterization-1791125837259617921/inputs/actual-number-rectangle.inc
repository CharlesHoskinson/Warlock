std::string geometryNumber(double value) {
    if(!std::isfinite(value)) throw std::runtime_error("Nonfinite geometry");
    char buffer[64];const auto result=std::to_chars(buffer,buffer+sizeof(buffer),value,std::chars_format::general,std::numeric_limits<double>::max_digits10);
    if(result.ec!=std::errc{}) throw std::runtime_error("Geometry number bound");
    return std::string(buffer,result.ptr);
}

std::string geometryRect(const CBox& box) {
    if(box.w<=0 || box.h<=0 || !std::isfinite(box.x+box.w) || !std::isfinite(box.y+box.h)) throw std::runtime_error("Invalid geometry rectangle");
    return "["+geometryNumber(box.x)+","+geometryNumber(box.y)+","+geometryNumber(box.w)+","+geometryNumber(box.h)+"]";
}
