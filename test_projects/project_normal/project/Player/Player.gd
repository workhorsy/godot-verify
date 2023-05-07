extends Spatial
class_name PlayerZZ


func _ready() -> void:
	pass

func _physics_process(delta : float) -> void:
	var rot = self.rotation
	rot.z += deg2rad(3.0)
	self.rotation = rot
