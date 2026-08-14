extends Node2D

@onready var _score_label: Label = $HUD/Margin/VBox/ScoreLabel
@onready var _win_panel: Control = $HUD/WinPanel
@onready var _result_label: Label = $HUD/WinPanel/VBox/WinLabel
@onready var _reset_button: Button = $HUD/WinPanel/VBox/ResetButton
@onready var _player: Player = $World/Player
@onready var _flag: Area2D = $World/PlatD/Flag
@onready var _sfx_coin: AudioStreamPlayer = $SfxCoin
@onready var _sfx_fall: AudioStreamPlayer = $SfxFall
@onready var _sfx_win: AudioStreamPlayer = $SfxWin
@onready var _music: AudioStreamPlayer = $Music

var _total := 0
var _got := 0
var _flag_reached := false


func _ready() -> void:
	_win_panel.visible = false
	_reset_button.pressed.connect(_on_reset_pressed)
	_flag.body_entered.connect(_on_flag_reached)
	var coins := get_tree().get_nodes_in_group("coins")
	_total = coins.size()
	for coin in coins:
		coin.collected.connect(_on_coin_collected)
	_update_score()
	call_deferred("_start_music")


func _start_music() -> void:
	if _music.stream is AudioStreamWAV:
		var wav := _music.stream as AudioStreamWAV
		wav.loop_begin = 0
		wav.loop_end = int(wav.get_length() * wav.mix_rate)
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	if not _music.playing:
		_music.play()


func _physics_process(_delta: float) -> void:
	if _player.global_position.y > 820.0:
		_sfx_fall.play()
		_player.respawn()


func _on_coin_collected() -> void:
	_got += 1
	_update_score()
	_sfx_coin.play()


func _on_flag_reached(body: Node2D) -> void:
	if _flag_reached or not body.is_in_group("player"):
		return
	_flag_reached = true
	if _got >= _total:
		_result_label.text = "You got them all.\nThat's the demo."
		_sfx_win.play()
	else:
		var noun := "coin" if _got == 1 else "coins"
		_result_label.text = "You reached the flag\nwith %d of %d %s." % [_got, _total, noun]
	_win_panel.visible = true


func _update_score() -> void:
	_score_label.text = "Coins   %d / %d" % [_got, _total]


func _on_reset_pressed() -> void:
	get_tree().reload_current_scene()
