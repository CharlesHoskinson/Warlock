precision highp float;uniform highp sampler2D atlas;varying highp vec2 tex;void main(){gl_FragColor=texture2D(atlas,tex);}
