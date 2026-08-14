class_name Coin
extends Area2D

signal collected

var _time := randf() * TAU
var _base_y := 0.0


func _ready() -> void:
	add_to_group("coins")
	_base_y = position.y
	body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	_time += delta
	position.y = _base_y + sin(_time * 3.4) * 7.0
	$Visual.rotation += delta * 2.4


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	collected.emit()
	queue_free()
