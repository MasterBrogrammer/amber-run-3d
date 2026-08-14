shader_type canvas_item;

uniform float speed : hint_range(0.5, 8.0) = 2.6;
uniform float strength : hint_range(0.0, 0.08) = 0.028;
uniform float pole_cut : hint_range(0.0, 0.6) = 0.30;

void fragment() {
	vec2 uv = UV;
	float cloth = smoothstep(pole_cut, pole_cut + 0.10, uv.x);
	float along = (uv.x - pole_cut);
	float wave = sin(uv.y * 16.0 - TIME * speed + uv.x * 7.0) * strength;
	wave += sin(uv.y * 7.0 + TIME * speed * 1.35) * strength * 0.45;
	uv.x += wave * cloth * along * 3.2;
	uv.y += wave * cloth * 0.35;
	if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
		COLOR = vec4(0.0);
	} else {
		COLOR = texture(TEXTURE, uv);
	}
}
