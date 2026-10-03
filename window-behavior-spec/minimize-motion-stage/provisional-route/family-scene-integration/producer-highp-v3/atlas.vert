precision highp float;attribute highp vec2 position;attribute highp vec2 uv;varying highp vec2 tex;void main(){tex=uv;gl_Position=vec4(position,0.,1.);}
