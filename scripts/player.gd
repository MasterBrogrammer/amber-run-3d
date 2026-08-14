class_name Player
extends CharacterBody2D

const SPEED := 280.0
const JUMP_VELOCITY := -620.0
const COYOTE_TIME := 0.12
const JUMP_BUFFER := 0.12

var _coyote := 0.0
var _jump_buffer := 0.0
var _spawn_position := Vector2.ZERO

@onready var _visual: Node2D = $Visual
@onready var _sprite: AnimatedSprite2D = $Visual/Sprite
@onready var _shadow: Sprite2D = $ContactShadow
@onready var _sfx_jump: AudioStreamPlayer = $SfxJump


func _ready() -> void:
	add_to_group("player")
	_spawn_position = global_position
	_sprite.play("idle")


func _physics_process(delta: float) -> void:
	if is_on_floor():
		_coyote = COYOTE_TIME
	else:
		velocity += get_gravity() * delta
		_coyote = maxf(_coyote - delta, 0.0)

	var direction := Input.get_axis("ui_left", "ui_right")
	if direction != 0.0:
		velocity.x = direction * SPEED
		_visual.scale.x = signf(direction)
	else:
		velocity.x = move_toward(velocity.x, 0.0, SPEED)

	if Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("ui_up"):
		_jump_buffer = JUMP_BUFFER
	else:
		_jump_buffer = maxf(_jump_buffer - delta, 0.0)

	if _jump_buffer > 0.0 and _coyote > 0.0:
		velocity.y = JUMP_VELOCITY
		_coyote = 0.0
		_jump_buffer = 0.0
		_sfx_jump.play()

	move_and_slide()
	_update_animation()
	_update_shadow()


func _update_animation() -> void:
	var next := "idle"
	if not is_on_floor():
		next = "jump"
	elif absf(velocity.x) > 12.0:
		next = "run"
	if _sprite.animation != next:
		_sprite.play(next)


func _update_shadow() -> void:
	if is_on_floor():
		_shadow.scale = Vector2(0.55, 0.45)
		_shadow.modulate.a = 0.75
	else:
		_shadow.scale = Vector2(0.34, 0.26)
		_shadow.modulate.a = 0.32


func respawn() -> void:
	global_position = _spawn_position
	velocity = Vector2.ZERO
	_sprite.play("idle")
